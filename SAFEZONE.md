# SafeZone - Community Safety Checker

> **Note (updated):** SafeZone now reads from official public registries via a
> provider layer (`safezone/providers/`). The `mock_data.py` module described
> in sections below has been removed - it generated randomised offender records
> for real ZIP codes, which could falsely associate real addresses with sex
> offences. Sections referring to it describe the previous version.
> See `DEPLOYING.md` for the current data-source setup.


## What is SafeZone?

SafeZone is a web application that allows teenagers and families to check for registered sexual offenders in their neighborhood by entering a ZIP code. It displays results on an interactive map with safety tips and educational resources. The app is designed to be easy to use, visually appealing, and informative.

---

## Features

- ZIP code search to find registered offenders in an area
- Interactive map showing approximate offender locations
- Search history saved in the browser (no account needed)
- Safety tips for everyday situations
- FAQ section with helpful resources
- Clean, teen-friendly design with bright colors

---

## Tech Stack

| Layer | Technology |
|---|---|
| Programming Language | Python |
| Web Framework | Flask |
| Web Server | Gunicorn |
| Frontend | HTML, CSS, JavaScript |
| UI Framework | Bootstrap 5 |
| Maps | Leaflet.js |
| Icons | Font Awesome |
| Browser Storage | localStorage |
| Template Engine | Jinja2 |

---

## Project Structure

```
safezone/
├── main.py              # App entry point
├── app.py               # Flask routes and logic
├── mock_data.py         # Sample offender data
├── templates/
│   └── index.html       # Main HTML page
├── static/
│   ├── css/
│   │   └── style.css    # Custom styling
│   └── js/
│       └── app.js       # Frontend JavaScript
```

---

## File Breakdown

### `main.py` - Entry Point
Starts the Flask application.

```python
from app import app
```

---

### `app.py` - Backend Logic
Handles all routes and processes search requests.

**Routes:**
- `GET /` - Loads the main homepage
- `POST /search` - Accepts a ZIP code and returns offender data

**How the search works:**
1. User submits a ZIP code
2. Flask validates it is a 5-digit number
3. The app looks up the ZIP code in the mock data
4. Returns a JSON response with the offender count and details

```python
@app.route('/search', methods=['POST'])
def search_zip():
    data = request.get_json()
    zip_code = data.get('zip_code', '').strip()

    # Validate ZIP code
    if not zip_code.isdigit() or len(zip_code) != 5:
        return jsonify({'success': False, 'error': 'Please enter a valid 5-digit ZIP code'}), 400

    # Look up mock data
    offender_data = get_offender_data_by_zip(zip_code)

    return jsonify({
        'success': True,
        'zip_code': zip_code,
        'offender_count': offender_data['count'],
        'has_offenders': offender_data['count'] > 0,
        'offenders': offender_data['offenders']
    })
```

---

### `mock_data.py` - Sample Data
Provides realistic sample data for demonstration purposes. Built to be easily replaced with a real API.

**How it works:**
- Pre-loaded ZIP codes (90210, 10001, 77001) return specific offender data
- Known safe ZIP codes (12345, 54321, etc.) return zero offenders
- All other ZIP codes randomly generate results (30% chance of offenders)

```python
def get_offender_data_by_zip(zip_code):
    if zip_code in MOCK_OFFENDERS:
        return MOCK_OFFENDERS[zip_code]

    if zip_code in SAFE_ZIP_CODES:
        return {'count': 0, 'offenders': []}

    # 30% chance of generating random offenders
    if random.random() < 0.3:
        ...
```

**Each offender record contains:**
- ID, name, age
- Address and offense type
- Conviction date
- Latitude and longitude (for map display)

---

### `templates/index.html` - Frontend Page
The main HTML page built with Jinja2 and Bootstrap 5. Contains:
- Navigation bar
- ZIP code search form
- Results display area
- Interactive Leaflet.js map
- Safety tips section
- FAQ section

---

### `static/css/style.css` - Styling
Custom CSS that defines the teen-friendly color scheme and animations.

**Color Palette:**
```css
:root {
    --primary-color: #ff6b6b;     /* Coral pink */
    --secondary-color: #4ecdc4;   /* Turquoise */
    --accent-color: #45b7d1;      /* Blue */
    --pink-color: #fd79a8;        /* Bright pink */
    --purple-color: #a29bfe;      /* Soft purple */
}
```

---

### `static/js/app.js` - Frontend Interactivity
Handles all client-side functionality using a JavaScript class called `SafeZoneApp`.

**Key functions:**
- `handleSearch()` - Sends ZIP code to backend and displays results
- `displayResults()` - Shows safe/alert message based on response
- `initializeMap()` - Renders Leaflet.js map with offender markers
- `addToSearchHistory()` - Saves searches to localStorage
- `loadSearchHistory()` - Restores past searches on page load

---

## How to Run

The app runs on port 5000 using Gunicorn:

```bash
gunicorn --bind 0.0.0.0:5000 --reload main:app
```

---

## Future Improvements (Version 2.0)

- Connect to a real offender registry API (NSOPW)
- Add user accounts with saved locations
- Build a native mobile app
- Add email/SMS alerts for watched areas
- Implement a heat map for visual safety patterns

---

## Disclaimer

SafeZone currently uses demonstration data only. It is intended for educational purposes and community safety awareness. Always verify information through official government sources.
