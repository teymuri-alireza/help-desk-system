(() => {
    const searchInput = document.getElementById("ticket-search");
    const container = document.getElementById("tickets-container");

    if (!searchInput || !container) return;

    function filterTickets() {
        const term = searchInput.value.toLowerCase().trim();
        const ticketItems = container.querySelectorAll(".ticket-item");
        let visibleCount = 0;

        ticketItems.forEach((ticket) => {
            const ticketId = ticket.querySelector(".ticket-id")?.textContent.toLowerCase() || "";
            const ticketTitle = ticket.querySelector("h3")?.textContent.toLowerCase() || "";
            const ticketDescription = ticket.querySelector(".ticket-description")?.textContent.toLowerCase() || "";
            const ticketStatus = ticket.querySelector(".status")?.textContent.toLowerCase() || "";

            const isMatch =
                !term ||
                ticketId.includes(term) ||
                ticketTitle.includes(term) ||
                ticketDescription.includes(term) ||
                ticketStatus.includes(term);

            ticket.classList.toggle("hidden", !isMatch);

            if (isMatch) visibleCount++;
        });

        let emptyMessage = container.querySelector(".search-empty-state");

        if (visibleCount === 0 && term) {
            if (!emptyMessage) {
                emptyMessage = document.createElement("div");
                emptyMessage.className = "empty-state search-empty-state";
                emptyMessage.textContent = "نتیجه‌ای برای جستجو پیدا نشد";
                container.appendChild(emptyMessage);
            }
            emptyMessage.style.display = "block";
        } else if (emptyMessage) {
            emptyMessage.style.display = "none";
        }
    }

    searchInput.addEventListener("input", filterTickets);

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && document.activeElement === searchInput) {
            searchInput.value = "";
            filterTickets();
        }
    });

    const observer = new MutationObserver(() => {
        filterTickets();
    });

    observer.observe(container, {
        childList: true,
        subtree: true,
    });
})();