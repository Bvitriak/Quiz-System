(function () {
    "use strict";

    function initAnswers() {
        const wrap = document.getElementById("answers");
        const btn = document.getElementById("addOption");
        if (!wrap || !btn) return;

        function currentInputType() {
            return wrap.dataset.type === "multiple" ? "checkbox" : "radio";
        }

        function buildCard(idx) {
            const card = document.createElement("div");
            card.className = "answer-card";
            card.innerHTML =
                '<header class="answer-card__head">' +
                    '<span class="answer-card__title">Answer ' + (idx + 1) + '</span>' +
                    '<label class="answer-card__correct">' +
                        '<input type="' + currentInputType() + '" ' +
                               'name="correct" value="' + idx + '">' +
                        '<span>Correct</span>' +
                    '</label>' +
                '</header>' +
                '<input class="form__input" type="text" name="option" ' +
                       'placeholder="Answer option">';
            return card;
        }

        btn.addEventListener("click", function (event) {
            event.preventDefault();
            event.stopPropagation();
            const idx = wrap.querySelectorAll(".answer-card").length;
            wrap.appendChild(buildCard(idx));
        });
    }

    function syncCorrectInputs(answersWrap, newType) {
        const inputs = answersWrap.querySelectorAll('input[name="correct"]');
        inputs.forEach(function (inp) {
            inp.type = newType === "multiple" ? "checkbox" : "radio";
        });
        if (newType === "single") {
            let firstChecked = null;
            inputs.forEach(function (inp) {
                if (inp.checked) {
                    if (firstChecked === null) {
                        firstChecked = inp;
                    } else {
                        inp.checked = false;
                    }
                }
            });
        }
    }

    function initTypeSwitch() {
        const sw = document.querySelector(".qtype-switch");
        if (!sw) return;
        if (sw.dataset.edit === "1") return;

        const radios = sw.querySelectorAll('input[name="type"]');
        const blocks = document.querySelectorAll(".qblock");
        const answersWrap = document.getElementById("answers");

        function apply(newType) {
            blocks.forEach(function (b) {
                const roles = (b.dataset.roles || "").split(",");
                b.hidden = roles.indexOf(newType) === -1;
            });
            if (answersWrap && (newType === "single" || newType === "multiple")) {
                answersWrap.dataset.type = newType;
                syncCorrectInputs(answersWrap, newType);
            }
        }

        radios.forEach(function (r) {
            r.addEventListener("change", function () {
                if (r.checked) apply(r.value);
            });
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        initAnswers();
        initTypeSwitch();
    });
})();
