document.addEventListener("DOMContentLoaded", loadNotifications);

async function loadNotifications() {
    const container = document.getElementById("notifications-list");

    function applyNavForRole(role) {
        if (role === "System Admin") {
            const el = document.getElementById("nav-users-admin");
            if (el) el.style.display = "";
        } else if (role === "IT Manager") {
            const el = document.getElementById("nav-users-manager");
            if (el) el.style.display = "";
        }

        if (role === "System Admin" || role === "IT Manager") {
            const stats = document.getElementById("nav-stats");
            if (stats) stats.style.display = "";
        }

        const ticketsNav = document.getElementById("nav-tickets");
        if (ticketsNav && role === "IT Expert") {
            ticketsNav.textContent = "تمامی تیکت‌های کارشناس";
        }
    }

    try {
        let role = null;

        try {
            const meRes = await fetch("/api/auth/me");
            if (!meRes.ok) {
                window.location.href = "/auth";
                return;
            }
            const me = await meRes.json();
            role = me.user_role;
            applyNavForRole(role);
        } catch (err) {
            window.location.href = "/auth";
            return;
        }

        const response = await fetch("/api/notifications/all");

        if (response.status === 401) {
            window.location.href = "/auth";
            return;
        }

        if (!response.ok) {
            throw new Error("Failed to load notifications.");
        }

        const data = await response.json();

        container.innerHTML = "";

        if (data.notifications.length === 0) {
            container.innerHTML = `
                <p class="empty-notifications">
                    هیچ اعلانی وجود ندارد.
                </p>
            `;
            return;
        }

        data.notifications.forEach(notification => {
            const article = document.createElement("article");

            article.className = `notification-card ${notification.is_read ? "" : "unread"}`;

            article.innerHTML = `
                <div id="${notification.id}" class="notification-top">
                    <span class="notification-date">
                        ایجاد شده در ${formatDate(notification.created_at)}
                    </span>
                </div>

                <h3>${notification.title}</h3>

                <p>${notification.text}</p>

                <div class="notification-btn-status">

                    <div class="notification-status ${notification.is_read ? "read" : "unread"}">
                        ${notification.is_read ? "خوانده شده" : "خوانده‌نشده"}
                    </div>

                    <a
                        href="${notification.url}"
                        class="notification-btn btn submit-btn show-ticket"
                        style="max-width:20%;"
                    >
                        مشاهده جزییات بیشتر
                    </a>

                    ${
                        !notification.is_read
                        ? `
                        <button
                            class="notification-btn mark-read-btn"
                            data-id="${notification.id}"
                            style="max-width:20%;"
                        >
                            مشاهده شد
                        </button>
                        `
                        : ""
                    }

                </div>
            `;

            container.appendChild(article);
        });

        registerReadButtons();

    } catch (err) {
        console.error(err);

        container.innerHTML = `
            <p class="error">
                خطا در دریافت اعلان‌ها.
            </p>
        `;
    }
}

function registerReadButtons() {

    document.querySelectorAll(".mark-read-btn").forEach(button => {
        button.addEventListener("click", async () => {

            const notificationId = Number(button.dataset.id);
            try {
                const response = await fetch("/api/notifications", {
                    method: "PATCH",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        notification_id: notificationId,
                        is_read: true
                    })
                });
                if (!response.ok) {
                    throw new Error();
                }
                loadNotifications();
            } catch {
                alert("خطا در بروزرسانی اعلان.");
            }
        });
    });
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString("fa-IR");
}
