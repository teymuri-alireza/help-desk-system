// Helper function to update the badge
function updateNotificationBadge(trigger, count) {
  // Remove existing badge if present
  const existingBadge = trigger.querySelector('.notification-badge');
  if (existingBadge) {
    existingBadge.remove();
  }

  // Add new badge if count > 0
  if (count > 0) {
    const badge = document.createElement('span');
    badge.className = 'notification-badge';
    badge.textContent = count;
    trigger.appendChild(badge);
  }
}
