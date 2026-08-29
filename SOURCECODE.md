# SafeZone - Complete Source Code

> **Note (updated):** SafeZone now reads from official public registries via a
> provider layer (`safezone/providers/`). The `mock_data.py` module described
> in sections below has been removed - it generated randomised offender records
> for real ZIP codes, which could falsely associate real addresses with sex
> offences. Sections referring to it describe the previous version.
> See `DEPLOYING.md` for the current data-source setup.


## File Structure

```
safezone/
├── main.py
├── app.py
├── mock_data.py
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
```

---

## main.py

```python
from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

---

## app.py

```python
import os
import logging
from flask import Flask, render_template, request, jsonify
from mock_data import get_offender_data_by_zip

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_zip():
    """Search for offenders by ZIP code"""
    try:
        data = request.get_json()
        zip_code = data.get('zip_code', '').strip()

        if not zip_code:
            return jsonify({'success': False, 'error': 'ZIP code is required'}), 400

        if not zip_code.isdigit() or len(zip_code) != 5:
            return jsonify({'success': False, 'error': 'Please enter a valid 5-digit ZIP code'}), 400

        offender_data = get_offender_data_by_zip(zip_code)

        response = {
            'success': True,
            'zip_code': zip_code,
            'offender_count': offender_data['count'],
            'has_offenders': offender_data['count'] > 0,
            'offenders': offender_data['offenders'],
            'message': f"Found {offender_data['count']} registered offender(s) in ZIP code {zip_code}"
                       if offender_data['count'] > 0
                       else f"No registered offenders found in ZIP code {zip_code}"
        }

        return jsonify(response)

    except Exception as e:
        logging.error(f"Error processing search request: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred. Please try again.'}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'success': False, 'error': 'Internal server error. Please try again later.'}), 500
```

---

## mock_data.py

```python
"""
Mock data for sexual offender registry lookups.
This module provides sample data that can be easily replaced with real API calls.
"""

import random

MOCK_OFFENDERS = {
    '90210': {
        'count': 2,
        'offenders': [
            {
                'id': 'SO001',
                'name': 'John D.',
                'age': 45,
                'address': '123 Main St',
                'offense_type': 'Sexual assault',
                'conviction_date': '2015-03-15',
                'lat': 34.0901,
                'lng': -118.4065
            },
            {
                'id': 'SO002',
                'name': 'Michael R.',
                'age': 38,
                'address': '456 Oak Ave',
                'offense_type': 'Child endangerment',
                'conviction_date': '2018-07-22',
                'lat': 34.0895,
                'lng': -118.4070
            }
        ]
    },
    '10001': {
        'count': 1,
        'offenders': [
            {
                'id': 'SO003',
                'name': 'Robert K.',
                'age': 52,
                'address': '789 Broadway',
                'offense_type': 'Sexual misconduct',
                'conviction_date': '2016-11-08',
                'lat': 40.7505,
                'lng': -73.9934
            }
        ]
    },
    '77001': {
        'count': 3,
        'offenders': [
            {
                'id': 'SO004',
                'name': 'David L.',
                'age': 41,
                'address': '321 Houston St',
                'offense_type': 'Sexual assault',
                'conviction_date': '2017-02-14',
                'lat': 29.7604,
                'lng': -95.3698
            },
            {
                'id': 'SO005',
                'name': 'James W.',
                'age': 35,
                'address': '654 Texas Ave',
                'offense_type': 'Indecent exposure',
                'conviction_date': '2019-05-30',
                'lat': 29.7589,
                'lng': -95.3677
            },
            {
                'id': 'SO006',
                'name': 'Mark T.',
                'age': 48,
                'address': '987 Main St',
                'offense_type': 'Sexual battery',
                'conviction_date': '2014-09-12',
                'lat': 29.7612,
                'lng': -95.3702
            }
        ]
    }
}

SAFE_ZIP_CODES = ['12345', '54321', '99999', '11111', '22222']

def get_offender_data_by_zip(zip_code):
    """
    Get offender data for a given ZIP code.
    In production, replace this with real API calls to NSOPW.
    """
    if zip_code in MOCK_OFFENDERS:
        return MOCK_OFFENDERS[zip_code]

    if zip_code in SAFE_ZIP_CODES:
        return {'count': 0, 'offenders': []}

    # 30% chance of random offenders for unknown ZIP codes
    if random.random() < 0.3:
        num_offenders = random.randint(1, 2)
        return {
            'count': num_offenders,
            'offenders': [
                {
                    'id': f'SO{random.randint(100, 999)}',
                    'name': f'[Name Redacted {i+1}]',
                    'age': random.randint(25, 65),
                    'address': '[Address Redacted]',
                    'offense_type': random.choice(['Sexual assault', 'Sexual misconduct', 'Child endangerment']),
                    'conviction_date': f'20{random.randint(10,23)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
                    'lat': 0,
                    'lng': 0
                } for i in range(num_offenders)
            ]
        }

    return {'count': 0, 'offenders': []}
```

---

## templates/index.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SafeZone - Community Safety Checker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>

    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light shadow-sm" style="background: rgba(255,255,255,0.95); backdrop-filter: blur(10px);">
        <div class="container">
            <a class="navbar-brand fw-bold" href="#" style="color: #ff6b6b; font-size: 1.5rem;">
                🛡️ SafeZone
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <div class="navbar-nav ms-auto">
                    <a class="nav-link fw-semibold" href="#faq" style="color: #4ecdc4;">❓ FAQ</a>
                    <a class="nav-link fw-semibold" href="#safety-tips" style="color: #74b9ff;">💡 Safety Tips</a>
                </div>
            </div>
        </div>
    </nav>

    <div class="container mt-4">

        <!-- Hero Section -->
        <div class="row justify-content-center mb-5">
            <div class="col-lg-8 text-center">
                <div class="hero-illustration mb-4">
                    <svg width="120" height="120" viewBox="0 0 120 120" fill="none">
                        <circle cx="60" cy="60" r="55" fill="url(#heroGradient)" opacity="0.1"/>
                        <circle cx="60" cy="60" r="45" fill="url(#heroGradient)" opacity="0.2"/>
                        <circle cx="60" cy="60" r="35" fill="url(#heroGradient)" opacity="0.3"/>
                        <path d="M60 25C45.088 25 33 37.088 33 52C33 70 60 95 60 95S87 70 87 52C87 37.088 74.912 25 60 25Z" fill="url(#heroGradient)"/>
                        <circle cx="60" cy="52" r="12" fill="white"/>
                        <path d="M55 52L58 55L65 48" stroke="#ff6b6b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <defs>
                            <linearGradient id="heroGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" style="stop-color:#ff6b6b"/>
                                <stop offset="100%" style="stop-color:#4ecdc4"/>
                            </linearGradient>
                        </defs>
                    </svg>
                </div>
                <h1 class="display-5 fw-bold text-white mb-3">🏡 Check Your Community</h1>
                <p class="lead text-white">
                    Stay informed about your neighborhood's safety. Enter your ZIP code to check for registered offenders in your area.
                </p>
                <div class="alert alert-info border-0 rounded-3 mt-4" role="alert">
                    <i class="fas fa-info-circle me-2"></i>
                    <strong>Educational Purpose:</strong> This app is for educational and safety awareness only.
                    Always verify through official sources and report concerns to local authorities.
                </div>
            </div>
        </div>

        <!-- Search Form -->
        <div class="row justify-content-center mb-5">
            <div class="col-lg-6">
                <div class="card border-0 shadow-lg rounded-4">
                    <div class="card-body p-4">
                        <form id="searchForm" class="needs-validation" novalidate>
                            <div class="mb-3">
                                <label for="zipCode" class="form-label fw-semibold">📍 Enter Your ZIP Code</label>
                                <div class="input-group input-group-lg">
                                    <span class="input-group-text" style="background: linear-gradient(135deg,#ff6b6b,#4ecdc4); border:none; color:white; border-radius:1.5rem 0 0 1.5rem;">🏠</span>
                                    <input type="text" class="form-control form-control-lg" id="zipCode"
                                        placeholder="e.g., 90210, 77001, 10001" maxlength="5" pattern="[0-9]{5}" required
                                        style="border-radius: 0 1.5rem 1.5rem 0; border-left: none;">
                                </div>
                                <small class="form-text text-muted mt-1">💡 Try: 90210, 77001, 10001, or 12345</small>
                            </div>
                            <button type="submit" class="btn btn-primary btn-lg w-100">
                                <span id="searchBtnText">🔍 Check My Area</span>
                                <div class="spinner-border spinner-border-sm ms-2 d-none" id="loadingSpinner" role="status"></div>
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <!-- Search Results -->
        <div id="searchResults" class="row justify-content-center mb-5 d-none">
            <div class="col-lg-8">
                <div id="resultsCard" class="card border-0 shadow rounded-4">
                    <div class="card-body p-4">
                        <div id="resultsContent"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Map Container -->
        <div id="mapContainer" class="row justify-content-center mb-5 d-none">
            <div class="col-lg-10">
                <div class="card border-0 shadow rounded-4">
                    <div class="card-header bg-transparent border-0 p-4">
                        <h5 class="card-title mb-0"><i class="fas fa-map me-2"></i>Area Map</h5>
                    </div>
                    <div class="card-body p-0">
                        <div id="map" style="height: 400px; border-radius: 0 0 1rem 1rem;"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Search History -->
        <div id="searchHistory" class="row justify-content-center mb-5 d-none">
            <div class="col-lg-8">
                <div class="card border-0 shadow rounded-4">
                    <div class="card-header bg-transparent border-0 p-4">
                        <h5 class="card-title mb-0"><i class="fas fa-history me-2"></i>Recent Searches</h5>
                    </div>
                    <div class="card-body pt-0">
                        <div id="historyList"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- FAQ Section -->
        <div id="faq" class="row justify-content-center mb-5">
            <div class="col-lg-10">
                <h2 class="text-center mb-4 fw-bold text-white">❓ Got Questions? We've Got Answers!</h2>
                <div class="accordion accordion-flush" id="faqAccordion">
                    <div class="accordion-item border rounded-3 mb-3">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed fw-semibold" type="button" data-bs-toggle="collapse" data-bs-target="#faq1">
                                What is this app for?
                            </button>
                        </h2>
                        <div id="faq1" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                This app helps you check for registered sexual offenders in your ZIP code area for educational and safety awareness purposes.
                            </div>
                        </div>
                    </div>
                    <div class="accordion-item border rounded-3 mb-3">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed fw-semibold" type="button" data-bs-toggle="collapse" data-bs-target="#faq2">
                                Is this information accurate?
                            </button>
                        </h2>
                        <div id="faq2" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                Currently this app uses sample data for demonstration. Always verify through the official National Sex Offender Public Website at nsopw.gov.
                            </div>
                        </div>
                    </div>
                    <div class="accordion-item border rounded-3 mb-3">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed fw-semibold" type="button" data-bs-toggle="collapse" data-bs-target="#faq3">
                                What should I do if I find concerning information?
                            </button>
                        </h2>
                        <div id="faq3" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                For immediate safety concerns contact local law enforcement. Visit <a href="https://www.nsopw.gov" target="_blank">www.nsopw.gov</a> for official information.
                            </div>
                        </div>
                    </div>
                    <div class="accordion-item border rounded-3 mb-3">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed fw-semibold" type="button" data-bs-toggle="collapse" data-bs-target="#faq4">
                                How can I stay safe?
                            </button>
                        </h2>
                        <div id="faq4" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                See our safety tips below, trust your instincts, and don't hesitate to reach out to trusted adults or authorities if you feel unsafe.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Safety Tips Section -->
        <div id="safety-tips" class="row justify-content-center mb-5">
            <div class="col-lg-10">
                <h2 class="text-center mb-4 fw-bold text-white">💡 Stay Safe Out There!</h2>
                <div class="row g-4">
                    <div class="col-md-6 col-lg-4">
                        <div class="card h-100 border-0 shadow rounded-4 safety-tip-card" style="background: linear-gradient(135deg,#ff6b6b,#4ecdc4);">
                            <div class="card-body text-center p-4">
                                <div class="safety-emoji mb-3">👥</div>
                                <h5 class="card-title fw-bold text-white">Stay With Groups</h5>
                                <p class="card-text text-white">Travel with friends or family when possible, especially at night.</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-4">
                        <div class="card h-100 border-0 shadow rounded-4 safety-tip-card" style="background: linear-gradient(135deg,#74b9ff,#a29bfe);">
                            <div class="card-body text-center p-4">
                                <div class="safety-emoji mb-3">👀</div>
                                <h5 class="card-title fw-bold text-white">Stay Aware</h5>
                                <p class="card-text text-white">Keep your head up and trust your instincts about situations.</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-4">
                        <div class="card h-100 border-0 shadow rounded-4 safety-tip-card" style="background: linear-gradient(135deg,#fd79a8,#fdcb6e);">
                            <div class="card-body text-center p-4">
                                <div class="safety-emoji mb-3">📱</div>
                                <h5 class="card-title fw-bold text-white">Emergency Contacts</h5>
                                <p class="card-text text-white">Always have emergency contacts ready and know how to reach authorities.</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-4">
                        <div class="card h-100 border-0 shadow rounded-4 safety-tip-card" style="background: linear-gradient(135deg,#00b894,#55efc4);">
                            <div class="card-body text-center p-4">
                                <div class="safety-emoji mb-3">🏠</div>
                                <h5 class="card-title fw-bold text-white">Know Your Area</h5>
                                <p class="card-text text-white">Know safe places, well-lit areas, and routes near you.</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-4">
                        <div class="card h-100 border-0 shadow rounded-4 safety-tip-card" style="background: linear-gradient(135deg,#e17055,#fab1a0);">
                            <div class="card-body text-center p-4">
                                <div class="safety-emoji mb-3">💬</div>
                                <h5 class="card-title fw-bold text-white">Communicate</h5>
                                <p class="card-text text-white">Let trusted adults know where you are going and when you will be back.</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-4">
                        <div class="card h-100 border-0 shadow rounded-4 safety-tip-card" style="background: linear-gradient(135deg,#6c5ce7,#a29bfe);">
                            <div class="card-body text-center p-4">
                                <div class="safety-emoji mb-3">🛡️</div>
                                <h5 class="card-title fw-bold text-white">Trust Your Instincts</h5>
                                <p class="card-text text-white">If something feels wrong, leave and seek help immediately.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Resources -->
        <div class="row justify-content-center mb-5">
            <div class="col-lg-8">
                <div class="card border-0 bg-light rounded-4">
                    <div class="card-body p-4 text-center">
                        <h5 class="card-title fw-bold mb-3"><i class="fas fa-life-ring me-2 text-primary"></i>Need Help?</h5>
                        <p class="card-text mb-3">If you are in immediate danger, call <strong>911</strong>.</p>
                        <div class="d-flex flex-wrap justify-content-center gap-3">
                            <a href="https://www.nsopw.gov" target="_blank" class="btn btn-outline-primary rounded-3">NSOPW Official Site</a>
                            <a href="https://www.rainn.org" target="_blank" class="btn btn-outline-success rounded-3">RAINN Support</a>
                            <a href="tel:988" class="btn btn-outline-warning rounded-3">Crisis Lifeline: 988</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="bg-dark text-light py-4 mt-5">
        <div class="container text-center">
            <p class="mb-2">&copy; 2025 SafeZone - Community Safety Awareness</p>
            <p class="small text-muted mb-0">For educational purposes only. Always verify through official sources.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>
```

---

## static/css/style.css

```css
:root {
    --primary-color: #ff6b6b;
    --primary-dark: #ff5252;
    --secondary-color: #4ecdc4;
    --accent-color: #45b7d1;
    --success-color: #96ceb4;
    --warning-color: #ffeaa7;
    --danger-color: #fd79a8;
    --info-color: #74b9ff;
    --purple-color: #a29bfe;
    --pink-color: #fd79a8;
    --mint-color: #00b894;
    --light-bg: #f8fafc;
    --card-shadow: 0 15px 35px rgba(255, 107, 107, 0.15);
    --border-radius: 1.5rem;
    --gradient-primary: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%);
    --gradient-secondary: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
    --gradient-accent: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%);
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--gradient-primary);
    min-height: 100vh;
    background-attachment: fixed;
}

body::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        radial-gradient(circle at 20% 50%, rgba(255,107,107,0.3) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(78,205,196,0.3) 0%, transparent 50%),
        radial-gradient(circle at 40% 80%, rgba(116,185,255,0.2) 0%, transparent 50%);
    pointer-events: none;
    z-index: -1;
}

.navbar { backdrop-filter: blur(10px); background-color: rgba(255,255,255,0.95) !important; }
.navbar-brand { font-size: 1.5rem; font-weight: 700; }
.container { position: relative; z-index: 1; }

.card {
    transition: all 0.3s ease;
    border: none !important;
    box-shadow: var(--card-shadow);
    border-radius: var(--border-radius) !important;
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(10px);
}
.card:hover { transform: translateY(-8px) scale(1.02); box-shadow: 0 25px 50px rgba(255,107,107,0.2); }

.form-control {
    border: 2px solid rgba(255,107,107,0.2);
    transition: all 0.3s ease;
    font-size: 1.1rem;
    border-radius: var(--border-radius);
    background: rgba(255,255,255,0.9);
}
.form-control:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 0.2rem rgba(255,107,107,0.25);
    transform: scale(1.02);
}

.btn { font-weight: 600; transition: all 0.3s ease; border: none; border-radius: var(--border-radius); }
.btn-primary {
    background: var(--gradient-primary);
    padding: 0.75rem 2rem;
    font-size: 1.1rem;
    color: white;
    box-shadow: 0 8px 25px rgba(255,107,107,0.3);
}
.btn-primary:hover { transform: translateY(-3px); box-shadow: 0 15px 35px rgba(255,107,107,0.4); color: white; }

.safety-tip-card { transition: all 0.3s ease; position: relative; overflow: hidden; }
.safety-tip-card:hover { transform: translateY(-10px) scale(1.05); box-shadow: 0 20px 40px rgba(0,0,0,0.3); }

.safety-emoji { font-size: 3rem; animation: float 3s ease-in-out infinite; }
.safety-tip-card:hover .safety-emoji { transform: scale(1.2) rotate(5deg); }

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

.hero-illustration svg { animation: pulse-glow 2s ease-in-out infinite alternate; }
@keyframes pulse-glow {
    from { filter: drop-shadow(0 0 10px rgba(255,107,107,0.3)); }
    to { filter: drop-shadow(0 0 20px rgba(78,205,196,0.5)); }
}

.results-safe { background: linear-gradient(135deg, #96ceb4, #55efc4); border-left: 5px solid var(--success-color); color: white; }
.results-warning { background: linear-gradient(135deg, #fdcb6e, #e17055); border-left: 5px solid var(--warning-color); color: white; }
.results-danger { background: linear-gradient(135deg, #fd79a8, #e84393); border-left: 5px solid var(--danger-color); color: white; }
.results-safe h4, .results-warning h4, .results-danger h4 { color: white !important; }
.results-safe p, .results-warning p, .results-danger p { color: white !important; }

#map { border-radius: 0 0 var(--border-radius) var(--border-radius); z-index: 1; }

.fade-in { animation: fadeIn 0.5s ease-in; }
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.history-item { transition: all 0.3s ease; border-radius: 0.5rem; margin-bottom: 0.5rem; }
.history-item:hover { background-color: #f8fafc; transform: translateX(5px); }

@media (max-width: 768px) {
    .display-5 { font-size: 2rem; }
    .card-body { padding: 1.5rem !important; }
    .btn-lg { padding: 0.75rem 1.5rem; font-size: 1rem; }
}
```

---

## static/js/app.js

```javascript
class SafeZoneApp {
    constructor() {
        this.map = null;
        this.searchHistory = this.loadSearchHistory();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.displaySearchHistory();
    }

    setupEventListeners() {
        const searchForm = document.getElementById('searchForm');
        const zipCodeInput = document.getElementById('zipCode');

        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSearch();
        });

        zipCodeInput.addEventListener('input', (e) => {
            const zip = e.target.value.trim();
            e.target.setCustomValidity(/^\d{5}$/.test(zip) || zip.length === 0 ? '' : 'Please enter a valid 5-digit ZIP code');
        });

        zipCodeInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); this.handleSearch(); }
        });
    }

    async handleSearch() {
        const zipCode = document.getElementById('zipCode').value.trim();
        if (!/^\d{5}$/.test(zipCode)) {
            this.showError('Please enter a valid 5-digit ZIP code');
            return;
        }

        this.setLoadingState(true);

        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ zip_code: zipCode })
            });

            const data = await response.json();

            if (data.success) {
                this.displayResults(data);
                this.addToSearchHistory(zipCode, data);
                this.displaySearchHistory();
            } else {
                this.showError(data.error || 'An error occurred while searching');
            }
        } catch (error) {
            this.showError('Unable to connect to the server. Please try again.');
        } finally {
            this.setLoadingState(false);
        }
    }

    setLoadingState(isLoading) {
        const searchBtn = document.getElementById('searchBtnText');
        const loadingSpinner = document.getElementById('loadingSpinner');
        const submitButton = document.querySelector('button[type="submit"]');
        searchBtn.textContent = isLoading ? '🔍 Searching...' : '🔍 Check My Area';
        loadingSpinner.classList.toggle('d-none', !isLoading);
        submitButton.disabled = isLoading;
    }

    displayResults(data) {
        const resultsContainer = document.getElementById('searchResults');
        const resultsContent = document.getElementById('resultsContent');
        const resultsCard = document.getElementById('resultsCard');

        const isWarning = data.has_offenders;
        resultsCard.className = `card border-0 shadow rounded-4 ${isWarning ? 'results-warning' : 'results-safe'}`;

        let offenderListHtml = '';
        if (isWarning && data.offenders) {
            offenderListHtml = `
                <div class="mt-4">
                    <h6 class="fw-bold mb-3">Registered Offenders in Area:</h6>
                    <div class="row g-3">
                        ${data.offenders.map(o => `
                            <div class="col-md-6">
                                <div class="card border-0 bg-white bg-opacity-75">
                                    <div class="card-body p-3">
                                        <h6>${o.name}</h6>
                                        <p class="small mb-1"><strong>Age:</strong> ${o.age}<br>
                                        <strong>Offense:</strong> ${o.offense_type}<br>
                                        <strong>Conviction:</strong> ${o.conviction_date}</p>
                                        <small class="text-muted">${o.address}</small>
                                    </div>
                                </div>
                            </div>`).join('')}
                    </div>
                </div>`;
        }

        resultsContent.innerHTML = `
            <div class="text-center">
                <h4 class="fw-bold mb-3">${isWarning ? '⚠️ Heads Up!' : '✅ All Good!'}</h4>
                <p class="lead mb-3">${data.message}</p>
                ${offenderListHtml}
                <small class="text-muted">For educational purposes only. Always verify through official sources.</small>
            </div>`;

        resultsContainer.classList.remove('d-none');
        resultsContainer.classList.add('fade-in');

        if (isWarning && data.offenders.some(o => o.lat && o.lng)) {
            this.initializeMap(data.zip_code, data.offenders);
        }

        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    initializeMap(zipCode, offenders) {
        const mapContainer = document.getElementById('mapContainer');
        const mapElement = document.getElementById('map');
        mapContainer.classList.remove('d-none');

        if (this.map) { this.map.remove(); this.map = null; }

        const valid = offenders.filter(o => o.lat && o.lng && o.lat !== 0 && o.lng !== 0);
        if (valid.length === 0) return;

        this.map = L.map('map').setView([valid[0].lat, valid[0].lng], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);

        valid.forEach(o => {
            L.marker([o.lat, o.lng]).addTo(this.map).bindPopup(
                `<b>${o.name}</b><br>${o.offense_type}<br>${o.address}`
            );
        });

        if (valid.length > 1) {
            const group = new L.featureGroup(valid.map(o => L.marker([o.lat, o.lng])));
            this.map.fitBounds(group.getBounds().pad(0.1));
        }
    }

    showError(message) {
        const resultsContainer = document.getElementById('searchResults');
        const resultsContent = document.getElementById('resultsContent');
        const resultsCard = document.getElementById('resultsCard');
        resultsCard.className = 'card border-0 shadow rounded-4 results-danger';
        resultsContent.innerHTML = `
            <div class="text-center">
                <h4 class="fw-bold mb-3">Search Error</h4>
                <p class="lead mb-3">${message}</p>
            </div>`;
        resultsContainer.classList.remove('d-none');
    }

    addToSearchHistory(zipCode, data) {
        this.searchHistory = this.searchHistory.filter(i => i.zipCode !== zipCode);
        this.searchHistory.unshift({
            zipCode,
            timestamp: new Date().toLocaleString(),
            offenderCount: data.offender_count,
            hasOffenders: data.has_offenders
        });
        this.searchHistory = this.searchHistory.slice(0, 10);
        this.saveSearchHistory();
    }

    displaySearchHistory() {
        const historyContainer = document.getElementById('searchHistory');
        const historyList = document.getElementById('historyList');
        if (this.searchHistory.length === 0) { historyContainer.classList.add('d-none'); return; }
        historyContainer.classList.remove('d-none');
        historyList.innerHTML = this.searchHistory.map(item => `
            <div class="history-item p-3 border rounded-3 d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-1">ZIP: ${item.zipCode}</h6>
                    <small class="text-muted">${item.timestamp}</small>
                </div>
                <span class="${item.hasOffenders ? 'text-warning' : 'text-success'}">
                    ${item.hasOffenders ? `⚠️ ${item.offenderCount} offender(s)` : '✅ Clear'}
                </span>
            </div>`).join('');
    }

    loadSearchHistory() {
        try { return JSON.parse(localStorage.getItem('safezone_search_history') || '[]'); }
        catch { return []; }
    }

    saveSearchHistory() {
        try { localStorage.setItem('safezone_search_history', JSON.stringify(this.searchHistory)); }
        catch (e) { console.error('Error saving history:', e); }
    }
}

document.addEventListener('DOMContentLoaded', () => new SafeZoneApp());

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
});
```
