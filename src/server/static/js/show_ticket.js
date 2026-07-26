/*
 * show_ticket.js
 *
 * Fetches a single ticket + the current user and renders everything that
 * show_ticket.html used to get from Jinja context. Mirrors the pattern used
 * in show_user.js (fetch -> render into a container -> wire up events).
 *
 * ASSUMPTIONS ABOUT THE API (I didn't have your api/tickets.py, so verify
 * these against what you actually built and adjust the ENDPOINTS block
 * below if the paths/shape differ):
 *
 *   GET  /api/tickets/{id}
 *        -> {
 *             id, title, description, created_at, satisfaction_rating,
 *             status: {name, fa}, priority: {name, fa},
 *             attachment: {file_name} | null,
 *             creator: {id}, creator_id,
 *             assignee: {id, username} | null, assigned_to,
 *             category: {id, name} | null, category_id,
 *             department: {id, name} | null, department_id,
 *             edit_options: {
 *               statuses: [{name, fa}], priorities: [{name, fa}],
 *               it_experts: [{id, name}], categories: [{id, name}],
 *               departments: [{id, name}]
 *             }
 *           }
 *        404 -> ticket not found, 403 -> forbidden
 *
 *   GET   /api/auth/me                       -> {user_id, user_username, user_role}  (already exists)
 *   PATCH /api/tickets/{id}                  -> update ticket (form-data, same fields as old form)
 *   POST  /api/tickets/{id}/responses        -> new response (handled by responses.js)
 *   POST  /api/tickets/{id}/remove_assignee
 *   GET   /api/tickets/{id}/assign/preview   -> {suggested_expert_name}
 *   POST  /api/tickets/{id}/assign
 *   POST  /api/tickets/{id}/rate             -> {rating}
 *   PATCH /api/tickets/{id}/reopen
 *
 * If your real endpoints differ, this file only needs the ENDPOINTS object
 * and the field names inside the render functions touched.
 */

const ENDPOINTS = {
    me: "/api/auth/me",
    ticket: (id) => `/api/tickets/${id}`,
    removeAssignee: (id) => `/api/tickets/${id}/remove_assignee`,
    assignPreview: (id) => `/api/tickets/${id}/assign/preview`,
    assign: (id) => `/api/tickets/${id}/assign`,
    rate: (id) => `/api/tickets/${id}/rate`,
    reopen: (id) => `/api/tickets/${id}/reopen`,
};

const STATUS_ALERT_CLASS = {
    NEW: "alert-success",
    IN_PROGRESS: "alert-warning",
    WAITING_FOR_USER: "alert-warning",
    RESOLVED: "alert-danger",
    CLOSED: "alert-danger",
};

const PRIORITY_ALERT_CLASS = {
    NORMAL: "alert-info",
    WARNING: "alert-warning",
    CRITICAL: "alert-danger",
};

function getTicketIdFromUrl() {
    const parts = window.location.pathname.split("/").filter(Boolean);
    return parts[parts.length - 1];
}

function setActionFlash(type, text) {
    localStorage.setItem("ticket_action_flash", JSON.stringify({ type, text }));
}

function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    const div = document.createElement("div");
    div.textContent = String(str);
    return div.innerHTML;
}

async function apiFetch(url, options = {}) {
    const response = await fetch(url, { credentials: "include", ...options });
    if (response.status === 403) {
        window.location.href = "/forbidden";
        return null;
    }
    return response;
}

