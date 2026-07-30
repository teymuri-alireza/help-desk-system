async function loadNotifications() {
  const notificationsMenu = document.getElementById('notifications-menu');
  const notificationsTrigger = document.querySelector('.notifications-trigger');

  try {
    const response = await fetch('/api/notifications');

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const notifications = Array.isArray(data.notifications)
      ? data.notifications
      : [];

    // Update notification count badge
    const unreadCount = data.unread_count || 0;
    updateNotificationBadge(notificationsTrigger, unreadCount);

    notificationsMenu.replaceChildren();

    if (notifications.length === 0) {
      // Show "No notifications" message
      const emptyMessage = document.createElement('div');
      emptyMessage.className = 'notification-empty';
      emptyMessage.textContent = 'هیچ اعلان جدیدی وجود ندارد';
      notificationsMenu.appendChild(emptyMessage);
    } else {

      for (const notification of notifications) {
        const item = document.createElement('div');
        item.className = 'notification-item';

        const title = document.createElement('div');
        title.className = 'notification-title';
        title.textContent = notification.title ?? '';
        title.style.cursor = 'pointer';
        title.style.textDecoration = 'underline';
        title.onclick = () => {
            window.open(notification.url, '_blank');
        };

        const text = document.createElement('div');
        text.className = 'notification-text';
        text.textContent = notification.text ?? '';

        const button = document.createElement('button');
        button.className = 'notification-btn';
        button.dataset.id = notification.id;
        button.textContent = 'مشاهده شد';

        item.append(title, text, button);
        notificationsMenu.appendChild(item);
      }
    }
  } catch (error) {
    console.error('Failed to load notifications:', error);
  }
}

document
  .getElementById('notifications-menu')
  .addEventListener('click', async (e) => {
    const btn = e.target.closest('.notification-btn');
    if (!btn) return;

    btn.disabled = true;

    try {
      const response = await fetch('/api/notifications', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          notification_id: btn.dataset.id,
          is_read: true
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      // Refresh the UI
      loadNotifications()

    } catch (error) {
      console.error('Failed to update notification:', error);
      btn.disabled = false;
    }
  });

loadNotifications();

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
