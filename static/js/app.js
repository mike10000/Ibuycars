// Car Search Application
let allListingsGlobal = []; // Store all listings for filtering
let currentFilter = null; // Track current filter

// Local Storage Key
const STORAGE_KEY = 'ibuycars_leads';

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
            if (program === 'all_vehicles') {
                makeInput.value = 'All Vehicles';
            } else if (program && PROGRAM_MAKES[program]) {
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
            enable_craigslist: document.getElementById('enable_craigslist').checked,
            enable_cars_com: document.getElementById('enable_cars_com').checked,
            enable_offerup: document.getElementById('enable_offerup').checked,
            enable_autotrader: document.getElementById('enable_autotrader').checked,
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
                    <div class="car-actions">
                        <button class="btn-note" data-url="${listing.url}" data-title="${listing.title}" data-price="${listing.price}" data-source="${listing.source}" data-image="${listing.image_url || ''}">📝 Notes</button>
                        <select class="lead-status-dropdown" data-url="${listing.url}" data-title="${listing.title}" data-price="${listing.price}" data-source="${listing.source}" data-image="${listing.image_url || ''}">
                            <option value="Not Contacted" style="background-color: #6c757d; color: white;">Not Contacted</option>
                            <option value="Pending" style="background-color: #ffc107; color: black;">Pending</option>
                            <option value="Captured" style="background-color: #28a745; color: white;">Captured</option>
                            <option value="Rejected" style="background-color: #dc3545; color: white;">Rejected</option>
                        </select>
                    </div>
                </div>
            </div>
        `;

        // Set initial status from API
        const dropdown = card.querySelector('.lead-status-dropdown');

        // Load status asynchronously
        getLeads().then(leads => {
            const existingLead = leads.find(l => l.url === listing.url);
            if (existingLead && existingLead.status) {
                dropdown.value = existingLead.status;
                updateDropdownColor(dropdown);
            }
        });

        // Update dropdown background color based on selection
        updateDropdownColor(dropdown);

        // Add click handler to open link
        card.addEventListener('click', function (e) {
            if (e.target.closest('.btn-note')) {
                e.stopPropagation();
                const btn = e.target.closest('.btn-note');
                openNoteModal({
                    url: btn.dataset.url,
                    title: btn.dataset.title,
                    price: btn.dataset.price,
                    source: btn.dataset.source,
                    image_url: btn.dataset.image
                });
            } else if (e.target.closest('.lead-status-dropdown')) {
                e.stopPropagation();
                // Dropdown click is handled by change event below
            } else {
                window.open(listing.url, '_blank');
            }
        });

        // Handle status change
        dropdown.addEventListener('change', async function (e) {
            e.stopPropagation();
            const newStatus = this.value;
            updateDropdownColor(this);

            // Save or update lead with new status
            const leadData = {
                url: listing.url,
                title: listing.title,
                price: listing.price,
                source: listing.source,
                image_url: listing.image_url || '',
                status: newStatus
            };

            await saveLead(leadData);
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


    // Helper to get leads from API
    async function getLeads() {
        try {
            const response = await fetch('/api/leads');
            if (response.ok) {
                const data = await response.json();
                return data.success ? data.leads : [];
            }
        } catch (error) {
            console.error('Error fetching leads:', error);
        }
        return [];
    }

    // Helper to save lead to API
    async function saveLead(leadData) {
        try {
            const response = await fetch('/api/leads', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(leadData)
            });
            return response.ok;
        } catch (error) {
            console.error('Error saving lead:', error);
            return false;
        }
    }

    // Save Note (Lead)
    document.getElementById('saveNoteBtn').addEventListener('click', async function (e) {
        e.preventDefault();

        const leadData = {
            url: document.getElementById('noteUrl').value,
            title: document.getElementById('noteTitle').value,
            price: document.getElementById('notePrice').value,
            source: document.getElementById('noteSource').value,
            image_url: document.getElementById('noteImage').value,
            seller_phone: document.getElementById('notePhone').value,
            notes: document.getElementById('noteText').value,
            status: 'new'
        };

        const success = await saveLead(leadData);

        if (success) {
            noteModal.style.display = 'none';

            if (notesSection.style.display === 'block') {
                loadNotes();
            }
        } else {
            alert('Error saving lead. Please try again.');
        }
    });

    // Modal
    async function openNoteModal(data) {
        document.getElementById('noteUrl').value = data.url;
        document.getElementById('noteTitle').value = data.title;
        document.getElementById('notePrice').value = data.price;
        document.getElementById('noteSource').value = data.source;
        document.getElementById('noteImage').value = data.image_url;
        document.getElementById('modalCarTitle').textContent = data.title;
        document.getElementById('noteText').value = ''; // Clear previous note
        document.getElementById('notePhone').value = ''; // Clear previous phone

        // Check if note exists in API
        const leads = await getLeads();
        const existing = leads.find(l => l.url === data.url);
        if (existing) {
            document.getElementById('noteText').value = existing.notes || '';
            document.getElementById('notePhone').value = existing.seller_phone || '';
        }

        noteModal.style.display = 'block';
    }

    // Close modal handlers
    if (closeModal) {
        closeModal.addEventListener('click', (e) => {
            e.stopPropagation();
            noteModal.style.display = 'none';
        });
    }

    // Click outside modal to close
    window.addEventListener('click', (e) => {
        if (e.target === noteModal) {
            noteModal.style.display = 'none';
        }
    });

    // Escape key to close modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && noteModal.style.display === 'block') {
            noteModal.style.display = 'none';
        }
    });

    // Display Notes (Leads)
    function displayNotes(leads) {
        if (!leads || leads.length === 0) {
            noNotes.style.display = 'block';
            notesContainer.innerHTML = '';
            return;
        }

        noNotes.style.display = 'none';
        notesContainer.innerHTML = '';

        const STATUS_COLORS = {
            'Not Contacted': '#6c757d', // Grey
            'Contacted': '#ffc107',     // Yellow/Orange
            'Successful': '#28a745',    // Green
            'Rejected': '#dc3545'       // Red
        };

        const STATUS_OPTIONS = ['Not Contacted', 'Contacted', 'Successful', 'Rejected'];

        leads.forEach(lead => {
            const card = document.createElement('div');
            card.className = 'car-card';

            // Add captured class if status is Successful
            if (lead.status === 'Successful') {
                card.classList.add('lead-captured');
            }

            const sourceClass = (lead.source || 'unknown').toLowerCase().replace(/\s+/g, '-');
            const imageHtml = lead.image_url
                ? `<img src="${lead.image_url}" alt="${lead.title}">`
                : '<div style="padding: 2rem; text-align: center; color: #999;">No Image</div>';

            // Default to 'Not Contacted' if status is unknown or old
            const currentStatus = STATUS_OPTIONS.includes(lead.status) ? lead.status : 'Not Contacted';
            const statusColor = STATUS_COLORS[currentStatus] || '#6c757d';

            card.innerHTML = `
                <div class="car-image">
                    ${imageHtml}
                </div>
                <div class="car-content">
                    <h4 class="car-title">
                        <a href="${lead.url}" target="_blank" style="text-decoration: none; color: inherit; hover: text-decoration: underline;">${lead.title}</a>
                    </h4>
                    <div class="car-price">${lead.price}</div>
                    ${lead.phone ? `
                    <div class="contact-info" style="margin: 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-weight: 500;">📞 ${lead.phone}</span>
                        <button class="btn-copy" data-phone="${lead.phone}" style="background: none; border: 1px solid #cbd5e1; border-radius: 4px; padding: 2px 6px; cursor: pointer; font-size: 0.8rem;" title="Copy to clipboard">📋 Copy</button>
                    </div>
                    ` : ''}
                    <div class="note-content">${lead.notes || ''}</div>
                    <div class="car-footer">
                        <span class="source-badge ${sourceClass}">${lead.source}</span>
                        <div class="note-actions" style="display: flex; gap: 0.5rem; align-items: center;">
                            <button class="btn-delete" data-id="${lead.id}" style="padding: 0.4rem 0.8rem; font-size: 0.8rem;">Delete</button>
                            <button class="btn-status" data-id="${lead.id}" style="background: ${statusColor}; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; font-weight: bold; flex-grow: 1; cursor: pointer;">${currentStatus}</button>
                        </div>
                    </div>
                </div>
            `;

            // Status toggle handler (Cycle through statuses)
            card.querySelector('.btn-status').addEventListener('click', function () {
                const currentStatus = STATUS_OPTIONS.includes(lead.status) ? lead.status : 'Not Contacted';
                const currentIndex = STATUS_OPTIONS.indexOf(currentStatus);
                const nextIndex = (currentIndex + 1) % STATUS_OPTIONS.length;
                const newStatus = STATUS_OPTIONS[nextIndex];

                updateLeadStatus(lead.id, newStatus);
            });

            // Delete handler
            card.querySelector('.btn-delete').addEventListener('click', function () {
                if (confirm('Delete this lead?')) {
                    deleteLead(lead.id);
                }
            });

            // Copy phone handler
            const copyBtn = card.querySelector('.btn-copy');
            if (copyBtn) {
                copyBtn.addEventListener('click', function () {
                    const phone = this.dataset.phone;
                    navigator.clipboard.writeText(phone).then(() => {
                        const originalText = this.innerHTML;
                        this.innerHTML = '✅ Copied!';
                        setTimeout(() => {
                            this.innerHTML = originalText;
                        }, 2000);
                    }).catch(err => {
                        console.error('Failed to copy text: ', err);
                        alert('Failed to copy phone number');
                    });
                });
            }

            notesContainer.appendChild(card);
        });
    }

    // Update Lead Status
    async function updateLeadStatus(leadId, status) {
        try {
            const response = await fetch(`/api/leads/${leadId}/status`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status })
            });

            if (response.ok) {
                loadNotes(); // Reload to update UI
            } else {
                alert('Error updating status');
            }
        } catch (error) {
            console.error('Error updating status:', error);
            alert('Error updating status');
        }
    }

    // Helper function to update dropdown color
    function updateDropdownColor(dropdown) {
        const STATUS_COLORS = {
            'Not Contacted': { bg: '#6c757d', text: 'white' },
            'Pending': { bg: '#ffc107', text: 'black' },
            'Captured': { bg: '#28a745', text: 'white' },
            'Rejected': { bg: '#dc3545', text: 'white' }
        };

        const status = dropdown.value;
        const colors = STATUS_COLORS[status] || STATUS_COLORS['Not Contacted'];
        dropdown.style.backgroundColor = colors.bg;
        dropdown.style.color = colors.text;
    }

    // Load Notes
    async function loadNotes() {
        const leads = await getLeads();
        displayNotes(leads);
    }

    // Delete Lead
    async function deleteLead(leadId) {
        try {
            const response = await fetch(`/api/leads/${leadId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                loadNotes();
            } else {
                alert('Error deleting lead');
            }
        } catch (error) {
            console.error('Error deleting lead:', error);
            alert('Error deleting lead');
        }
    }
});
