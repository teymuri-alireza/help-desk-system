document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('user-search');

    // Check if search input exists
    if (!searchInput) {
        console.warn('User search input not found');
        return;
    }

    // Note: users_list.js populates the table asynchronously (it fetches
    // /api/users after this handler runs), so `.user-items` rows do not
    // exist yet at this point. We intentionally do NOT bail out here, and
    // we re-query the rows fresh inside filterUsers() on every call rather
    // than caching a NodeList now, so the search works against whatever
    // rows are in the table at the time the user actually types.

    function filterUsers(searchTerm) {
        const term = searchTerm.toLowerCase().trim();
        const userItems = document.querySelectorAll('.user-items');
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
        const emptyMessage = document.querySelector('.search-empty-state');
        if (!emptyMessage) return;

        if (visibleCount === 0 && term) {
            emptyMessage.textContent = 'نتیجه‌ای برای جستجو پیدا نشد';
            emptyMessage.style.display = 'block';
        } else {
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