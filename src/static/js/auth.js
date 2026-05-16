(function () {
    "use strict";

    const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    function showError(form, message) {
        let alert = form.querySelector(".alert--client");
        if (!alert) {
            alert = document.createElement("div");
            alert.className = "alert alert--error alert--client";
            form.prepend(alert);
        }
        alert.textContent = message;
    }

    function clearError(form) {
        const alert = form.querySelector(".alert--client");
        if (alert) alert.remove();
    }

    function validateRegister(form) {
        const fullName = form.full_name.value.trim();
        const email = form.email.value.trim();
        const role = form.role.value;
        const password = form.password.value;
        const confirm = form.password_confirm.value;

        if (!fullName) return "Enter your name";
        if (!EMAIL_RE.test(email)) return "Enter a valid Email";
        if (!role) return "Select a role";
        if (password.length < 6) return "Password must contain at least 6 characters";
        if (password !== confirm) return "Passwords do not match";
        return null;
    }

    function validateLogin(form) {
        const email = form.email.value.trim();
        const password = form.password.value;
        if (!EMAIL_RE.test(email)) return "Enter a valid Email";
        if (!password) return "Enter your password";
        return null;
    }

    function bind(formId, validator) {
        const form = document.getElementById(formId);
        if (!form) return;
        form.addEventListener("submit", function (event) {
            clearError(form);
            const error = validator(form);
            if (error) {
                event.preventDefault();
                showError(form, error);
            }
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        bind("registerForm", validateRegister);
        bind("loginForm", validateLogin);
    });
})();
