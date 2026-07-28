document.addEventListener("DOMContentLoaded", () => {
    loadUserProfile();
    initEditFormHandler();
    initToggleEditFormButton();
});

function initToggleEditFormButton() {
    const toggleBtn = document.getElementById("toggleEditFormBtn");
    const form = document.getElementById("editForm");

    if (!toggleBtn || !form) return;

    toggleBtn.addEventListener("click", () => {
        const isHidden = form.style.display === "none";
        form.style.display = isHidden ? "block" : "none";
        toggleBtn.textContent = isHidden ? "بستن فرم" : "نمایش فرم";
    });
}

function getUserIdFromPath() {
    const parts = window.location.pathname.split("/").filter(Boolean);
    return parts[parts.length - 1];
}

async function loadUserProfile() {
    const profileContainer = document.getElementById("user-profile-container");
    const editSection = document.getElementById("edit-user-section");
    const userId = getUserIdFromPath();

    try {
        const meResponse = await fetch("/api/auth/me");

        if (meResponse.status === 401) {
            window.location.href = "/auth";
            return;
        }

        if (!meResponse.ok) {
            showProfileMessage(profileContainer, "خطا در دریافت اطلاعات کاربر جاری.");
            return;
        }

        const meData = await meResponse.json();
        const isSystemAdmin = meData.user_role === "System Admin";

        applyCurrentUserRole(meData.user_role);

        const userResponse = await fetch(`/api/users/${userId}`);

        if (userResponse.status === 401) {
            window.location.href = "/auth";
            return;
        }

        if (userResponse.status === 403) {
            window.location.href = "/forbidden";
            return;
        }

        if (userResponse.status === 404) {
            showProfileMessage(profileContainer, "کاربر مورد نظر یافت نشد");
            return;
        }

        if (!userResponse.ok) {
            showProfileMessage(profileContainer, "خطا در دریافت اطلاعات کاربر. لطفاً بعداً تلاش کنید.");
            return;
        }

        const data = await userResponse.json();
        renderProfile(profileContainer, data.user, isSystemAdmin);
        setupEditForm(editSection, data, isSystemAdmin, userId);

    } catch (error) {
        showProfileMessage(profileContainer, "خطا در برقراری ارتباط با سرور. لطفاً اتصال خود را بررسی کنید.");
    }
}

function applyCurrentUserRole(currentUserRole) {
    const ticketsNavLink = document.getElementById("nav-tickets");
    if (ticketsNavLink && currentUserRole === "IT Expert") {
        ticketsNavLink.textContent = "تمامی تیکت‌های کارشناس";
    }
    if (currentUserRole === "System Admin") {
        const adminNavLink = document.getElementById("nav-users-admin");
        if (adminNavLink) {
            adminNavLink.style.display = "";
        }
    }
}

function renderProfile(container, user, isSystemAdmin) {
    container.innerHTML = "";

    const item = document.createElement("div");
    item.className = "ticket-item";

    const meta = document.createElement("div");
    meta.className = "ticket-meta";

    const info = document.createElement("div");
    info.className = "ticket-info";

    info.appendChild(makeParagraph(`#${user.id}`, "ticket-id"));
    info.appendChild(makeHeading(user.name));
    info.appendChild(makeLabeledParagraph("نام کاربری:", user.username));
    info.appendChild(makeLabeledParagraph("ایمیل:", user.email));
    info.appendChild(makeLabeledParagraph("نقش:", user.role_fa, "role"));
    info.appendChild(makeLabeledParagraph("وضعیت:", user.status));

    if (user.role_en === "IT Expert") {
        info.appendChild(makeLabeledParagraph("دپارتمان مربوطه کارشناس:", user.department_name || "-"));
    }

    const createdP = makeLabeledParagraph("تاریخ عضویت:", formatCreatedAt(user.created_at));
    createdP.classList.add("ticket-created");
    info.appendChild(createdP);

    meta.appendChild(info);
    item.appendChild(meta);
    container.appendChild(item);

    if (isSystemAdmin) {
        const actions = document.createElement("div");
        actions.className = "auth-buttons";

        const deleteBtn = document.createElement("button");
        deleteBtn.className = "btn submit-btn show-ticket delete-user-btn";
        deleteBtn.style.backgroundColor = "tomato";
        deleteBtn.dataset.userId = user.id;
        deleteBtn.textContent = "Delete";
        deleteBtn.addEventListener("click", () => handleDelete(user.id));

        actions.appendChild(deleteBtn);
        container.appendChild(actions);
    }
}

