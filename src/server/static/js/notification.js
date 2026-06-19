async function loadNotifications() {
  const notificationsMenu = document.getElementById('notifications-menu');
  const notificationsTrigger = document.querySelector('.notifications-trigger');

  try {
    const response = await fetch('/notifications');

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const notifications = Array.isArray(data.response)
      ? data.response
      : [];

    // Update notification count badge
    const countNotifications = data.count_notifications || 0;
    updateNotificationBadge(notificationsTrigger, countNotifications);

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
      const response = await fetch('/notifications', {
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

document.addEventListener("DOMContentLoaded", () => {
    const alert = document.getElementById("flash-alert");
    const userAlert = document.getElementById("user-flash-alert");

    if (alert) {
        setTimeout(() => {
            alert.style.opacity = "0";

            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 3500);
    }

    if (userAlert) {
        setTimeout(() => {
            userAlert.style.opacity = "0";

            setTimeout(() => {
                userAlert.remove();
            }, 500);
        }, 3500);
    }
});