document.addEventListener("DOMContentLoaded", async () => {
    const ticketId = getTicketIdFromUrl();
    const container = document.getElementById("ticket-detail-container");
    const assignSection = document.getElementById("assign-section");
    const editSection = document.getElementById("edit-ticket-section");
    const reopenSection = document.getElementById("reopen-section");

    let currentUser = null;
    let ticket = null;

    try {
        const [meRes, ticketRes] = await Promise.all([
            apiFetch(ENDPOINTS.me),
            apiFetch(ENDPOINTS.ticket(ticketId)),
        ]);

        if (!meRes || !ticketRes) return; // 403 already redirected

        if (!meRes.ok) {
            container.innerHTML = `<div class="empty-state"><p>خطا در دریافت اطلاعات کاربر</p></div>`;
            return;
        }
        currentUser = await meRes.json();

        if (ticketRes.status === 404) {
            container.innerHTML = `<div class="empty-state"><p>تیکت مورد نظر یافت نشد</p></div>`;
            return;
        }
        if (!ticketRes.ok) {
            container.innerHTML = `<div class="empty-state"><p>خطا در دریافت اطلاعات تیکت</p></div>`;
            return;
        }
        ticket = await ticketRes.json();
    } catch (err) {
        console.error(err);
        container.innerHTML = `<div class="empty-state"><p>خطا در برقراری ارتباط با سرور</p></div>`;
        return;
    }

    renderNav(currentUser);
    renderTicketDetail(ticket, currentUser, container);
    renderAssignSection(ticket, currentUser, assignSection);
    renderEditSection(ticket, currentUser, editSection);
    renderReopenSection(ticket, currentUser, reopenSection);
    wireEditForm(ticket);
    wireNewResponseForm(ticket, currentUser);
});

function renderNav(currentUser) {
    const usersLink = document.getElementById("nav-users");
    const ticketsLink = document.getElementById("nav-tickets");
    const statsLink = document.getElementById("nav-stats");

    if (usersLink) {
        if (currentUser.user_role === "System Admin") {
            usersLink.textContent = "تمامی کاربران";
            usersLink.style.display = "";
        } else if (currentUser.user_role === "IT Manager") {
            usersLink.textContent = "تمامی کارشناسان";
            usersLink.style.display = "";
        } else {
            usersLink.style.display = "none";
        }
    }

    if (ticketsLink) {
        ticketsLink.textContent =
            currentUser.user_role === "IT Expert" ? "تمامی تیکت‌های کارشناس" : "تمامی تیکت‌ها";
    }

    if (statsLink) {
        statsLink.style.display =
            currentUser.user_role === "System Admin" || currentUser.user_role === "IT Manager" ? "" : "none";
    }
}

