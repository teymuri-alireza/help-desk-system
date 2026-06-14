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

    if (!alert) return;

    setTimeout(() => {
        alert.style.opacity = "0";

        setTimeout(() => {
            alert.remove();
        }, 500);
    }, 3500);
});

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