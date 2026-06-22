const searchInput = document.getElementById('ticket-search');
const ticketItems = document.querySelectorAll('.ticket-item');

function filterTickets(searchTerm) {
    const term = searchTerm.toLowerCase().trim();
    let visibleCount = 0;
    
    ticketItems.forEach(ticket => {
        // Get ticket ID, title, and description
        const ticketId = ticket.querySelector('.ticket-id')?.textContent.toLowerCase() || '';
        const ticketTitle = ticket.querySelector('h3')?.textContent.toLowerCase() || '';
        const ticketDescription = ticket.querySelector('.ticket-description')?.textContent.toLowerCase() || '';
        
        // Check if search term matches any of the fields
        const isMatch = ticketId.includes(term) || 
                       ticketTitle.includes(term) || 
                       ticketDescription.includes(term);
        
        if (isMatch) {
            ticket.classList.remove('hidden');
            visibleCount++;
        } else {
            ticket.classList.add('hidden');
        }
    });
    
    // Show or hide empty state based on results
    const container = document.querySelector('.tickets-container');
    let emptyMessage = container.querySelector('.search-empty-state');
    
    if (visibleCount === 0 && term) {
        if (!emptyMessage) {
            emptyMessage = document.createElement('div');
            emptyMessage.className = 'empty-state search-empty-state';
            emptyMessage.textContent = 'نتیجه‌ای برای جستجو پیدا نشد';
            container.appendChild(emptyMessage);
        }
        emptyMessage.style.display = 'block';
    } else if (emptyMessage) {
        emptyMessage.style.display = 'none';
    }
}

// Add event listener for search input
searchInput.addEventListener('input', (e) => {
    filterTickets(e.target.value);
});

// Optional: Clear search on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && document.activeElement === searchInput) {
        searchInput.value = '';
        filterTickets('');
    }
});