function renderTicketDetail(ticket, currentUser, container) {
    const statusClass = STATUS_ALERT_CLASS[ticket.status.name] || "alert-info";
    const priorityClass = PRIORITY_ALERT_CLASS[ticket.priority.name] || "alert-info";
    const isStudentOrEmployee = ["Student", "Employee"].includes(currentUser.user_role);

    const attachmentHtml = ticket.attachment
        ? `<a href="/contents/upload/${escapeHtml(ticket.attachment.file_name)}" target="_blank">مشاهده فایل پیوست</a>`
        : `<p class="ticket-created">فایل پیوستی یافت نشد</p>`;

    const assigneeHtml = ticket.assignee
        ? `<p>کارشناس بررسی کننده: ${escapeHtml(ticket.assignee.username)}</p>` +
          (["System Admin", "IT Manager"].includes(currentUser.user_role)
              ? `<form id="removeAssigneeForm" style="margin-top: 0.5rem;">
                    <button type="submit" class="submit-btn btn-small" style="background: #b91c1c; border-color: #b91c1c;">
                        حذف کارشناس ارجاع داده شده
                    </button>
                 </form>`
              : "")
        : `<p>به این تیکت هنوز کارشناسی ارجاع داده نشده.</p>`;

    const categoryHtml = ticket.category
        ? `<p>دسته بندی تیکت: ${escapeHtml(ticket.category.name)}</p>`
        : `<p>برای این تیکت دسته بندی انتخاب نشده.</p>`;

    const departmentHtml = ticket.department
        ? `<p>دپارتمان تیکت: ${escapeHtml(ticket.department.name)}</p>`
        : `<p>برای این تیکت دپارتمان انتخاب نشده.</p>`;

    const creatorHtml = !isStudentOrEmployee
        ? `<small><p class="ticket-created">شناسه کاربر ایجاد کننده: <a href="/users/${ticket.creator_id}">${ticket.creator_id}</a></p></small>`
        : "";

    const canRespond =
        (ticket.status.name === "IN_PROGRESS" && currentUser.user_role !== "Student") ||
        (ticket.status.name === "WAITING_FOR_USER" && currentUser.user_role === "Student");

    const responseFormHtml = canRespond
        ? `<form id="new-response-form" class="ticket-form">
             <div class="form-group">
                 <label for="response">متن پاسخ:</label>
                 <textarea id="response" name="text" placeholder="متن پاسخ خود را وارد کنید..." required></textarea>
                 <p id="response-error" class="alert alert-danger" style="display:none;"></p>
             </div>
             <button type="submit" class="submit-btn btn-small">ارسال پاسخ</button>
           </form>`
        : "";

    const isCreator = ticket.creator.id === currentUser.user_id;
    const isClosedOrResolved = ["RESOLVED", "CLOSED"].includes(ticket.status.name);

    let ratingHtml = "";
    if (isCreator) {
        const ratingSummary = isClosedOrResolved
            ? `<div class="rating-action">
                 <div class="rating-summary">
                   ${
                       ticket.satisfaction_rating
                           ? `<span>امتیاز ثبت شده: ${"★".repeat(ticket.satisfaction_rating)} / 5</span>`
                           : `<span>هنوز امتیازی ثبت نشده است.</span>`
                   }
                 </div>
                 ${
                     !ticket.satisfaction_rating
                         ? `<button type="button" class="rating-open-btn" data-modal-target="ratingModal">ثبت امتیاز</button>`
                         : ""
                 }
               </div>`
            : "";

        ratingHtml = `${ratingSummary}
            <div class="rating-modal-backdrop" id="ratingModalBackdrop"></div>
            <div class="rating-modal" id="ratingModal" role="dialog" aria-modal="true" aria-labelledby="ratingModalTitle" aria-hidden="true">
                <div class="rating-modal-content">
                    <button type="button" class="rating-modal-close" id="closeRatingModal" aria-label="بستن">×</button>
                    <h3 id="ratingModalTitle">امتیازدهی به تیکت</h3>
                    <p>از تجربه‌ی خود درباره‌ی این تیکت امتیاز دهید.</p>
                    <form id="ratingForm" class="rating-form">
                        <div class="rating-stars" role="radiogroup" aria-label="انتخاب امتیاز">
                            ${[1, 2, 3, 4, 5]
                                .map((v) => `<button type="button" class="rating-star" data-value="${v}" aria-label="${v} ستاره">★</button>`)
                                .join("")}
                        </div>
                        <input type="hidden" name="rating" id="ratingInput" value="5">
                        <button type="submit" class="submit-btn btn-small">ثبت امتیاز</button>
                    </form>
                </div>
            </div>`;
    }

    container.innerHTML = `
        <div class="ticket-item">
            <div class="ticket-meta">
                <div class="ticket-info">
                    <p class="ticket-id" id="ticket-id" data-ticket_id="${ticket.id}">#${ticket.id}</p>
                    <h3>عنوان: ${escapeHtml(ticket.title)}</h3>
                </div>
                <span class="status alert ${statusClass}">وضعیت: ${escapeHtml(ticket.status.fa)}</span>
                <span class="status alert ${priorityClass}">اولویت: ${escapeHtml(ticket.priority.fa)}</span>
            </div>
            <p class="ticket-description">توضیحات: ${escapeHtml(ticket.description)}</p>
            ${attachmentHtml}
            <div class="ticket-reply" id="ticket-reply" data-current-user-id="${currentUser.user_id}"></div>
            <br />
            ${assigneeHtml}
            ${categoryHtml}
            ${departmentHtml}
            <small><p class="ticket-created">ثبت شده در: ${escapeHtml(ticket.created_at)}</p></small>
            ${creatorHtml}
            ${responseFormHtml}
            ${ratingHtml}
        </div>
    `;

    const removeAssigneeForm = document.getElementById("removeAssigneeForm");
    if (removeAssigneeForm) {
        removeAssigneeForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            if (!confirm("آیا از حذف کارشناس ارجاع داده شده مطمئن هستید؟")) return;
            try {
                const res = await apiFetch(ENDPOINTS.removeAssignee(ticket.id), { method: "POST" });
                if (!res) return;
                if (res.ok) {
                    setActionFlash("success", "کارشناس ارجاع داده شده با موفقیت حذف شد");
                    window.location.reload();
                } else {
                    const error = await res.text();
                    alert("Error: " + error);
                }
            } catch (err) {
                console.error(err);
            }
        });
    }

    if (isCreator) {
        wireRatingModal(ticket);
    }
}