function setupEditForm(editSection, data, isSystemAdmin, userId) {
    const { user, departments, roles, status } = data;

    editSection.style.display = "";

    const form = document.getElementById("editForm");
    form.action = `/api/users/${userId}`;

    document.getElementById("edit-name").value = user.name;

    const adminFields = document.getElementById("admin-only-fields");
    const usernameInput = document.getElementById("edit-username");
    const emailInput = document.getElementById("edit-email");
    const roleSelect = document.getElementById("edit-role");
    const statusSelect = document.getElementById("edit-status");
    const departmentField = document.getElementById("department-field");
    const departmentSelect = document.getElementById("edit-department");

    if (!isSystemAdmin) {
        adminFields.style.display = "none";
        // A hidden field can't show its validation bubble, so the browser
        // silently blocks submission if it's still marked required. Strip
        // "required" from everything inside the hidden admin-only block.
        usernameInput.removeAttribute("required");
        emailInput.removeAttribute("required");
        roleSelect.removeAttribute("required");
        statusSelect.removeAttribute("required");
        departmentSelect.removeAttribute("required");
        return;
    }

    adminFields.style.display = "";
    usernameInput.setAttribute("required", "required");
    emailInput.setAttribute("required", "required");
    roleSelect.setAttribute("required", "required");
    statusSelect.setAttribute("required", "required");

    usernameInput.value = user.username;
    emailInput.value = user.email;

    roleSelect.innerHTML = "";
    roles.forEach((r) => {
        const option = document.createElement("option");
        option.value = r.name;
        option.textContent = r.fa;
        if (r.name === user.role_name) {
            option.selected = true;
        }
        roleSelect.appendChild(option);
    });

    statusSelect.innerHTML = "";
    status.forEach((s) => {
        const option = document.createElement("option");
        option.value = s.name;
        option.textContent = s.fa;
        if (s.name === user.status_name) {
            option.selected = true;
        }
        statusSelect.appendChild(option);
    });

    departmentSelect.innerHTML = '<option value="">-- دپارتمان را انتخاب کنید --</option>';
    departments.forEach((d) => {
        const option = document.createElement("option");
        option.value = d.id;
        option.textContent = d.name;
        if (user.department_id !== null && String(d.id) === String(user.department_id)) {
            option.selected = true;
        }
        departmentSelect.appendChild(option);
    });

    // Keep the department field (and its required-ness) in sync if the
    // admin changes the role mid-edit, not just on initial load.
    function toggleDepartmentField() {
        const isExpert = roleSelect.value === "IT_EXPERT";
        departmentField.style.display = isExpert ? "" : "none";
        if (isExpert) {
            departmentSelect.setAttribute("required", "required");
        } else {
            departmentSelect.removeAttribute("required");
        }
    }

    roleSelect.addEventListener("change", toggleDepartmentField);
    toggleDepartmentField();
}

function initEditFormHandler() {
    const form = document.getElementById("editForm");

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const formData = new FormData(form);

        try {
            const response = await fetch(form.action, {
                method: "PATCH",
                body: formData,
                credentials: "include"
            });

            if (response.ok) {
                localStorage.setItem("update_user_flash_message", "successful");
                window.location.reload();
            } else if (response.status === 403) {
                window.location.href = "/forbidden";
            } else {
                const error = await response.text();
                alert("Error: " + error);
            }
        } catch (err) {
            console.error(err);
            alert("An error occurred.");
        }
    });
}

async function handleDelete(userId) {
    if (!confirm("Are you sure you want to delete this user?")) {
        return;
    }

    try {
        const response = await fetch(`/api/users/${userId}`, {
            method: "DELETE"
        });

        if (response.ok) {
            window.location.href = "/users";
        } else {
            alert("Failed to delete user.");
        }
    } catch (err) {
        console.error(err);
        alert("An error occurred.");
    }
}

function makeHeading(text) {
    const h3 = document.createElement("h3");
    h3.textContent = text;
    return h3;
}

function makeParagraph(text, className) {
    const p = document.createElement("p");
    if (className) p.className = className;
    p.textContent = text;
    return p;
}

function makeLabeledParagraph(label, value, spanClass) {
    const p = document.createElement("p");
    const strong = document.createElement("strong");
    strong.textContent = label;
    p.appendChild(strong);

    if (spanClass) {
        const span = document.createElement("span");
        span.className = spanClass;
        span.textContent = ` ${value}`;
        p.appendChild(span);
    } else {
        p.appendChild(document.createTextNode(` ${value}`));
    }

    return p;
}

function formatCreatedAt(isoString) {
    if (!isoString) return "";
    return isoString.replace("T", " ").split(".")[0];
}

function showProfileMessage(container, message) {
    container.innerHTML = "";
    const div = document.createElement("div");
    const p = document.createElement("p");
    p.className = "ticket-description";
    p.textContent = message;
    div.appendChild(p);
    container.appendChild(div);
}
