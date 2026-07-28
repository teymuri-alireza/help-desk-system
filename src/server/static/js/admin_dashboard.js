document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
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
        const isSystemAdmin = data.users_list !== undefined;

        renderMetrics(data, isSystemAdmin);
        renderTickets(data.tickets_list || [], isSystemAdmin);

        if (isSystemAdmin) {
            renderUsers(data.users_list || []);
            setupNewUserForm(data.roles || [], data.departments || []);
            document.getElementById("new-user-section").style.display = "";
            document.getElementById("recent-users-section").style.display = "";
        }

        loadingEl.style.display = "none";
        contentEl.style.display = "";

    } catch (error) {
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

function renderTickets(ticketsList, isSystemAdmin) {
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

        const creatorCell = document.createElement("td");
        if (isSystemAdmin) {
            const link = document.createElement("a");
            link.href = `/users/${ticket.creator_id}`;
            link.textContent = ticket.creator_username;
            creatorCell.appendChild(link);
        } else {
            creatorCell.textContent = ticket.creator_username;
        }
        row.appendChild(creatorCell);

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

function renderUsers(usersList) {
    const body = document.getElementById("recent-users-body");
    body.innerHTML = "";

    if (usersList.length === 0) {
        body.appendChild(buildEmptyRow(6, "کاربری یافت نشد."));
        return;
    }

    usersList.forEach((user) => {
        const row = document.createElement("tr");

        row.appendChild(buildCell(user.id));
        row.appendChild(buildCell(user.username));
        row.appendChild(buildCell(user.name));
        row.appendChild(buildCell(user.email));
        row.appendChild(buildCell(user.role_fa));

        const actionCell = document.createElement("td");
        const viewLink = document.createElement("a");
        viewLink.href = `/users/${user.id}`;
        viewLink.className = "btn-small btn submit-btn";
        viewLink.textContent = "مشاهده";
        actionCell.appendChild(viewLink);
        row.appendChild(actionCell);

        body.appendChild(row);
    });
}

function setupNewUserForm(roles, departments) {
    const roleSelect = document.getElementById("new-user-role");
    roleSelect.innerHTML = "";
    roles.forEach((r) => {
        const option = document.createElement("option");
        option.value = r.name;
        option.textContent = r.fa;
        roleSelect.appendChild(option);
    });

    const departmentSelect = document.getElementById("new-user-department-select");
    departmentSelect.innerHTML = '<option value="">-- دپارتمان را انتخاب کنید --</option>';
    departments.forEach((d) => {
        const option = document.createElement("option");
        option.value = d.id;
        option.textContent = d.name;
        departmentSelect.appendChild(option);
    });

    const departmentField = document.getElementById("new-user-department");

    function toggleDepartmentField() {
        const isExpert = roleSelect.value === "IT_EXPERT";
        departmentField.style.display = isExpert ? "" : "none";
        if (isExpert) {
            departmentSelect.setAttribute("required", "required");
        } else {
            departmentSelect.removeAttribute("required");
            departmentSelect.value = "";
        }
    }

    roleSelect.addEventListener("change", toggleDepartmentField);
    toggleDepartmentField();

    document.getElementById("newUserForm").addEventListener("submit", handleNewUserSubmit);
}

async function handleNewUserSubmit(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const alertEl = document.getElementById("user-flash-alert");

    try {
        const response = await fetch("/api/users", {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            showFormAlert(alertEl, "کاربر با موفقیت ثبت شد", "alert-success");
            form.reset();
            document.getElementById("new-user-department").style.display = "none";
            await refreshDashboardData();
            return;
        }

        if (response.status === 409) {
            showFormAlert(alertEl, "این نام کاربری قبلا استفاده شده است.", "alert-danger");
            return;
        }

        if (response.status === 400) {
            const errorData = await response.json().catch(() => null);
            const message = (errorData && errorData.detail)
                ? errorData.detail
                : "دپارتمان برای کارشناس فناوری اطلاعات الزامی است.";
            showFormAlert(alertEl, message, "alert-danger");
            return;
        }

        if (response.status === 403) {
            window.location.href = "/forbidden";
            return;
        }

        showFormAlert(alertEl, "خطا در ثبت کاربر. لطفاً بعداً تلاش کنید.", "alert-danger");

    } catch (error) {
        showFormAlert(alertEl, "خطا در برقراری ارتباط با سرور.", "alert-danger");
    }
}

async function refreshDashboardData() {
    try {
        const response = await fetch("/api/dashboard");
        if (!response.ok) return;

        const data = await response.json();
        const isSystemAdmin = data.users_list !== undefined;

        renderMetrics(data, isSystemAdmin);
        renderTickets(data.tickets_list || [], isSystemAdmin);

        if (isSystemAdmin) {
            renderUsers(data.users_list || []);
        }
    } catch (error) {
        // The user was already created successfully (confirmed by the POST response);
        // a refresh failure here just means the tables won't update until the next reload.
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