function wireRatingModal(ticket) {
    const modal = document.getElementById("ratingModal");
    const backdrop = document.getElementById("ratingModalBackdrop");
    const openBtn = document.querySelector('[data-modal-target="ratingModal"]');
    const closeBtn = document.getElementById("closeRatingModal");
    const ratingInput = document.getElementById("ratingInput");
    const stars = document.querySelectorAll(".rating-star");
    const ratingForm = document.getElementById("ratingForm");

    function openModal() {
        if (!modal || !backdrop) return;
        modal.classList.add("is-open");
        backdrop.classList.add("is-open");
        document.body.classList.add("modal-open");
        modal.setAttribute("aria-hidden", "false");
    }

    function closeModal() {
        if (!modal || !backdrop) return;
        modal.classList.remove("is-open");
        backdrop.classList.remove("is-open");
        document.body.classList.remove("modal-open");
        modal.setAttribute("aria-hidden", "true");
    }

    if (openBtn) openBtn.addEventListener("click", openModal);
    if (closeBtn) closeBtn.addEventListener("click", closeModal);
    if (backdrop) backdrop.addEventListener("click", closeModal);
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") closeModal();
    });

    stars.forEach((star) => {
        star.addEventListener("click", () => {
            const value = star.getAttribute("data-value");
            ratingInput.value = value;
            stars.forEach((item) => {
                item.classList.toggle("active", item.getAttribute("data-value") <= value);
            });
        });
    });

    if (ratingForm) {
        ratingForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            try {
                const formData = new FormData(ratingForm);
                const res = await apiFetch(ENDPOINTS.rate(ticket.id), { method: "POST", body: formData });
                if (!res) return;
                if (res.ok) {
                    setActionFlash("success", "امتیاز با موفقیت ثبت شد");
                    window.location.reload();
                } else {
                    const error = await res.text();
                    alert("Error: " + error);
                }
            } catch (err) {
                console.error(err);
            }
        });
    }
}

function renderAssignSection(ticket, currentUser, section) {
    const eligibleRole = !["Student", "Employee", "IT Expert"].includes(currentUser.user_role);
    const canShow = eligibleRole && !ticket.assigned_to && !["RESOLVED", "CLOSED"].includes(ticket.status.name);

    if (!canShow) {
        section.style.display = "none";
        section.innerHTML = "";
        return;
    }

    section.style.display = "";
    section.innerHTML = `
        <div class="section-header"><h2>اختصاص اتوماتیک تیکت به کارشناس</h2></div>
        <div id="assign-preview-area">
            <a href="#" id="assign-preview-link" class="submit-btn btn-small" style="text-decoration: none;">
                اجرای فرایند اختصاص
            </a>
        </div>
    `;

    document.getElementById("assign-preview-link").addEventListener("click", async (e) => {
        e.preventDefault();
        try {
            const res = await apiFetch(ENDPOINTS.assignPreview(ticket.id));
            if (!res) return;
            if (!res.ok) {
                const error = await res.text();
                alert("Error: " + error);
                return;
            }
            const data = await res.json();
            const area = document.getElementById("assign-preview-area");
            area.innerHTML = `
                <div class="alert alert-info">کارشناس پیشنهادی: ${escapeHtml(data.suggested_expert_name)}</div>
                <p>آیا می‌خواهید این کارشناس به این تیکت اختصاص داده شود؟</p>
                <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; align-items: center;">
                    <button class="submit-btn btn-small" id="assign-confirm-btn" type="button">بله، انجام شود</button>
                    <button class="submit-btn btn-small" id="assign-cancel-btn" type="button">خیر، لغو شود</button>
                </div>
            `;
            document.getElementById("assign-cancel-btn").addEventListener("click", () => renderAssignSection(ticket, currentUser, section));
            document.getElementById("assign-confirm-btn").addEventListener("click", async () => {
                try {
                    const confirmRes = await apiFetch(ENDPOINTS.assign(ticket.id), { method: "POST" });
                    if (!confirmRes) return;
                    if (confirmRes.ok) {
                        setActionFlash("success", "اختصاص اتوماتیک کارشناس به تیکت با موفقیت انجام شد");
                        window.location.reload();
                    } else {
                        const error = await confirmRes.text();
                        setActionFlash("danger", error);
                        window.location.reload();
                    }
                } catch (err) {
                    console.error(err);
                }
            });
        } catch (err) {
            console.error(err);
        }
    });
}

