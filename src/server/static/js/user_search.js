document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('user-search');
    
    // Check if search input exists
    if (!searchInput) {
        console.warn('User search input not found');
        return;
    }
    
    const userItems = document.querySelectorAll('.user-items');
    
    // Check if there are any user items to search through
    if (userItems.length === 0) {
        console.warn('No user items found to search through');
        return;
    }

    function filterUsers(searchTerm) {
        const term = searchTerm.toLowerCase().trim();
        let visibleCount = 0;
        
        userItems.forEach(user => {
            const userId = user.querySelector('.user-id')?.textContent.toLowerCase() || '';
            const userUsername = user.querySelector('.user-username')?.textContent.toLowerCase() || '';
            const userRole = user.querySelector('.user-role')?.textContent.toLowerCase() || '';
            const userStatus = user.querySelector('.user-status')?.textContent.toLowerCase() || '';
            
            // Check if search term matches any of the fields
            const isMatch = userId.includes(term) || 
                           userUsername.includes(term) || 
                           userRole.includes(term) ||
                           userStatus.includes(term);
            
            if (isMatch) {
                user.classList.remove('hidden');
                visibleCount++;
            } else {
                user.classList.add('hidden');
            }
        });
        
        // Show or hide empty state based on results
        const container = document.querySelector('.user-container');
        if (!container) return;
        
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
        filterUsers(e.target.value);
    });

    // Optional: Clear search on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && document.activeElement === searchInput) {
            searchInput.value = '';
            filterUsers('');
        }
    });
});