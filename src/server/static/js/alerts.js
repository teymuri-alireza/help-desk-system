document.addEventListener("DOMContentLoaded", () => {
    const ticketAlert = document.getElementById("ticket-flash-alert");
    const userAlert = document.getElementById("user-flash-alert");
    const ticketClosedAlert = document.getElementById("ticket-closed-flash-alert");

    if (ticketAlert) {
        setTimeout(() => {
            ticketAlert.style.opacity = "0";

            setTimeout(() => {
                ticketAlert.remove();
            }, 500);
        }, 3500);
    }

    if (userAlert) {
        setTimeout(() => {
            userAlert.style.opacity = "0";

            setTimeout(() => {
                userAlert.remove();
            }, 500);
        }, 3500);
    }

    if (ticketClosedAlert) {
        setTimeout(() => {
            ticketClosedAlert.style.opacity = "0";

            setTimeout(() => {
                ticketClosedAlert.remove();
            }, 500);
        }, 3500);
    }
});
