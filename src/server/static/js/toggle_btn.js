// Button to open and close form
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
