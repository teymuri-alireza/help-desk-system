const roleMap = {
    "Student": "دانشجو",
    "Employee": "کارمند",
    "IT Expert": "کارشناس فناوری اطلاعات",
    "Help Desk Manager": "مدیر میز خدمت",
    "IT Manager": "مدیر فناوری اطلاعات",
    "System Admin": "مدیر سیستم"
};

function renderResponses(responses) {
    const responseDiv = document.getElementById("ticket-reply");
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

    for (const response of responses) {
        const idP = document.createElement("p");
        idP.className = "ticket-id";
        idP.textContent = `#${response.id}`;

        const br = document.createElement("br");
        idP.appendChild(br);

        const roleFa = roleMap[response.creator.role] || response.creator.role;
        const creatorText = document.createTextNode(`نویسنده: ${response.creator.name} - نقش: ${roleFa}`);
        idP.appendChild(creatorText);
        responseDiv.appendChild(idP);

        const textP = document.createElement("p");
        textP.textContent = response.text;
        responseDiv.appendChild(textP);

        const hr = document.createElement("hr");
        hr.className = "line";
        responseDiv.appendChild(hr);
    }
}

async function loadResponses() {
    const responseDiv = document.getElementById("ticket-reply");
    const ticketID = document.getElementById("ticket-id");

    const response = await fetch(`/tickets/${ticketID.dataset.ticket_id}/responses`);
    if (response.ok) {
        const data = await response.json();
        const responses = data.responses;

        renderResponses(responses);
    }
}

loadResponses()