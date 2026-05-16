(function () {
    "use strict";

    function init() {
        const avatar = document.getElementById("userAvatar");
        const menu = document.getElementById("userMenu");
        if (!avatar || !menu) return;

        function open() {
            menu.hidden = false;
            avatar.setAttribute("aria-expanded", "true");
        }

        function close() {
            menu.hidden = true;
            avatar.setAttribute("aria-expanded", "false");
        }

        avatar.addEventListener("click", function (event) {
            event.stopPropagation();
            if (menu.hidden) {
                open();
            } else {
                close();
            }
        });

        document.addEventListener("click", function (event) {
            if (menu.hidden) return;
            if (event.target === avatar || avatar.contains(event.target)) return;
            if (menu.contains(event.target)) return;
            close();
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && !menu.hidden) {
                close();
                avatar.focus();
            }
        });
    }

    function isSameOriginNav(link) {
        const href = link.getAttribute("href");
        if (!href || href.startsWith("#") || href.startsWith("javascript:")) return false;
        try {
            const url = new URL(href, window.location.href);
            return url.origin === window.location.origin;
        } catch (e) {
            return false;
        }
    }

    function initPageTransitions() {
        const supportsNativeVT = "startViewTransition" in document &&
            document.querySelector('meta[name="view-transition"]') !== null;
        if (supportsNativeVT) return;

        const prefersReduce = window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        ).matches;
        if (prefersReduce) return;

        const selectors = ".tabs__item, .topbar__logo, .user-menu__logout";
        document.body.addEventListener("click", function (event) {
            const link = event.target.closest(selectors);
            if (!link) return;
            if (event.button !== 0) return;
            if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
            if (link.target === "_blank") return;
            if (!isSameOriginNav(link)) return;

            event.preventDefault();
            const href = link.getAttribute("href");
            document.body.classList.add("is-leaving");
            window.setTimeout(function () {
                window.location.href = href;
            }, 170);
        });

        window.addEventListener("pageshow", function () {
            document.body.classList.remove("is-leaving");
        });
    }

    function initConfirmHandlers() {
        document.body.addEventListener("click", function (event) {
            const target = event.target.closest("[data-confirm]");
            if (!target) return;
            const message = target.getAttribute("data-confirm");
            if (!window.confirm(message)) {
                event.preventDefault();
                event.stopPropagation();
            }
        });
    }

    function initToasts() {
        const data = document.getElementById("flashData");
        if (!data) return;
        let items;
        try {
            items = JSON.parse(data.textContent || "[]");
        } catch (e) {
            return;
        }
        if (!items.length) return;

        let stack = document.querySelector(".toast-stack");
        if (!stack) {
            stack = document.createElement("div");
            stack.className = "toast-stack";
            document.body.appendChild(stack);
        }

        items.forEach(function (item, idx) {
            const el = document.createElement("div");
            const category = (item.category || "info").toLowerCase();
            el.className = "toast toast--" + category;
            el.textContent = item.message;
            stack.appendChild(el);

            window.setTimeout(function () {
                el.classList.add("is-leaving");
                window.setTimeout(function () {
                    el.remove();
                }, 250);
            }, 3500 + idx * 200);
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        init();
        initPageTransitions();
        initConfirmHandlers();
        initToasts();
    });
})();
