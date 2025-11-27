// Car Search Application
let allListingsGlobal = []; // Store all listings for filtering
let currentFilter = null; // Track current filter

document.addEventListener('DOMContentLoaded', function () {
    const searchForm = document.getElementById('searchForm');
    const resultsSection = document.getElementById('results');
    const resultsContainer = document.getElementById('resultsContainer');
    const resultsSummary = document.getElementById('resultsSummary');
    const noResults = document.getElementById('noResults');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const searchBtn = document.getElementById('searchBtn');

    // Notes elements
    const notesSection = document.getElementById('notes');
    const notesContainer = document.getElementById('notesContainer');
    const noNotes = document.getElementById('noNotes');
    const navNotes = document.getElementById('navNotes');
    const noteModal = document.getElementById('noteModal');
    const closeModal = document.querySelector('.close-modal');
    const noteForm = document.getElementById('noteForm');

    // Vehicle Program Data
    const PROGRAM_MAKES = {
        exotic: [
            'Aston Martin', 'Bentley', 'Ferrari', 'Lamborghini', 'Maserati',
            'McLaren', 'Rolls Royce'
        ],
        high_end: [
            'Acura', 'Alfa Romeo', 'Audi', 'BMW', 'Hummer', 'Infiniti', 'Jaguar',
            'Lexus', 'Lincoln', 'Lotus', 'Lucid', 'Mercedes-Benz', 'Mini',
            'Polestar', 'Porsche', 'Rivian', 'Tesla', 'Volvo'
        ],
        flagship: [
            'Buick', 'Cadillac', 'Chevrolet', 'Chrysler', 'Dodge', 'Fiat', 'Ford',
            'Genesis', 'GMC', 'Honda', 'Hyundai', 'Jeep', 'Kia', 'Land Rover',
            'Mazda', 'Mitsubishi', 'Nissan', 'Oldsmobile', 'Pontiac', 'RAM',
            'Saab', 'Saturn', 'Scion', 'Subaru', 'Suzuki', 'Toyota', 'Volkswagen'
        ]
    };

    // Vehicle Program Logic
    const vehicleProgramSelect = document.getElementById('vehicle_program');
    const makeInput = document.getElementById('make');

    if (vehicleProgramSelect) {
        // Handle program selection
        vehicleProgramSelect.addEventListener('change', function () {
            const program = this.value;
            if (program && PROGRAM_MAKES[program]) {
                makeInput.value = PROGRAM_MAKES[program].join(', ');
            } else {
                // If "Custom" is selected, we could clear it, or leave it. 
                // Let's clear it to avoid confusion if they switch back to custom explicitly.
                if (program === '') {
                    makeInput.value = '';
                }
            }
        });

        // Handle manual make input changes
        makeInput.addEventListener('input', function () {
            // If user types manually, reset program to "Custom"
            vehicleProgramSelect.value = '';
        });
    }

    // Form submission
    searchForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        // Get form data
        const makeInput = document.getElementById('make').value.trim();
        const modelInput = document.getElementById('model').value.trim();

        const formData = {
            make: makeInput,
            model: modelInput || null,
            year_min: document.getElementById('year_min').value || null,
            year_max: document.getElementById('year_max').value || null,
            price_min: document.getElementById('price_min').value || null,
            price_max: document.getElementById('price_max').value || null,
            location: document.getElementById('location').value.trim() || null,
            max_results: parseInt(document.getElementById('max_results').value) || 20,
            enable_facebook: document.getElementById('enable_facebook').checked,
            private_sellers_only: document.getElementById('private_sellers_only').checked
        };

        // Validate
        if (!formData.location) {
            alert('Please enter a location or ZIP code');
            return;
        }

        // Show loading
        loadingOverlay.style.display = 'flex';
        searchBtn.disabled = true;
        resultsSection.style.display = 'none';
        notesSection.style.display = 'none';

        try {
            // Make API request
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            // Hide loading
            loadingOverlay.style.display = 'none';
            searchBtn.disabled = false;

            if (data.success) {
                displayResults(data);
            } else {
                alert('Error: ' + (data.error || 'Unknown error occurred'));
            }
        } catch (error) {
            loadingOverlay.style.display = 'none';
            searchBtn.disabled = false;
            alert('Error connecting to server: ' + error.message);
            console.error('Search error:', error);
        }
    });

    // Display results
    function displayResults(data) {
        const { summary, total, listings } = data;

        // Store listings globally for filtering
        allListingsGlobal = listings;
        currentFilter = null;

        // Show results section
        resultsSection.style.display = 'block';

        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

        // Display summary
        displaySummary(summary, total);

        // Display listings
        if (listings && listings.length > 0) {
            noResults.style.display = 'none';
            resultsContainer.innerHTML = '';

            listings.forEach(listing => {
                const card = createCarCard(listing);
                resultsContainer.appendChild(card);
            });
        } else {
            noResults.style.display = 'block';
            resultsContainer.innerHTML = '';
        }
    }

    // Display summary
    function displaySummary(summary, total) {
        let html = '';

        for (const [source, count] of Object.entries(summary)) {
            if (count > 0) {
                html += `<div class="summary-badge" data-source="${source}">
                    <span class="source-name">${source}:</span>
                    <span class="count">${count}</span>
                </div>`;
            }
        }

        html += `<div class="summary-badge total" data-source="all">
            <span class="source-name">Total:</span>
            <span class="count">${total}</span>
        </div>`;

        resultsSummary.innerHTML = html;

        // Add click handlers to badges
        document.querySelectorAll('.summary-badge').forEach(badge => {
            badge.addEventListener('click', function () {
                const source = this.getAttribute('data-source');
                filterBySource(source);
            });
        });
    }

    // Filter results by source
    function filterBySource(source) {
        // Update active state
        document.querySelectorAll('.summary-badge').forEach(b => b.classList.remove('active'));
        document.querySelector(`[data-source="${source}"]`).classList.add('active');

        // Filter listings
        let filteredListings;
        if (source === 'all') {
            filteredListings = allListingsGlobal;
            currentFilter = null;
        } else {
            filteredListings = allListingsGlobal.filter(listing => listing.source === source);
            currentFilter = source;
        }

        // Display filtered listings
        resultsContainer.innerHTML = '';
        if (filteredListings.length > 0) {
            noResults.style.display = 'none';
            filteredListings.forEach(listing => {
                const card = createCarCard(listing);
                resultsContainer.appendChild(card);
            });
        } else {
            noResults.style.display = 'block';
        }
    }

    // Create car card
    function createCarCard(listing) {
        const card = document.createElement('div');
        card.className = 'car-card';

        // Format source for badge class
        const sourceClass = listing.source.toLowerCase().replace(/\s+/g, '-');

        // Image
        const imageHtml = listing.image_url
            ? `<img src="${listing.image_url}" alt="${listing.title}" onerror="this.parentElement.innerHTML='<div style=\\'padding: 2rem; text-align: center; color: #999;\\'>No Image</div>'">`
            : '<div style="padding: 2rem; text-align: center; color: #999;">No Image</div>';

        // Details
        const details = [];
        if (listing.year) {
            details.push(`<div class="car-detail-item">📅 ${listing.year}</div>`);
        }
        if (listing.mileage) {
            details.push(`<div class="car-detail-item">🛣️ ${listing.mileage}</div>`);
        }
        if (listing.location && listing.location !== 'N/A') {
            details.push(`<div class="car-detail-item">📍 ${listing.location}</div>`);
        }

        card.innerHTML = `
            <div class="car-image">
                ${imageHtml}
            </div>
            <div class="car-content">
                <h4 class="car-title">${listing.title || 'No title available'}</h4>
                <div class="car-price">${listing.price || 'Price not available'}</div>
                ${details.length > 0 ? `<div class="car-details">${details.join('')}</div>` : ''}
                <div class="car-footer">
                    <span class="source-badge ${sourceClass}">${listing.source}</span>
                    <button class="btn-note" data-url="${listing.url}" data-title="${listing.title}" data-price="${listing.price}" data-source="${listing.source}" data-image="${listing.image_url || ''}">📝 Note</button>
                    <a href="${listing.url}" target="_blank" class="view-link">View Listing →</a>
                </div>
            </div>
        `;

        // Add click handler to open link
        card.addEventListener('click', function (e) {
            if (e.target.closest('.btn-note')) {
                const btn = e.target.closest('.btn-note');
                openNoteModal({
                    url: btn.dataset.url,
                    title: btn.dataset.title,
                    price: btn.dataset.price,
                    source: btn.dataset.source,
                    image_url: btn.dataset.image
                });
            } else if (!e.target.closest('.view-link')) {
                window.open(listing.url, '_blank');
            }
        });

        return card;
    }

    // Notes Functionality

    // Navigation
    navNotes.addEventListener('click', function (e) {
        e.preventDefault();
        document.getElementById('search').style.display = 'none';
        document.querySelector('.hero').style.display = 'none';
        resultsSection.style.display = 'none';
        notesSection.style.display = 'block';
        loadNotes();
    });

    document.querySelector('a[href="#search"]').addEventListener('click', function (e) {
        e.preventDefault();
        document.getElementById('search').style.display = 'block';
        document.querySelector('.hero').style.display = 'block';
        notesSection.style.display = 'none';
        if (resultsContainer.children.length > 0) {
            resultsSection.style.display = 'block';
        }
    });

    // Modal
    function openNoteModal(data) {
        document.getElementById('noteUrl').value = data.url;
        document.getElementById('noteTitle').value = data.title;
        document.getElementById('notePrice').value = data.price;
        document.getElementById('noteSource').value = data.source;
        document.getElementById('noteImage').value = data.image_url;
        document.getElementById('modalCarTitle').textContent = data.title;
        document.getElementById('noteText').value = ''; // Clear previous note

        // Check if note exists
        fetch('/api/notes')
            .then(res => res.json())
            .then(response => {
                if (response.success) {
                    const existing = response.notes.find(n => n.url === data.url);
                    if (existing) {
                        document.getElementById('noteText').value = existing.note;
                    }
                }
            });

        noteModal.style.display = 'block';
    }

    closeModal.addEventListener('click', () => noteModal.style.display = 'none');
    window.addEventListener('click', (e) => {
        if (e.target === noteModal) noteModal.style.display = 'none';
    });

    // Save Note
    noteForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const formData = {
            url: document.getElementById('noteUrl').value,
            title: document.getElementById('noteTitle').value,
            price: document.getElementById('notePrice').value,
            source: document.getElementById('noteSource').value,
            image_url: document.getElementById('noteImage').value,
            note: document.getElementById('noteText').value
        };

        try {
            const response = await fetch('/api/notes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.success) {
                noteModal.style.display = 'none';
                alert('Note saved successfully!');
            } else {
                alert('Error saving note: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            alert('Error saving note: ' + error.message);
        }
    });

    // Load Notes
    function loadNotes() {
        fetch('/api/notes')
            .then(res => res.json())
            .then(response => {
                if (response.success) {
                    displayNotes(response.notes);
                }
            })
            .catch(error => {
                console.error('Error loading notes:', error);
            });
    }

    // Display Notes
    function displayNotes(notes) {
        if (notes.length === 0) {
            noNotes.style.display = 'block';
            notesContainer.innerHTML = '';
            return;
        }

        noNotes.style.display = 'none';
        notesContainer.innerHTML = '';

        notes.forEach(note => {
            const card = document.createElement('div');
            card.className = 'car-card';

            const sourceClass = note.source.toLowerCase().replace(/\s+/g, '-');
            const imageHtml = note.image_url
                ? `<img src="${note.image_url}" alt="${note.title}">`
                : '<div style="padding: 2rem; text-align: center; color: #999;">No Image</div>';

            card.innerHTML = `
                <div class="car-image">
                    ${imageHtml}
                </div>
                <div class="car-content">
                    <h4 class="car-title">${note.title}</h4>
                    <div class="car-price">${note.price}</div>
                    <div class="note-content">${note.note}</div>
                    <div class="car-footer">
                        <span class="source-badge ${sourceClass}">${note.source}</span>
                        <div class="note-actions">
                            <button class="btn-delete" data-url="${note.url}">Delete</button>
                            <a href="${note.url}" target="_blank" class="view-link">View Listing →</a>
                        </div>
                    </div>
                </div>
            `;

            // Delete handler
            card.querySelector('.btn-delete').addEventListener('click', function () {
                if (confirm('Delete this note?')) {
                    deleteNote(note.url);
                }
            });

            notesContainer.appendChild(card);
        });
    }

    // Delete Note
    function deleteNote(url) {
        fetch('/api/notes', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        })
            .then(res => res.json())
            .then(response => {
                if (response.success) {
                    loadNotes();
                } else {
                    alert('Error deleting note');
                }
            })
            .catch(error => {
                alert('Error deleting note: ' + error.message);
            });
    }
});
