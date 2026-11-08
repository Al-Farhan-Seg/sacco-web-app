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
    if (modal.querySelector("#modal-title")) modal.setAttribute("aria-labelledby", "modal-title");
    lucide.createIcons();
    const first = modal.querySelector("input:not([type=hidden]), select, textarea") || modal.querySelector(".btn[data-modal-close]");
    if (first) first.focus();
  }

  function showError(status) {
    const note = document.createElement("p");
    note.className = "form-errors";
    note.setAttribute("role", "alert");
    note.textContent = "Something went wrong (error " + status + "). Reload the page and try again.";
    modal.querySelector(".modal-body")?.prepend(note);
  }

  async function open(url) {
    const response = await fetch(url);
    if (sentToLogin(response)) return;
    if (!response.ok) return window.alert("Could not open the form (error " + response.status + ").");
    currentUrl = url;
    if (!modal.open) modal.showModal();
    fill(await response.text());
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
    const response = await fetch(form.getAttribute("action") || currentUrl, { method: "POST", body: new FormData(form) });
    if (sentToLogin(response)) return;
    if (response.status === 204) return window.location.reload();
    if (response.status === 400) return fill(await response.text());
    if (button) button.disabled = false;
    showError(response.status);
  });

  modal.addEventListener("close", function () {
    modal.innerHTML = "";
  });

  document.querySelectorAll(".toast").forEach(function (toast) {
    setTimeout(function () { toast.remove(); }, 5000);
  });

  lucide.createIcons();
})();
