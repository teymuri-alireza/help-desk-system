document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
    initNewTicketForm();
});

async function loadDashboard() {
    const loadingEl = document.getElementById("dashboard-loading");
    const contentEl = document.getElementById("dashboard-content");

    try {
        const response = await fetch("/api/dashboard");

        if (response.status === 401) {
            window.location.href = "/auth";
            return;
        }

        if (!response.ok) {
            showLoadingError(loadingEl, "خطا در دریافت اطلاعات داشبورد. لطفاً بعداً تلاش کنید.");
            return;
        }

        const data = await response.json();

        renderMetrics(data);
        renderTickets(data.tickets_list || []);

        loadingEl.style.display = "none";
        contentEl.style.display = "";

    } catch (error) {
        showLoadingError(loadingEl, "خطا در برقراری ارتباط با سرور. لطفاً اتصال خود را بررسی کنید.");
    }
}

function renderMetrics(data) {
    document.getElementById("assigned-metric-value").textContent = data.assigned_tickets;
    document.getElementById("open-metric-value").textContent = data.open_tickets;
    document.getElementById("resolved-metric-value").textContent = data.resolved_tickets;
}

function renderTickets(ticketsList) {
    const body = document.getElementById("recent-tickets-body");
    body.innerHTML = "";

    if (ticketsList.length === 0) {
        body.appendChild(buildEmptyRow(6, "تیکتی یافت نشد."));
        return;
    }

    ticketsList.forEach((ticket) => {
        const row = document.createElement("tr");

        row.appendChild(buildCell(`#${ticket.id}`));

        const titleCell = document.createElement("td");
        const strong = document.createElement("strong");
        strong.textContent = ticket.title;
        titleCell.appendChild(strong);
        row.appendChild(titleCell);

        const statusCell = document.createElement("td");
        const badge = document.createElement("span");
        badge.className = `status-badge status-${ticket.status_name}`;
        badge.textContent = ticket.status_fa;
        statusCell.appendChild(badge);
        row.appendChild(statusCell);

        row.appendChild(buildCell(ticket.creator_username));
        row.appendChild(buildCell(formatDate(ticket.created_at)));

        const actionCell = document.createElement("td");
        const viewLink = document.createElement("a");
        viewLink.href = `/tickets/${ticket.id}`;
        viewLink.className = "btn-small btn submit-btn";
        viewLink.textContent = "مشاهده";
        actionCell.appendChild(viewLink);
        row.appendChild(actionCell);

        body.appendChild(row);
    });
}

function initNewTicketForm() {
    const form = document.getElementById("newTicketForm");
    form.addEventListener("submit", handleNewTicketSubmit);
}

async function handleNewTicketSubmit(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const alertEl = document.getElementById("ticket-flash-alert");

    try {
        const response = await fetch("/api/tickets", {
            method: "POST",
            body: formData
        });

        if (response.status === 401) {
            window.location.href = "/auth";
            return;
        }

        if (response.status === 403) {
            window.location.href = "/forbidden";
            return;
        }

        if (response.ok) {
            showFormAlert(alertEl, "تیکت با موفقیت ثبت شد", "alert-success");
            form.reset();
            await refreshDashboardData();
            return;
        }

        const message = await extractErrorMessage(response);
        showFormAlert(alertEl, message, "alert-danger");

    } catch (error) {
        showFormAlert(alertEl, "خطا در برقراری ارتباط با سرور.", "alert-danger");
    }
}

async function extractErrorMessage(response) {
    try {
        const data = await response.clone().json();
        if (data && data.detail) return data.detail;
    } catch (error) {
        // Response body wasn't JSON; fall through to text.
    }

    try {
        const text = await response.text();
        if (text) return text;
    } catch (error) {
        // Ignore and use the generic fallback below.
    }

    return "خطا در ثبت تیکت. لطفاً بعداً تلاش کنید.";
}

async function refreshDashboardData() {
    try {
        const response = await fetch("/api/dashboard");
        if (!response.ok) return;

        const data = await response.json();
        renderMetrics(data);
        renderTickets(data.tickets_list || []);
    } catch (error) {
        // The ticket was already created successfully (confirmed by the POST response);
        // a refresh failure here just means the table won't update until the next reload.
    }
}

function buildCell(value) {
    const cell = document.createElement("td");
    cell.textContent = value === null || value === undefined ? "" : String(value);
    return cell;
}

function buildEmptyRow(colSpan, message) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = colSpan;
    cell.style.textAlign = "center";
    cell.textContent = message;
    row.appendChild(cell);
    return row;
}

function formatDate(isoString) {
    if (!isoString) return "";
    return isoString.replace("T", " ").split(".")[0];
}

function showFormAlert(alertEl, message, className) {
    alertEl.className = `alert ${className}`;
    alertEl.textContent = message;
    alertEl.style.display = "";
    alertEl.style.opacity = "1";

    setTimeout(() => {
        alertEl.style.opacity = "0";
        setTimeout(() => {
            alertEl.style.display = "none";
            alertEl.style.opacity = "1";
        }, 500);
    }, 3500);
}

function showLoadingError(loadingEl, message) {
    loadingEl.innerHTML = "";
    const p = document.createElement("p");
    p.textContent = message;
    loadingEl.appendChild(p);
}