function renderEditSection(ticket, currentUser, section) {
    const isClosedOrResolved = ["RESOLVED", "CLOSED"].includes(ticket.status.name);
    if (isClosedOrResolved) {
        section.style.display = "none";
        return;
    }
    section.style.display = "";

    const form = section.querySelector("#editForm");
    const role = currentUser.user_role;
    const isStudentOrEmployee = ["Student", "Employee"].includes(role);
    const isItExpert = role === "IT Expert";
    const opts = ticket.edit_options || { statuses: [], priorities: [], it_experts: [], categories: [], departments: [] };

    let html = "";

    if (!isStudentOrEmployee) {
        if (!isItExpert) {
            html += `
                <div class="form-group">
                    <label>عنوان</label>
                    <input type="text" name="title" value="${escapeHtml(ticket.title)}" required placeholder="عنوان تیکت">
                </div>
                <div class="form-group">
                    <label>توضیحات</label>
                    <input type="text" name="description" value="${escapeHtml(ticket.description)}" required placeholder="توضیحات تیکت">
                </div>`;
        }

        if (!isItExpert) {
            html += `
                <div class="form-group">
                    <label>وضعیت</label>
                    <select name="ticket_status" required>
                        ${opts.statuses
                            .map((s) => `<option value="${s.name}" ${ticket.status.name === s.name ? "selected" : ""}>${escapeHtml(s.fa)}</option>`)
                            .join("")}
                    </select>
                </div>`;
        } else {
            html += `
                <div class="form-group">
                    <label class="custom-checkbox" for="ticket_status">
                        <input type="checkbox" id="ticket_status" name="ticket_status" value="RESOLVED">
                        <span>مشکل تیکت حل شد</span>
                    </label>
                </div>`;
        }

        if (!isItExpert) {
            html += `
                <div class="form-group">
                    <label>اولویت</label>
                    <select name="priority" required>
                        ${opts.priorities
                            .map((p) => `<option value="${p.name}" ${ticket.priority.name === p.name ? "selected" : ""}>${escapeHtml(p.fa)}</option>`)
                            .join("")}
                    </select>
                </div>
                <div class="form-group">
                    <label>کارشناس بررسی کننده</label>
                    ${
                        opts.it_experts.length === 0
                            ? ticket.department_id
                                ? `<div class="alert alert-info">در دپارتمان تعیین شده برای تیکت، کارشناسی فعالیت نمیکند.</div>`
                                : `<div class="alert alert-info">برای انتخاب کارشناس، ابتدا دپارتمان تیکت را مشخص کنید و دکمه "آپدیت تیکت" را بزنید</div>`
                            : ""
                    }
                    <select name="assigned_to">
                        <option value="">-- کارشناس را انتخاب کنید --</option>
                        ${opts.it_experts
                            .map((e) => `<option value="${e.id}" ${ticket.assigned_to === e.id ? "selected" : ""}>${escapeHtml(e.name)}</option>`)
                            .join("")}
                    </select>
                </div>
                <div class="form-group">
                    <label>دسته بندی تیکت</label>
                    <select name="category_id">
                        <option value="">-- دسته بندی را انتخاب کنید --</option>
                        ${opts.categories
                            .map((c) => `<option value="${c.id}" ${ticket.category_id === c.id ? "selected" : ""}>${escapeHtml(c.name)}</option>`)
                            .join("")}
                    </select>
                </div>
                <div class="form-group">
                    <label>دپارتمان تیکت</label>
                    <select name="department_id">
                        <option value="">-- دپارتمان را انتخاب کنید --</option>
                        ${opts.departments
                            .map((d) => `<option value="${d.id}" ${ticket.department_id === d.id ? "selected" : ""}>${escapeHtml(d.name)}</option>`)
                            .join("")}
                    </select>
                </div>`;
        }
    } else {
        html += `
            <div class="form-group">
                <label class="custom-checkbox" for="ticket_status">
                    <input type="checkbox" id="ticket_status" name="ticket_status" value="CLOSED">
                    <span>آیا میخواهید تیکت را ببندید؟</span>
                </label>
            </div>`;
    }

    html += `<button class="submit-btn" type="submit">آپدیت تیکت</button>`;
    form.innerHTML = html;
}

