const roleMap = {
    "Student": "دانشجو",
    "Employee": "کارمند",
    "IT Expert": "کارشناس فناوری اطلاعات",
    "IT Manager": "مدیر فناوری اطلاعات",
    "System Admin": "مدیر سیستم"
};

function createResponseElement(response, currentUserId, ticketId) {
    const responseContainer = document.createElement("div");
    responseContainer.className = "response-item";
    responseContainer.style.display = "flex";
    responseContainer.style.justifyContent = "space-between";
    responseContainer.style.alignItems = "flex-start";
    responseContainer.style.gap = "12px";
    responseContainer.style.padding = "12px 0";

    const contentWrapper = document.createElement("div");
    contentWrapper.style.flex = "1";

    const idP = document.createElement("p");
    idP.className = "ticket-id";
    idP.textContent = `#${response.id}`;

    const br = document.createElement("br");
    idP.appendChild(br);

    const roleFa = roleMap[response.creator.role] || response.creator.role;
    const creatorText = document.createTextNode(`نویسنده: ${response.creator.name} - نقش: ${roleFa}`);
    idP.appendChild(creatorText);
    contentWrapper.appendChild(idP);

    const textP = document.createElement("p");
    textP.className = "response-text";
    textP.textContent = response.text;
    contentWrapper.appendChild(textP);
    responseContainer.appendChild(contentWrapper);

    if (currentUserId && Number(response.creator_id) === Number(currentUserId)) {
        const actionWrapper = document.createElement("div");
        actionWrapper.style.marginLeft = "auto";
        actionWrapper.style.flexShrink = "0";
        actionWrapper.style.display = "flex";
        actionWrapper.style.flexDirection = "column";
        actionWrapper.style.gap = "8px";

        const replyBtn = document.createElement("button");
        replyBtn.type = "button";
        replyBtn.className = "submit-btn btn-small";
        replyBtn.textContent = "پاسخ به این پاسخ";
        actionWrapper.appendChild(replyBtn);

        responseContainer.appendChild(actionWrapper);

        // --- reply popup modal ---
        const replyOverlay = document.createElement("div");
        replyOverlay.style.cssText = "position:fixed; inset:0; background:rgba(0,0,0,0.45); display:none; align-items:center; justify-content:center; z-index:1000;";

        const replyBox = document.createElement("div");
        replyBox.style.cssText = "background:#fff; width:min(90vw, 560px); padding:20px; border-radius:8px; box-shadow:0 12px 36px rgba(0,0,0,0.2);";

        const replyHeader = document.createElement("div");
        replyHeader.style.cssText = "display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;";

        const replyTitle = document.createElement("h3");
        replyTitle.textContent = "پاسخ به این پاسخ";
        replyHeader.appendChild(replyTitle);

        const replyCloseBtn = document.createElement("button");
        replyCloseBtn.type = "button";
        replyCloseBtn.textContent = "×";
        replyCloseBtn.style.cssText = "border:none; background:transparent; font-size:24px; cursor:pointer;";
        replyHeader.appendChild(replyCloseBtn);
        replyBox.appendChild(replyHeader);

        const replyForm = document.createElement("form");
        replyForm.className = "response-reply-form";

        const replyTextareaGroup = document.createElement("div");
        replyTextareaGroup.className = "form-group";

        const replyTextarea = document.createElement("textarea");
        replyTextarea.name = "text";
        replyTextarea.required = true;
        replyTextarea.placeholder = "متن پاسخ خود را وارد کنید...";
        replyTextarea.style.cssText = "width:100%; min-height:120px; resize:vertical;";
        replyTextareaGroup.appendChild(replyTextarea);
        replyForm.appendChild(replyTextareaGroup);

        const replyParentInput = document.createElement("input");
        replyParentInput.type = "hidden";
        replyParentInput.name = "parent_response_id";
        replyParentInput.value = response.id;
        replyForm.appendChild(replyParentInput);

        const replyActionButtons = document.createElement("div");
        replyActionButtons.style.cssText = "display:flex; justify-content:flex-end; gap:8px; margin-top:10px;";

        const replySubmitBtn = document.createElement("button");
        replySubmitBtn.type = "submit";
        replySubmitBtn.className = "submit-btn btn-small";
        replySubmitBtn.textContent = "ثبت پاسخ";
        replyActionButtons.appendChild(replySubmitBtn);

        const replyCancelBtn = document.createElement("button");
        replyCancelBtn.type = "button";
        replyCancelBtn.className = "submit-btn btn-small";
        replyCancelBtn.textContent = "انصراف";
        replyCancelBtn.addEventListener("click", () => {
            replyOverlay.style.display = "none";
        });
        replyActionButtons.appendChild(replyCancelBtn);

        replyForm.appendChild(replyActionButtons);
        replyBox.appendChild(replyForm);
        replyOverlay.appendChild(replyBox);
        document.body.appendChild(replyOverlay);

        replyBtn.addEventListener("click", () => {
            replyTextarea.value = "";
            replyOverlay.style.display = "flex";
        });

        replyCloseBtn.addEventListener("click", () => {
            replyOverlay.style.display = "none";
        });

        replyOverlay.addEventListener("click", (event) => {
            if (event.target === replyOverlay) {
                replyOverlay.style.display = "none";
            }
        });

        replyForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const formData = new FormData(replyForm);
            formData.set("text", replyTextarea.value);
            formData.set("parent_response_id", response.id);

            const replyResponse = await fetch(`/tickets/${ticketId}/responses`, {
                method: "POST",
                body: formData,
                credentials: "include"
            });

            if (replyResponse.ok) {
                replyOverlay.style.display = "none";
                window.location.reload();
            } else if (replyResponse.status === 403) {
                replyOverlay.style.display = "none";
                window.location.href = "/forbidden";
            } else {
                const errorText = await replyResponse.text();
                alert("خطا در ثبت پاسخ: " + errorText);
            }
        });

        const editToggleBtn = document.createElement("button");
        editToggleBtn.type = "button";
        editToggleBtn.className = "submit-btn btn-small";
        editToggleBtn.textContent = "ویرایش پاسخ";
        actionWrapper.appendChild(editToggleBtn);
        responseContainer.appendChild(actionWrapper);

        const modalOverlay = document.createElement("div");
        modalOverlay.style.cssText = "position:fixed; inset:0; background:rgba(0,0,0,0.45); display:none; align-items:center; justify-content:center; z-index:1000;";

        const modalBox = document.createElement("div");
        modalBox.style.cssText = "background:#fff; width:min(90vw, 560px); padding:20px; border-radius:8px; box-shadow:0 12px 36px rgba(0,0,0,0.2);";

        const modalHeader = document.createElement("div");
        modalHeader.style.cssText = "display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;";

        const modalTitle = document.createElement("h3");
        modalTitle.textContent = "ویرایش پاسخ";
        modalHeader.appendChild(modalTitle);

        const closeBtn = document.createElement("button");
        closeBtn.type = "button";
        closeBtn.textContent = "×";
        closeBtn.style.cssText = "border:none; background:transparent; font-size:24px; cursor:pointer;";
        modalHeader.appendChild(closeBtn);
        modalBox.appendChild(modalHeader);

        const editForm = document.createElement("form");
        editForm.className = "response-edit-form";

        const textareaGroup = document.createElement("div");
        textareaGroup.className = "form-group";

        const textarea = document.createElement("textarea");
        textarea.name = "text";
        textarea.required = true;
        textarea.value = response.text;
        textarea.style.cssText = "width:100%; min-height:120px; resize:vertical;";
        textareaGroup.appendChild(textarea);
        editForm.appendChild(textareaGroup);

        const actionButtons = document.createElement("div");
        actionButtons.style.cssText = "display:flex; justify-content:flex-end; gap:8px; margin-top:10px;";

        const saveBtn = document.createElement("button");
        saveBtn.type = "submit";
        saveBtn.className = "submit-btn btn-small";
        saveBtn.textContent = "ثبت تغییر";
        actionButtons.appendChild(saveBtn);

        const cancelBtn = document.createElement("button");
        cancelBtn.type = "button";
        cancelBtn.className = "submit-btn btn-small";
        cancelBtn.textContent = "انصراف";
        cancelBtn.addEventListener("click", () => {
            modalOverlay.style.display = "none";
        });
        actionButtons.appendChild(cancelBtn);
        editForm.appendChild(actionButtons);
        modalBox.appendChild(editForm);
        modalOverlay.appendChild(modalBox);
        document.body.appendChild(modalOverlay);

        const openModal = () => {
            textarea.value = response.text;
            modalOverlay.style.display = "flex";
        };

        editToggleBtn.addEventListener("click", openModal);
        closeBtn.addEventListener("click", () => {
            modalOverlay.style.display = "none";
        });
        modalOverlay.addEventListener("click", (event) => {
            if (event.target === modalOverlay) {
                modalOverlay.style.display = "none";
            }
        });

        editForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const formData = new FormData();
            formData.append("text", textarea.value);

            const responsePatch = await fetch(`/tickets/${ticketId}/responses/${response.id}`, {
                method: "PATCH",
                body: formData,
                credentials: "include"
            });

            if (responsePatch.ok) {
                modalOverlay.style.display = "none";
                localStorage.setItem('edit_response_ok', 'successful');
                window.location.reload();
            } else if (responsePatch.status === 403) {
                modalOverlay.style.display = "none";
                window.location.href = "/forbidden";
            } else {
                localStorage.setItem('edit_response_unavailable', 'error');
                const errorText = await responsePatch.text();
                alert("خطا در ویرایش پاسخ: " + errorText);
            }
        });
    }

    const hr = document.createElement("hr");
    hr.className = "line";
    responseContainer.appendChild(hr);

    return responseContainer;
}

function renderResponses(responses) {
    const responseDiv = document.getElementById("ticket-reply");
    const currentUserId = responseDiv.dataset.currentUserId;
    responseDiv.innerHTML = "";

    if (!responses || responses.length === 0) {
        const none = document.createElement("p");
        none.textContent = "پاسخی ثبت نشده";
        responseDiv.appendChild(none);
        return;
    }

    const label = document.createElement("p");
    label.className = "reply-label";
    label.textContent = "💬 پاسخ:";
    responseDiv.appendChild(label);

    const ticketID = document.getElementById("ticket-id");
    const ticketId = ticketID ? ticketID.dataset.ticket_id : null;

    for (const response of responses) {
        const responseElement = createResponseElement(response, currentUserId, ticketId);
        responseDiv.appendChild(responseElement);
    }
}

async function loadResponses() {
    const ticketID = document.getElementById("ticket-id");
    if (!ticketID) {
        return;
    }

    const response = await fetch(`/tickets/${ticketID.dataset.ticket_id}/responses`);
    if (response.ok) {
        const data = await response.json();
        const responses = data.responses;

        renderResponses(responses);
    }
}

loadResponses();