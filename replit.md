# SafeZone - Community Safety Checker

## Overview

SafeZone is a web application that allows users to search for registered offenders by ZIP code. It queries official public registries through a pluggable provider layer, displays results on an interactive map, and pairs them with safety resources. Where no verified data source exists for an area, it says so and links to the official registry rather than showing an estimate.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask for server-side rendering
- **UI Framework**: Bootstrap 5 for responsive design and components
- **Styling**: Custom CSS with CSS variables for consistent theming and modern gradients
- **JavaScript**: Vanilla JavaScript with class-based architecture for client-side functionality
- **Mapping**: Leaflet.js integration for displaying offender locations on interactive maps
- **Icons**: Font Awesome for consistent iconography

### Backend Architecture
- **Framework**: Flask (Python) following a simple MVC pattern
- **Routing**: RESTful API design with separate routes for page rendering and data endpoints
- **Data Layer**: Provider package (`safezone/providers/`) with one class per data source, selected per-jurisdiction at request time
- **Validation**: Server-side ZIP code validation with proper error handling
- **Response Format**: JSON API responses with consistent success/error structure

### Application Structure
- **Entry Point**: `main.py` serves as the application entry point
- **Core Application**: `app.py` contains all Flask routes and business logic
- **Data Sources**: `safezone/providers/` - Open Data DC (free), an optional keyed national aggregator, and an honest no-coverage fallback
- **Templates**: HTML templates in `templates/` directory for page rendering
- **Static Assets**: CSS and JavaScript files organized in `static/` directory

### Security Considerations
- Session secret is required from the environment; the app refuses to start without it
- Debug mode is opt-in via `FLASK_DEBUG` and off by default
- ZIP input is validated as exactly 5 digits before any provider is called
- Registry data is rendered via `textContent`/`createElement`, never `innerHTML`,
  so third-party record text cannot inject markup
- Per-IP rate limiting on `/search`
- `X-Content-Type-Options`, `X-Frame-Options` and `Referrer-Policy` set on all responses

Note: there is no CSRF protection, and none is needed today - `/search` is an
unauthenticated read-only endpoint with no session state or side effects. Add
Flask-WTF if user accounts are ever introduced. (Flask has no built-in CSRF
protection; an earlier version of this document claimed otherwise.)

## External Dependencies

### Frontend Libraries
- **Bootstrap 5**: UI component framework and responsive grid system
- **Leaflet.js**: Open-source mapping library for displaying interactive maps
- **Font Awesome**: Icon library for consistent UI elements

### Backend Dependencies
- **Flask**: Python web framework for HTTP handling and templating
- **Python Standard Library**: Logging, OS environment variable handling

### Data Sources
- **Open Data DC**: free ArcGIS feature layer, no API key, covers Washington DC
- **National aggregator**: optional, paid, enabled by setting `SAFEZONE_NATIONAL_API_URL` and `SAFEZONE_NATIONAL_API_KEY`
- **No national free API exists.** NSOPW is a federated search portal without a
  public programmatic interface. Uncovered areas are handed off to the official
  NSOPW search. See `DEPLOYING.md` for adding sources.

### Future Integration Points
- **Additional state providers**: several states publish open data (Iowa JSON feed, Texas bulk download); each needs its own provider class
- **Caching**: provider responses could be cached, subject to each source's terms - some prohibit it

### Development Tools
- **Logging**: Built-in Python logging for debugging and monitoring
- **Environment Configuration**: Support for environment-based configuration management