function renderReopenSection(ticket, currentUser, section) {
    const canShow =
        ["RESOLVED", "CLOSED"].includes(ticket.status.name) &&
        ["System Admin", "IT Manager"].includes(currentUser.user_role);

    if (!canShow) {
        section.style.display = "none";
        section.innerHTML = "";
        return;
    }

    section.style.display = "";
    section.innerHTML = `
        <div class="section-header"><h2>باز کردن دوباره تیکت</h2></div>
        <form class="ticket-form" id="reopenForm" style="font-size: 1.5em;">
            <div class="form-group">
                <label class="custom-checkbox" for="reopen_status">
                    <input type="checkbox" id="reopen_status" name="ticket_status" value="IN_PROGRESS">
                    <span>این تیکت بسته شده است. آیا میخواهید آن را دوباره باز کنید؟ (این کار باعث حذف امتیاز این تیکت میشود)</span>
                </label>
            </div>
            <button class="submit-btn" type="submit">آپدیت تیکت</button>
        </form>
    `;

    document.getElementById("reopenForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        try {
            const res = await apiFetch(ENDPOINTS.reopen(ticket.id), { method: "PATCH", body: formData });
            if (!res) return;
            if (res.ok) {
                setActionFlash("success", "تیکت با موفقیت دوباره در وضعیت در حال بررسی قرار گرفت");
                window.location.reload();
            } else {
                const error = await res.text();
                alert("Error: " + error);
            }
        } catch (err) {
            console.error(err);
        }
    });
}

function wireEditForm(ticket) {
    const form = document.getElementById("editForm");
    if (!form) return;
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        try {
            const res = await apiFetch(ENDPOINTS.ticket(ticket.id), { method: "PATCH", body: formData });
            if (!res) return;
            if (res.ok) {
                localStorage.setItem("ticket_update_flash_message", "successful");
                window.location.reload();
            } else {
                const error = await res.text();
                alert("Error: " + error);
            }
        } catch (err) {
            console.error(err);
        }
    });
}

function wireNewResponseForm(ticket, currentUser) {
    const form = document.getElementById("new-response-form");
    if (!form) return;
    const errorEl = document.getElementById("response-error");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (errorEl) errorEl.style.display = "none";
        const formData = new FormData(form);
        try {
            const res = await apiFetch(`/api/tickets/${ticket.id}/responses`, { method: "POST", body: formData });
            if (!res) return;
            if (res.ok) {
                window.location.reload();
            } else {
                const error = await res.text();
                if (errorEl) {
                    errorEl.textContent = error;
                    errorEl.style.display = "block";
                } else {
                    alert("Error: " + error);
                }
            }
        } catch (err) {
            console.error(err);
        }
    });
}
