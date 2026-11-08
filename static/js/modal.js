// Opens add/edit/delete forms in the shared <dialog id="modal">.
(function () {
  const modal = document.getElementById("modal");
  let currentUrl = "";

  // A logged-out fetch is redirected to the login page: go there instead of showing it in the modal.
  function sentToLogin(response) {
    if (response.redirected && response.url.includes("/login/")) {
      window.location = response.url;
      return true;
    }
    return false;
  }

  function fill(html) {
    modal.innerHTML = html;
    lucide.createIcons();
    const first = modal.querySelector("[aria-invalid=true], .has-error input, .has-error select, .has-error textarea") || modal.querySelector("input:not([type=hidden]), select, textarea") || modal.querySelector(".btn[data-modal-close]");
    if (first) first.focus();
  }

  function showError(problem) {
    modal.querySelector(".modal-body > .js-error")?.remove();
    const note = document.createElement("p");
    note.className = "form-errors js-error";
    note.setAttribute("role", "alert");
    note.textContent = "Could not save (" + problem + "). Check your connection and try again.";
    modal.querySelector(".modal-body")?.prepend(note);
  }

  // Error toast for when the form cannot be opened at all.
  function showToast(text) {
    let box = document.querySelector(".toasts");
    if (!box) {
      box = document.createElement("div");
      box.className = "toasts";
      box.setAttribute("role", "status");
      document.body.append(box);
    }
    const toast = document.createElement("div");
    toast.className = "toast toast-error";
    toast.textContent = text;
    box.append(toast);
    setTimeout(function () { toast.remove(); }, 5000);
  }

  async function open(url) {
    let response, html;
    try {
      response = await fetch(url);
      if (sentToLogin(response)) return;
      if (!response.ok) throw new Error("error " + response.status);
      html = await response.text();
    } catch (error) {
      return showToast("Could not open the form (" + (error.message || "network error") + "). Try again.");
    }
    currentUrl = url;
    if (!modal.open) modal.showModal();
    fill(html);
  }

  document.addEventListener("click", function (event) {
    const opener = event.target.closest("[data-modal-url]");
    if (opener) {
      event.preventDefault();
      open(opener.dataset.modalUrl);
    } else if (event.target.closest("[data-modal-close]") || event.target === modal) {
      modal.close();
    }
  });

  modal.addEventListener("submit", async function (event) {
    event.preventDefault();
    const form = event.target;
    const button = form.querySelector("[type=submit]");
    if (button) button.disabled = true;
    try {
      const response = await fetch(form.getAttribute("action") || currentUrl, { method: "POST", body: new FormData(form) });
      if (sentToLogin(response)) return;
      if (response.status === 204) return window.location.reload();
      if (response.status === 400) return fill(await response.text());
      showError("error " + response.status);
    } catch (error) {
      showError("network error");
    }
    if (button) button.disabled = false;
  });

  modal.addEventListener("close", function () {
    modal.innerHTML = "";
  });

  document.querySelectorAll(".toast").forEach(function (toast) {
    setTimeout(function () { toast.remove(); }, 5000);
  });

  lucide.createIcons();
})();
