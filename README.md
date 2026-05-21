
# GeoScraper

GeoScraper is a Python OSINT/web-scraping utility that:

- Searches DuckDuckGo
- Scrapes webpage text
- Uses Stanza NER to identify geolocations
- Geocodes locations into coordinates
- Exports findings to CSV
- Generates an interactive map

## Features

### Search
- Up to 10 user-defined queries
- Up to 50 DuckDuckGo results per query

### Scraping
- User-Agent spoofing
- HTML cleaning
- Text extraction

### NLP / NER
- Stanza Named Entity Recognition
- Extracts geopolitical entities (GPE)

### Geocoding
- OpenStreetMap Nominatim integration
- Latitude and longitude extraction

### Visualization
- Interactive HTML map
- Clickable markers with source links

### Performance Improvements
- Multithreaded URL processing
- Deduplicated locations
- Logging and exception handling

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
python main.py
```

---

## Output Files

| File | Description |
|---|---|
| results.csv | Structured geolocation results |
| map.html | Interactive map visualization |

---

## Recommended Future Enhancements

- Proxy rotation
- Async scraping with aiohttp
- Redis caching
- Selenium/Playwright support
- GeoJSON export
- Graph/network visualization
- Entity relationship extraction
- PostgreSQL/PostGIS backend
- FastAPI web interface
- Docker deployment

