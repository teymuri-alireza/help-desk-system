document.addEventListener("DOMContentLoaded", () => {
    loadUsers();
});

async function loadUsers() {
    const loadingEl = document.getElementById("users-loading");
    const manageColHeader = document.getElementById("manage-col-header");
    const titleEl = document.getElementById("users-page-title");
    const subtitleEl = document.getElementById("users-page-subtitle");
    const navbarUsers = document.getElementById("nav-users-admin");
    const navbarExperts = document.getElementById("nav-users-manager");
    const navbarStats = document.getElementById("nav-stats");

    try {
        const meResponse = await fetch("/api/auth/me");

        if (meResponse.status === 401) {
            window.location.href = "/auth";
            return;
        }

        if (!meResponse.ok) {
            showError(loadingEl, "خطا در دریافت اطلاعات کاربر. لطفاً صفحه را مجدداً بارگذاری کنید.");
            return;
        }

        const meData = await meResponse.json();
        const currentUserRole = meData.user_role;
        const isSystemAdmin = currentUserRole === "System Admin";

        if (currentUserRole === "IT Manager") {
            titleEl.textContent = "تمامی کارشناسان سامانه";
            subtitleEl.textContent = "مشاهده و مدیریت تمامی کارشناسان سامانه";
            navbarExperts.style.display = "";
        }

        if (isSystemAdmin) {
            manageColHeader.style.display = "";
            navbarUsers.style.display = "";
            navbarStats.style.display = "";
        }

        const usersResponse = await fetch("/api/users");

        if (usersResponse.status === 401) {
            window.location.href = "/auth";
            return;
        }

        if (usersResponse.status === 403) {
            window.location.href = "/forbidden";
            return;
        }

        if (!usersResponse.ok) {
            showError(loadingEl, "خطا در دریافت لیست کاربران. لطفاً بعداً تلاش کنید.");
            return;
        }

        const usersData = await usersResponse.json();
        renderUsers(usersData.users_list || [], isSystemAdmin);
        loadingEl.style.display = "none";

    } catch (error) {
        showError(loadingEl, "خطا در برقراری ارتباط با سرور. لطفاً اتصال خود را بررسی کنید.");
    }
}

function renderUsers(usersList, isSystemAdmin) {
    const tableBody = document.getElementById("user-container");
    tableBody.innerHTML = "";

    if (usersList.length === 0) {
        const emptyRow = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = isSystemAdmin ? 8 : 7;
        cell.style.textAlign = "center";
        cell.textContent = "هیچ کاربری یافت نشد.";
        emptyRow.appendChild(cell);
        tableBody.appendChild(emptyRow);
        return;
    }

    usersList.forEach((user) => {
        const row = document.createElement("tr");
        row.className = "user-items";

        row.appendChild(buildCell(user.id, "user-id"));
        row.appendChild(buildCell(user.username, "user-username"));
        row.appendChild(buildCell(user.name, "user-name"));
        row.appendChild(buildCell(user.email, "user-email"));
        row.appendChild(buildCell(user.role, "user-role"));
        row.appendChild(buildCell(user.status, "user-status"));
        row.appendChild(buildCell(user.department_name || "-", "user-department"));

        if (isSystemAdmin) {
            const manageCell = document.createElement("td");
            const wrapper = document.createElement("div");
            wrapper.className = "auth-buttons";

            const link = document.createElement("a");
            link.href = `/users/${user.id}`;
            link.className = "btn submit-btn show-ticket";
            link.style.maxWidth = "100%";
            link.textContent = "مدیریت کاربر";

            wrapper.appendChild(link);
            manageCell.appendChild(wrapper);
            row.appendChild(manageCell);
        }

        tableBody.appendChild(row);
    });
}

function buildCell(value, className) {
    const cell = document.createElement("td");
    if (className) {
        cell.className = className;
    }
    cell.textContent = value === null || value === undefined ? "" : String(value);
    return cell;
}

function showError(loadingEl, message) {
    if (loadingEl) {
        loadingEl.innerHTML = "";
        const p = document.createElement("p");
        p.textContent = message;
        loadingEl.appendChild(p);
        loadingEl.style.display = "";
    }
}
