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

    const idP = document.createElement("p");
    idP.className = "ticket-id";
    idP.textContent = `#${response.id}`;

    const br = document.createElement("br");
    idP.appendChild(br);

    const roleFa = roleMap[response.creator.role] || response.creator.role;
    const creatorText = document.createTextNode(`نویسنده: ${response.creator.name} - نقش: ${roleFa}`);
    idP.appendChild(creatorText);
    responseContainer.appendChild(idP);

    const textP = document.createElement("p");
    textP.className = "response-text";
    textP.textContent = response.text;
    responseContainer.appendChild(textP);

    if (currentUserId && Number(response.creator_id) === Number(currentUserId)) {
        const editToggleBtn = document.createElement("button");
        editToggleBtn.type = "button";
        editToggleBtn.className = "submit-btn btn-small";
        editToggleBtn.textContent = "ویرایش پاسخ";
        responseContainer.appendChild(editToggleBtn);

        const editForm = document.createElement("form");
        editForm.className = "response-edit-form";
        editForm.style.display = "none";

        const textareaGroup = document.createElement("div");
        textareaGroup.className = "form-group";

        const textarea = document.createElement("textarea");
        textarea.name = "text";
        textarea.required = true;
        textarea.value = response.text;
        textareaGroup.appendChild(textarea);
        editForm.appendChild(textareaGroup);

        const saveBtn = document.createElement("button");
        saveBtn.type = "submit";
        saveBtn.className = "submit-btn btn-small";
        saveBtn.textContent = "ثبت تغییر";
        editForm.appendChild(saveBtn);

        editToggleBtn.addEventListener("click", () => {
            editForm.style.display = editForm.style.display === "none" ? "block" : "none";
        });

        editForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const formData = new FormData();
            formData.append("text", textarea.value);

            const responsePatch = await fetch(`/tickets/${ticketId}/responses/${response.id}`, {
                method: "PATCH",
                body: formData,
                credentials: "include"
            });

            if (responsePatch.ok) {
                window.location.reload();
            } else if (responsePatch.status === 403) {
                window.location.href = "/forbidden";
            } else {
                const errorText = await responsePatch.text();
                alert("خطا در ویرایش پاسخ: " + errorText);
            }
        });

        responseContainer.appendChild(editForm);
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