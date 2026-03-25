# Sentinel Curator -- UI Guide

**Version:** 0.1.0
**Date:** 2026-03-25
**Note:** Phase 0 has no graphical user interface. The system is accessed via REST API.
         This document describes the planned UI approach and the current developer UI.

---

## 1. Current Interface (Phase 0)

The system currently exposes a REST API only. Users interact via:

- curl or HTTP clients (see API_GUIDE.md for examples)
- The built-in Swagger UI at http://127.0.0.1:8000/docs (development mode only)
- The ReDoc interface at http://127.0.0.1:8000/redoc (development mode only)

---

## 2. Swagger UI (Development Only)

When SC_APP_ENV=development, FastAPI automatically serves an interactive
API explorer at /docs.

To submit a query via Swagger UI:

1. Open http://127.0.0.1:8000/docs in a browser.
2. Click POST /query to expand the endpoint.
3. Click Try it out.
4. Add the X-Curator-Role header value in the header field.
5. Enter your question in the request body JSON.
6. Click Execute.
7. The response body will show the SQL generated, the results, and your clearance tier.

The Swagger UI must be disabled in production:
```python
# In api/main.py -- set docs_url=None for production
app = FastAPI(docs_url=None, redoc_url=None)
```

Or control via SC_APP_ENV=production in the environment.

---

## 3. Planned UI (Phase 4)

A lightweight web frontend is planned for Phase 4, providing:

- A natural-language query input field
- Clearance-tier indicator showing the user's current role
- Results table with sortable columns
- Map view for geolocation results (using Leaflet.js with PostGIS coordinates)
- Query history panel

Recommended technology stack for the planned UI:

| Component | Technology |
|---|---|
| Frontend framework | HTMX + Alpine.js (consistent with JANUS Platform pattern) |
| Template engine | Jinja2 via FastAPI |
| Map rendering | Leaflet.js (open source, no external API dependency) |
| Styling | Tailwind CSS |

The UI will be served directly by the FastAPI application to avoid
introducing a separate frontend container.

---

## 4. Map Coordinate Format

Geolocation results are returned as PostGIS GEOGRAPHY(POINT) values.

Format: POINT(longitude latitude)

Example: POINT(-118.2437 33.9416)

When building the future map UI, pass these to Leaflet as:
- latitude: 33.9416
- longitude: -118.2437

Note: PostGIS uses (longitude, latitude) ordering (x, y) which is
the reverse of Leaflet's (latitude, longitude) ordering. Swap accordingly.

---

## 5. Accessibility and Classification Markings

When the UI is built, all pages must display the classification tier
of the data being shown (UNCLASSIFIED, RESTRICTED, or CONFIDENTIAL)
as a clearly visible banner at the top and bottom of every screen,
consistent with UK Government information handling standards.
