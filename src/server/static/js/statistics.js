document.addEventListener("DOMContentLoaded", () => {
    loadStatistics();
});

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

async function loadStatistics() {
    const loadingEl = document.getElementById("stats-loading");
    const contentEl = document.getElementById("stats-content");

    try {
        const meResponse = await fetch("/api/auth/me");

        if (meResponse.status === 401) {
            window.location.href = "/auth";
            return;
        }

        if (!meResponse.ok) {
            showLoadingError(loadingEl, "خطا در دریافت اطلاعات کاربر. لطفاً صفحه را مجدداً بارگذاری کنید.");
            return;
        }

        const meData = await meResponse.json();
        const userRole = meData.user_role;
        applyNavForRole(userRole);

        const isSystemAdmin = userRole === "System Admin";

        const roleDataEl = document.getElementById("user-role-data");
        if (roleDataEl) {
            roleDataEl.dataset.user_role = userRole;
        }

        const statsResponse = await fetch("/api/dashboard/stats");

        if (statsResponse.status === 401) {
            window.location.href = "/auth";
            return;
        }

        if (statsResponse.status === 403) {
            window.location.href = "/forbidden";
            return;
        }

        if (!statsResponse.ok) {
            showLoadingError(loadingEl, "خطا در دریافت آمار سامانه. لطفاً بعداً تلاش کنید.");
            return;
        }

        const data = await statsResponse.json();

        renderMetrics(data, isSystemAdmin);
        renderCharts(isSystemAdmin);

        if (isSystemAdmin) {
            try {
                document.getElementById("users-charts-btn").style.display = "";
            } 
            catch {}
        }

        loadingEl.style.display = "none";
        contentEl.style.display = "";

    } catch (error) {
        console.log(error)
        showLoadingError(loadingEl, "خطا در برقراری ارتباط با سرور. لطفاً اتصال خود را بررسی کنید.");
    }
}

function renderMetrics(data, isSystemAdmin) {
    if (isSystemAdmin) {
        document.getElementById("users-metric-card").style.display = "";
        document.getElementById("users-metric-value").textContent =
            `${data.all_users_count} / ${data.active_users_count}`;
    }

    document.getElementById("tickets-metric-value").textContent =
        `${data.all_tickets_count} / ${data.active_tickets_count}`;
    document.getElementById("unassigned-metric-value").textContent = data.not_assigned_tickets;
    document.getElementById("recent-metric-value").textContent = data.last_created;
}

function renderCharts(isSystemAdmin) {
    // Cache-bust so freshly regenerated charts (triggered server-side by
    // GET /api/dashboard/stats) don't show a stale cached image.
    const cacheBuster = Date.now();

    if (isSystemAdmin) {
        document.getElementById("users-charts").style.display = "";
        document.getElementById("user-role-chart").src = `/contents/charts/user_role.png?t=${cacheBuster}`;
    }

    document.getElementById("ticket-status-chart").src = `/contents/charts/ticket_status.png?t=${cacheBuster}`;
    document.getElementById("ticket-category-chart").src = `/contents/charts/ticket_category.png?t=${cacheBuster}`;
    document.getElementById("ticket-department-chart").src = `/contents/charts/ticket_department.png?t=${cacheBuster}`;
    document.getElementById("it-experts-performance-chart").src = `/contents/charts/it_experts_performance.png?t=${cacheBuster}`;
}

function showLoadingError(loadingEl, message) {
    loadingEl.innerHTML = "";
    const p = document.createElement("p");
    p.textContent = message;
    loadingEl.appendChild(p);
}
