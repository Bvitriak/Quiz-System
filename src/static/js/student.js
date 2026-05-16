(function () {
    "use strict";

    function formatTime(seconds) {
        const m = Math.floor(seconds / 60).toString().padStart(2, "0");
        const s = Math.floor(seconds % 60).toString().padStart(2, "0");
        return `${m}:${s}`;
    }

    function initTimer() {
        const form = document.getElementById("quizForm");
        if (!form) return;

        const remainingAttr = form.dataset.remaining;
        const timeoutUrl = form.dataset.timeoutUrl;
        let remaining = parseInt(remainingAttr, 10);
        if (Number.isNaN(remaining)) return;

        const timer = document.getElementById("timer");
        const timerInfo = document.getElementById("timerInfo");

        function render() {
            const text = formatTime(remaining);
            if (timer) timer.textContent = text;
            if (timerInfo) timerInfo.textContent = text;
        }

        render();

        const interval = setInterval(function () {
            remaining -= 1;
            if (remaining <= 0) {
                clearInterval(interval);
                render();
                const finishForm = document.createElement("form");
                finishForm.method = "post";
                finishForm.action = timeoutUrl;
                document.body.appendChild(finishForm);
                finishForm.submit();
                return;
            }
            render();
        }, 1000);
    }

    function initAnswerGuard() {
        const form = document.getElementById("quizForm");
        if (!form) return;
        const submitBtn = form.querySelector(
            'button[name="next"], button[name="finish"]'
        );
        if (!submitBtn) return;

        function hasAnswer() {
            const textarea = form.querySelector('textarea[name="text_answer"]');
            if (textarea) return textarea.value.trim().length > 0;
            const checked = form.querySelectorAll('input[name="option"]:checked');
            return checked.length > 0;
        }

        function refresh() {
            submitBtn.disabled = !hasAnswer();
        }

        form.addEventListener("input", refresh);
        form.addEventListener("change", refresh);
        // Restore state when returning via bfcache (Back/Forward).
        window.addEventListener("pageshow", refresh);
        refresh();
    }

    function initHistoryShowMore() {
        const btn = document.querySelector(".history__more");
        if (!btn) return;
        btn.addEventListener("click", function () {
            const rows = document.querySelectorAll(".history tbody tr.is-hidden");
            rows.forEach(function (r) { r.classList.remove("is-hidden"); });
            btn.style.display = "none";
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        initTimer();
        initAnswerGuard();
        initHistoryShowMore();
    });
})();
