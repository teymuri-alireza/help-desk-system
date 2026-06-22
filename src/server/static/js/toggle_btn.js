// Button to open and close form
// Used in show_ticket.html, and show_user.html
const toggleBtn = document.getElementById('toggleFormBtn');
const editForm = document.getElementById('editForm');

toggleBtn.addEventListener('click', function() {
    if (editForm.style.display === 'none') {
        editForm.style.display = 'block';
        toggleBtn.textContent = 'بستن فرم';
    } else {
        editForm.style.display = 'none';
        toggleBtn.textContent = 'نمایش فرم';
    }
});

// Used in admin_dashboard.html
const adminDashboardToggleBtn = document.getElementById('toggleFormBtn');
const newTicketForm = document.getElementById('newTicketForm');

adminDashboardToggleBtn.addEventListener('click', function() {
    if (newTicketForm.style.display === 'none') {
        newTicketForm.style.display = 'block';
        adminDashboardToggleBtn.textContent = 'بستن فرم';
    } else {
        newTicketForm.style.display = 'none';
        adminDashboardToggleBtn.textContent = 'نمایش فرم';
    }
});

const toggleUserFormBtn = document.getElementById('toggleUserFormBtn');
const newUserForm = document.getElementById('newUserForm');

toggleUserFormBtn.addEventListener('click', function() {
    if (newUserForm.style.display === 'none') {
        newUserForm.style.display = 'block';
        toggleUserFormBtn.textContent = 'بستن فرم';
    } else {
        newUserForm.style.display = 'none';
        toggleUserFormBtn.textContent = 'نمایش فرم';
    }
});
