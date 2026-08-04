document.addEventListener("submit", function (event) {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) {
        return;
    }

    if ((form.method || "get").toLowerCase() !== "post") {
        return;
    }

    if (form.dataset.submitting === "true") {
        event.preventDefault();
        return;
    }

    form.dataset.submitting = "true";
    window.setTimeout(function () {
        form.querySelectorAll('button[type="submit"], input[type="submit"]').forEach(function (button) {
            button.disabled = true;
        });
    }, 0);
});

window.submitPostWithCsrf = function (url, fields) {
    const form = document.createElement("form");
    form.method = "post";
    form.action = url;

    const csrfSource = document.querySelector('[name="csrfmiddlewaretoken"]');
    if (!csrfSource) {
        throw new Error("No se encontro el token CSRF.");
    }

    const csrf = document.createElement("input");
    csrf.type = "hidden";
    csrf.name = "csrfmiddlewaretoken";
    csrf.value = csrfSource.value;
    form.appendChild(csrf);

    Object.entries(fields).forEach(function ([name, value]) {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = name;
        input.value = value;
        form.appendChild(input);
    });

    document.body.appendChild(form);
    form.requestSubmit();
};
