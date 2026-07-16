const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");

const loginError = document.getElementById("login-error");
const signupError = document.getElementById("signup-error");

function showError(element, message) {
    element.textContent = message;
    element.style.display = "block";
}

function clearError(element) {
    element.textContent = "";
    element.style.display = "none";
}

/* ---------------- LOGIN ---------------- */

loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    clearError(loginError);

    const formData = new FormData(loginForm);

    try {
        const response = await fetch("/api/auth/login", {
            method: "POST",
            body: formData,
            credentials: "same-origin"
        });

        if (response.ok) {
            window.location.href = "/dashboard";
            return;
        }

        const data = await response.json();

        switch (response.status) {
            case 401:
                showError(loginError, "کاربر یافت نشد.");
                break;

            case 403:
                showError(loginError, "حساب کاربری شما غیرفعال شده است.");
                break;

            default:
                showError(loginError, data.detail || "خطایی رخ داده است.");
        }

    } catch (err) {
        showError(loginError, "ارتباط با سرور برقرار نشد.");
    }
});


/* ---------------- SIGNUP ---------------- */

signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    clearError(signupError);

    const formData = new FormData(signupForm);

    try {
        const response = await fetch("/api/auth/signup", {
            method: "POST",
            body: formData,
            credentials: "same-origin"
        });

        if (response.ok) {
            window.location.href = "/dashboard";
            return;
        }

        const data = await response.json();

        switch (response.status) {
            case 409:
                showError(signupError, "این نام کاربری قبلاً ثبت شده است.");
                break;

            default:
                showError(signupError, data.detail || "ثبت‌نام با خطا مواجه شد.");
        }

    } catch (err) {
        showError(signupError, "ارتباط با سرور برقرار نشد.");
    }
});