(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        const back = document.getElementById("errorBack");
        if (back) {
            back.addEventListener("click", function () {
                if (window.history.length > 1) {
                    window.history.back();
                } else {
                    window.location.href = "/";
                }
            });
        }

        const code = document.querySelector(".error__code");
        if (code) {
            const value = code.dataset.code || code.textContent;
            console.info("Error page", value);
        }
    });
})();
