document.getElementById("logout-btn")?.addEventListener("click", async (e) => {
    e.preventDefault();

    const response = await fetch("/api/auth/logout", {
        method: "POST"
    });

    if (response.ok) {
        window.location.href = "/";
    }
});
