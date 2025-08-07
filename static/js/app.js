// SafeZone App - Main JavaScript functionality
class SafeZoneApp {
    constructor() {
        this.map = null;
        this.searchHistory = this.loadSearchHistory();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.displaySearchHistory();
        this.setupFormValidation();
    }

    setupEventListeners() {
        const searchForm = document.getElementById('searchForm');
        const zipCodeInput = document.getElementById('zipCode');

        // Form submission
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSearch();
        });

        // Real-time ZIP code validation
        zipCodeInput.addEventListener('input', (e) => {
            this.validateZipCode(e.target);
        });

        // Enter key handling
        zipCodeInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.handleSearch();
            }
        });
    }

    setupFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }

    validateZipCode(input) {
        const zipCode = input.value.trim();
        const isValid = /^\d{5}$/.test(zipCode);
        
        if (zipCode.length > 0 && !isValid) {
            input.setCustomValidity('Please enter a valid 5-digit ZIP code');
        } else {
            input.setCustomValidity('');
        }
    }

    async handleSearch() {
        const zipCodeInput = document.getElementById('zipCode');
        const zipCode = zipCodeInput.value.trim();

        if (!this.isValidZipCode(zipCode)) {
            this.showError('Please enter a valid 5-digit ZIP code');
            return;
        }

        this.setLoadingState(true);

        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
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
            console.error('Search error:', error);
            this.showError('Unable to connect to the server. Please try again.');
        } finally {
            this.setLoadingState(false);
        }
    }

    isValidZipCode(zipCode) {
        return /^\d{5}$/.test(zipCode);
    }

    setLoadingState(isLoading) {
        const searchBtn = document.getElementById('searchBtnText');
        const loadingSpinner = document.getElementById('loadingSpinner');
        const submitButton = document.querySelector('button[type="submit"]');

        if (isLoading) {
            searchBtn.textContent = 'Searching...';
            loadingSpinner.classList.remove('d-none');
            submitButton.disabled = true;
        } else {
            searchBtn.textContent = 'Check Area';
            loadingSpinner.classList.add('d-none');
            submitButton.disabled = false;
        }
    }

    displayResults(data) {
        const resultsContainer = document.getElementById('searchResults');
        const resultsContent = document.getElementById('resultsContent');
        const resultsCard = document.getElementById('resultsCard');

        let resultClass, iconClass, titleText, messageText;

        if (data.has_offenders) {
            resultClass = 'results-warning';
            iconClass = 'fas fa-exclamation-triangle text-warning';
            titleText = 'Area Alert';
            messageText = `Found ${data.offender_count} registered offender(s) in ZIP code ${data.zip_code}. Please review the safety information below and stay aware of your surroundings.`;
        } else {
            resultClass = 'results-safe';
            iconClass = 'fas fa-check-circle text-success';
            titleText = 'Area Clear';
            messageText = `No registered offenders found in ZIP code ${data.zip_code}. Remember to always stay vigilant and follow safety practices.`;
        }

        resultsCard.className = `card border-0 shadow rounded-4 ${resultClass}`;
        
        let offenderListHtml = '';
        if (data.has_offenders && data.offenders) {
            offenderListHtml = `
                <div class="mt-4">
                    <h6 class="fw-bold mb-3">Registered Offenders in Area:</h6>
                    <div class="row g-3">
                        ${data.offenders.map(offender => `
                            <div class="col-md-6">
                                <div class="card border-0 bg-white bg-opacity-75">
                                    <div class="card-body p-3">
                                        <h6 class="card-title mb-1">${offender.name}</h6>
                                        <p class="card-text small mb-1">
                                            <strong>Age:</strong> ${offender.age}<br>
                                            <strong>Offense:</strong> ${offender.offense_type}<br>
                                            <strong>Conviction:</strong> ${offender.conviction_date}
                                        </p>
                                        <small class="text-muted">Address: ${offender.address}</small>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        resultsContent.innerHTML = `
            <div class="text-center">
                <i class="${iconClass} fa-3x mb-3"></i>
                <h4 class="fw-bold mb-3">${titleText}</h4>
                <p class="lead mb-3">${messageText}</p>
                ${offenderListHtml}
                <div class="mt-4">
                    <small class="text-muted">
                        <i class="fas fa-info-circle me-1"></i>
                        This information is for educational purposes. Always verify through official sources.
                    </small>
                </div>
            </div>
        `;

        resultsContainer.classList.remove('d-none');
        resultsContainer.classList.add('fade-in');

        // Initialize map if there are offenders with coordinates
        if (data.has_offenders && data.offenders.some(o => o.lat && o.lng)) {
            this.initializeMap(data.zip_code, data.offenders);
        }

        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    initializeMap(zipCode, offenders) {
        const mapContainer = document.getElementById('mapContainer');
        const mapElement = document.getElementById('map');

        mapContainer.classList.remove('d-none');
        mapContainer.classList.add('fade-in');

        // Clear existing map
        if (this.map) {
            this.map.remove();
        }

        // Filter offenders with valid coordinates
        const validOffenders = offenders.filter(o => o.lat && o.lng && o.lat !== 0 && o.lng !== 0);

        if (validOffenders.length === 0) {
            mapElement.innerHTML = '<div class="d-flex align-items-center justify-content-center h-100"><p class="text-muted">Map coordinates not available for this area</p></div>';
            return;
        }

        // Initialize map centered on first offender
        const firstOffender = validOffenders[0];
        this.map = L.map('map').setView([firstOffender.lat, firstOffender.lng], 13);

        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);

        // Add markers for each offender
        validOffenders.forEach((offender, index) => {
            const marker = L.marker([offender.lat, offender.lng])
                .addTo(this.map)
                .bindPopup(`
                    <div class="p-2">
                        <h6 class="mb-2">${offender.name}</h6>
                        <p class="mb-1 small"><strong>Age:</strong> ${offender.age}</p>
                        <p class="mb-1 small"><strong>Offense:</strong> ${offender.offense_type}</p>
                        <p class="mb-0 small"><strong>Address:</strong> ${offender.address}</p>
                    </div>
                `);
        });

        // Fit map to show all markers
        if (validOffenders.length > 1) {
            const group = new L.featureGroup(validOffenders.map(o => L.marker([o.lat, o.lng])));
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
                <i class="fas fa-exclamation-circle text-danger fa-3x mb-3"></i>
                <h4 class="fw-bold mb-3">Search Error</h4>
                <p class="lead mb-3">${message}</p>
                <button class="btn btn-primary" onclick="location.reload()">
                    <i class="fas fa-refresh me-2"></i>Try Again
                </button>
            </div>
        `;

        resultsContainer.classList.remove('d-none');
        resultsContainer.classList.add('fade-in');
    }

    addToSearchHistory(zipCode, data) {
        const timestamp = new Date().toLocaleString();
        const historyItem = {
            zipCode,
            timestamp,
            offenderCount: data.offender_count,
            hasOffenders: data.has_offenders
        };

        // Remove duplicate ZIP codes
        this.searchHistory = this.searchHistory.filter(item => item.zipCode !== zipCode);
        
        // Add new item to beginning
        this.searchHistory.unshift(historyItem);
        
        // Keep only last 10 searches
        this.searchHistory = this.searchHistory.slice(0, 10);
        
        // Save to localStorage
        this.saveSearchHistory();
    }

    displaySearchHistory() {
        const historyContainer = document.getElementById('searchHistory');
        const historyList = document.getElementById('historyList');

        if (this.searchHistory.length === 0) {
            historyContainer.classList.add('d-none');
            return;
        }

        historyContainer.classList.remove('d-none');
        
        historyList.innerHTML = this.searchHistory.map(item => {
            const statusClass = item.hasOffenders ? 'text-warning' : 'text-success';
            const statusIcon = item.hasOffenders ? 'fas fa-exclamation-triangle' : 'fas fa-check-circle';
            const statusText = item.hasOffenders ? `${item.offenderCount} offender(s) found` : 'Area clear';
            
            return `
                <div class="history-item p-3 border rounded-3 d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1">ZIP Code: ${item.zipCode}</h6>
                        <small class="text-muted">${item.timestamp}</small>
                    </div>
                    <div class="text-end">
                        <span class="${statusClass}">
                            <i class="${statusIcon} me-1"></i>
                            ${statusText}
                        </span>
                    </div>
                </div>
            `;
        }).join('');
    }

    loadSearchHistory() {
        try {
            const stored = localStorage.getItem('safezone_search_history');
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('Error loading search history:', error);
            return [];
        }
    }

    saveSearchHistory() {
        try {
            localStorage.setItem('safezone_search_history', JSON.stringify(this.searchHistory));
        } catch (error) {
            console.error('Error saving search history:', error);
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SafeZoneApp();
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add some interactive feedback for safety tip cards
document.addEventListener('DOMContentLoaded', () => {
    const safetyCards = document.querySelectorAll('.safety-tip-card');
    
    safetyCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
        });
    });
});
