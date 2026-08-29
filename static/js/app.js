// SafeZone - main client logic.
//
// Rendering rule: registry data is third-party content and is never
// interpolated into innerHTML. Everything derived from a response is written
// through textContent or created with createElement, so a stray angle bracket
// in a real name or address can never become markup.

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
            const value = e.target.value.trim();
            e.target.setCustomValidity(
                value.length > 0 && !this.isValidZipCode(value)
                    ? 'Please enter a valid 5-digit ZIP code'
                    : ''
            );
        });
    }

    isValidZipCode(zipCode) {
        return /^\d{5}$/.test(zipCode);
    }

    async handleSearch() {
        const zipCode = document.getElementById('zipCode').value.trim();

        if (!this.isValidZipCode(zipCode)) {
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

            if (response.ok && data.success) {
                this.displayResults(data);
                this.addToSearchHistory(zipCode, data);
                this.displaySearchHistory();
            } else {
                this.showError(data.error || 'An error occurred while searching');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Unable to connect to the server. Please try again.');
        } finally {
            this.setLoadingState(false);
        }
    }

    setLoadingState(isLoading) {
        const searchBtn = document.getElementById('searchBtnText');
        const loadingSpinner = document.getElementById('loadingSpinner');
        const submitButton = document.querySelector('button[type="submit"]');

        searchBtn.textContent = isLoading ? 'Searching…' : 'Check My Area';
        loadingSpinner.classList.toggle('d-none', !isLoading);
        submitButton.disabled = isLoading;
    }

    // --- rendering helpers -------------------------------------------------

    el(tag, className, text) {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (text !== undefined && text !== null) node.textContent = String(text);
        return node;
    }

    labelled(label, value) {
        const p = this.el('p', 'card-text small mb-1');
        p.appendChild(this.el('strong', null, `${label}: `));
        p.appendChild(document.createTextNode(String(value)));
        return p;
    }

    officialLink(url, label) {
        const a = this.el('a', 'btn btn-primary rounded-3 mt-3', label);
        a.href = url;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        return a;
    }

    // --- results -----------------------------------------------------------

    displayResults(data) {
        const container = document.getElementById('searchResults');
        const content = document.getElementById('resultsContent');
        const card = document.getElementById('resultsCard');

        content.replaceChildren();

        let resultClass, titleText;
        if (!data.covered) {
            resultClass = 'results-neutral';
            titleText = data.degraded ? 'Source Unavailable' : 'Area Not Covered Yet';
        } else if (data.has_offenders) {
            resultClass = 'results-warning';
            titleText = 'Records Found';
        } else {
            resultClass = 'results-safe';
            titleText = 'No Records Listed';
        }

        card.className = `card border-0 shadow rounded-4 ${resultClass}`;

        const wrapper = this.el('div', 'text-center');
        wrapper.appendChild(this.el('h4', 'fw-bold mb-3', titleText));
        wrapper.appendChild(this.el('p', 'lead mb-3', data.message));

        if (data.covered && data.offenders && data.offenders.length) {
            wrapper.appendChild(this.buildOffenderList(data.offenders));
        }

        if (!data.covered && data.official_search_url) {
            wrapper.appendChild(
                this.officialLink(data.official_search_url, 'Search the Official Registry →')
            );
        }

        if (data.covered && data.source) {
            const src = this.el('p', 'text-muted small mt-4 mb-0');
            src.appendChild(document.createTextNode(`Source: ${data.attribution || data.source}. `));
            if (data.official_search_url) {
                const a = this.el('a', null, 'Verify on the official registry');
                a.href = data.official_search_url;
                a.target = '_blank';
                a.rel = 'noopener noreferrer';
                src.appendChild(a);
            }
            wrapper.appendChild(src);
        }

        content.appendChild(wrapper);
        container.classList.remove('d-none');
        container.classList.add('fade-in');

        const mappable = (data.offenders || []).filter((o) => o.lat && o.lng);
        if (data.covered && mappable.length) {
            this.initializeMap(mappable);
        } else {
            document.getElementById('mapContainer').classList.add('d-none');
        }

        container.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    buildOffenderList(offenders) {
        const section = this.el('div', 'mt-4 text-start');
        section.appendChild(this.el('h6', 'fw-bold mb-3', 'Registry records for this ZIP code:'));

        const row = this.el('div', 'row g-3');
        offenders.forEach((offender) => {
            const col = this.el('div', 'col-md-6');
            const card = this.el('div', 'card border-0 bg-white bg-opacity-75');
            const body = this.el('div', 'card-body p-3');

            body.appendChild(this.el('h6', 'card-title mb-1', offender.name));
            if (offender.age) body.appendChild(this.labelled('Age', offender.age));
            if (offender.offense) body.appendChild(this.labelled('Offense', offender.offense));
            if (offender.conviction_date) body.appendChild(this.labelled('Convicted', offender.conviction_date));
            if (offender.address) {
                body.appendChild(this.el('small', 'text-muted d-block mt-2', offender.address));
            }
            if (offender.source_url) {
                const a = this.el('a', 'small d-block mt-2', 'View official record →');
                a.href = offender.source_url;
                a.target = '_blank';
                a.rel = 'noopener noreferrer';
                body.appendChild(a);
            }

            card.appendChild(body);
            col.appendChild(card);
            row.appendChild(col);
        });

        section.appendChild(row);
        return section;
    }

    initializeMap(offenders) {
        const mapContainer = document.getElementById('mapContainer');
        mapContainer.classList.remove('d-none');

        if (this.map) this.map.remove();

        this.map = L.map('map').setView([offenders[0].lat, offenders[0].lng], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(this.map);

        const bounds = [];
        offenders.forEach((offender) => {
            const popup = this.el('div', 'p-1');
            popup.appendChild(this.el('h6', 'mb-2', offender.name));
            if (offender.offense) popup.appendChild(this.labelled('Offense', offender.offense));
            if (offender.address) popup.appendChild(this.labelled('Address', offender.address));

            L.marker([offender.lat, offender.lng]).addTo(this.map).bindPopup(popup);
            bounds.push([offender.lat, offender.lng]);
        });

        if (bounds.length > 1) {
            this.map.fitBounds(L.latLngBounds(bounds).pad(0.1));
        }
    }

    showError(message) {
        const container = document.getElementById('searchResults');
        const content = document.getElementById('resultsContent');
        const card = document.getElementById('resultsCard');

        card.className = 'card border-0 shadow rounded-4 results-danger';
        content.replaceChildren();

        const wrapper = this.el('div', 'text-center');
        wrapper.appendChild(this.el('h4', 'fw-bold mb-3', 'Search Error'));
        wrapper.appendChild(this.el('p', 'lead mb-0', message));
        content.appendChild(wrapper);

        container.classList.remove('d-none');
        document.getElementById('mapContainer').classList.add('d-none');
    }

    // --- history -----------------------------------------------------------

    addToSearchHistory(zipCode, data) {
        this.searchHistory = this.searchHistory.filter((item) => item.zipCode !== zipCode);
        this.searchHistory.unshift({
            zipCode,
            timestamp: new Date().toLocaleString(),
            covered: data.covered,
            offenderCount: data.count
        });
        this.searchHistory = this.searchHistory.slice(0, 10);
        this.saveSearchHistory();
    }

    displaySearchHistory() {
        const container = document.getElementById('searchHistory');
        const list = document.getElementById('historyList');

        if (!this.searchHistory.length) {
            container.classList.add('d-none');
            return;
        }
        container.classList.remove('d-none');
        list.replaceChildren();

        this.searchHistory.forEach((item) => {
            const row = this.el('div', 'history-item p-3 border rounded-3 d-flex justify-content-between align-items-center');
            const left = this.el('div');
            left.appendChild(this.el('h6', 'mb-1', `ZIP Code: ${item.zipCode}`));
            left.appendChild(this.el('small', 'text-muted', item.timestamp));

            let statusText, statusClass;
            if (!item.covered) {
                statusText = 'Not covered';
                statusClass = 'text-muted';
            } else if (item.offenderCount > 0) {
                statusText = `${item.offenderCount} record(s)`;
                statusClass = 'text-warning';
            } else {
                statusText = 'None listed';
                statusClass = 'text-success';
            }

            const right = this.el('div', 'text-end');
            right.appendChild(this.el('span', statusClass, statusText));

            row.append(left, right);
            list.appendChild(row);
        });
    }

    loadSearchHistory() {
        try {
            const stored = localStorage.getItem('safezone_search_history');
            const parsed = stored ? JSON.parse(stored) : [];
            return Array.isArray(parsed) ? parsed : [];
        } catch (error) {
            return [];
        }
    }

    saveSearchHistory() {
        try {
            localStorage.setItem('safezone_search_history', JSON.stringify(this.searchHistory));
        } catch (error) {
            /* storage unavailable (private mode) - history is a convenience only */
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new SafeZoneApp();

    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});
