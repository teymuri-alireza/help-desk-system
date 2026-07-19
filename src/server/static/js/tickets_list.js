(function () {
    const STATUS_ALERT_CLASS = {
        NEW: "alert-success",
        IN_PROGRESS: "alert-warning",
        WAITING_FOR_USER: "alert-warning",
        RESOLVED: "alert-danger",
        CLOSED: "alert-danger",
    };

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

    function buildTicketItem(ticket, role) {
        const item = document.createElement("div");
        item.className = "ticket-item";

        const alertClass = STATUS_ALERT_CLASS[ticket.status_name] || "";

        const creatorHtml =
            role === "System Admin"
                ? `<a href="/users/${ticket.creator_id}">${ticket.creator_username}</a>`
                : `<a>${ticket.creator_username}</a>`;

        item.innerHTML = `
            <div class="ticket-meta">
                <div class="ticket-info">
                    <p class="ticket-id">#${ticket.id}</p>
                    <h3>عنوان: ${ticket.title}</h3>
                </div>
                <span class="status alert ${alertClass}">
                    وضعیت: ${ticket.status_fa}
                </span>
            </div>
            <p class="ticket-description">توضیحات: ${ticket.description}</p>
            <div class="set-items-space-between">
                <p class="ticket-created">ثبت شده در: ${ticket.created_at}</p>
                <p class="ticket-created">کاربر ایجاد کننده: ${creatorHtml}</p>
            </div>
            <div class="auth-buttons">
                <a href="/tickets/${ticket.id}" class="btn submit-btn show-ticket">مشاهده جزییات تیکت</a>
            </div>
        `;

        return item;
    }

    function renderTickets(ticketsList, role) {
        const container = document.getElementById("tickets-container");
        container.innerHTML = "";

        if (!ticketsList || ticketsList.length === 0) {
            const empty = document.createElement("div");
            empty.className = "empty-state";
            empty.innerHTML = "<p>هیچ تیکتی ثبت نشده است</p>";
            container.appendChild(empty);
            return;
        }

        ticketsList.forEach((ticket) => {
            container.appendChild(buildTicketItem(ticket, role));
        });
    }

    function renderError() {
        const container = document.getElementById("tickets-container");
        container.innerHTML = '<div class="empty-state"><p>خطا در دریافت لیست تیکت‌ها</p></div>';
    }

    async function init() {
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

        try {
            const ticketsRes = await fetch("/api/tickets");
            if (!ticketsRes.ok) {
                renderError();
                return;
            }
            const data = await ticketsRes.json();
            renderTickets(data.tickets_list, role);
        } catch (err) {
            renderError();
        }
    }

    document.addEventListener("DOMContentLoaded", init);
})();
