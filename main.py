import csv
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import folium
import requests
import stanza
from bs4 import BeautifulSoup
from ddgs import DDGS
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim

MAX_QUERIES = 10
MAX_RESULTS_PER_QUERY = 50
REQUEST_TIMEOUT = 10
THREADS = 5

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)

HEADERS = {"User-Agent": USER_AGENT}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

geolocator = Nominatim(user_agent="geo_scraper")


def search_duckduckgo(query, max_results=50):
    with DDGS(headers=HEADERS) as ddgs:
        results = ddgs.text(query, max_results=max_results)
        return [r.get("href") for r in results if r.get("href")]


def fetch_page_text(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.extract()

        text = soup.get_text(separator=" ", strip=True)

        return text[:10000]

    except Exception as exc:
        logging.warning(f"Failed to fetch {url}: {exc}")
        return ""


def extract_locations(text, nlp):
    if not text:
        return []

    try:
        doc = nlp(text)

        locations = []

        for ent in doc.entities:
            if ent.type == "GPE":
                cleaned = ent.text.strip()

                if cleaned not in locations:
                    locations.append(cleaned)

        return locations

    except Exception as exc:
        logging.warning(f"NER failed: {exc}")
        return []


def geocode_location(location):
    try:
        geo = geolocator.geocode(location, timeout=10)

        if geo:
            return geo.latitude, geo.longitude

    except GeocoderTimedOut:
        logging.warning(f"Timeout geocoding: {location}")

    except Exception as exc:
        logging.warning(f"Geocoding failed for {location}: {exc}")

    return None, None


def process_url(query, url, nlp):
    text = fetch_page_text(url)

    if not text:
        return []

    snippet = text[:300]
    locations = extract_locations(text, nlp)

    results = []

    for location in locations:
        lat, lon = geocode_location(location)

        results.append({
            "query": query,
            "url": url,
            "snippet": snippet,
            "location": location,
            "latitude": lat,
            "longitude": lon
        })

    return results


def save_results(results, filename="results.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow([
            "Query",
            "URL",
            "Snippet",
            "Geolocation",
            "Latitude",
            "Longitude"
        ])

        for item in results:
            writer.writerow([
                item["query"],
                item["url"],
                item["snippet"],
                item["location"],
                item["latitude"],
                item["longitude"]
            ])


def generate_map(results, output_file="map.html"):
    world_map = folium.Map(location=[20, 0], zoom_start=2)

    for item in results:
        lat = item["latitude"]
        lon = item["longitude"]

        if lat is None or lon is None:
            continue

        popup_html = f"""
        <b>Query:</b> {item['query']}<br>
        <b>Location:</b> {item['location']}<br>
        <b>URL:</b> <a href='{item['url']}' target='_blank'>Source</a>
        """

        folium.Marker(
            location=[lat, lon],
            popup=popup_html,
            tooltip=item["location"]
        ).add_to(world_map)

    world_map.save(output_file)


def main():
    stanza.download("en")

    nlp = stanza.Pipeline(
        lang="en",
        processors="tokenize,ner",
        use_gpu=False
    )

    queries = []

    print("\nEnter up to 10 search queries.\n")

    for i in range(MAX_QUERIES):
        query = input(f"Query {i+1}: ").strip()

        if not query:
            break

        queries.append(query)

    all_results = []

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = []

        for query in queries:
            urls = search_duckduckgo(query, max_results=MAX_RESULTS_PER_QUERY)

            for url in urls:
                futures.append(
                    executor.submit(process_url, query, url, nlp)
                )

                time.sleep(0.2)

        for future in as_completed(futures):
            try:
                result = future.result()

                if result:
                    all_results.extend(result)

            except Exception as exc:
                logging.warning(f"Thread error: {exc}")

    save_results(all_results)
    generate_map(all_results)

    print("\nCompleted successfully.")
    print("Generated:")
    print("- results.csv")
    print("- map.html")


if __name__ == "__main__":
    main()
