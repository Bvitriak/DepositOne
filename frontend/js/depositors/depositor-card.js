const token = localStorage.getItem("access_token");
const params = new URLSearchParams(window.location.search);
const depositorId = params.get("id");
const form = document.getElementById("depositorForm");
const status = document.getElementById("formStatus");
const deletionCard = document.getElementById("deletionCard");

let original = null;

async function loadDepositor() {
  let response;
  try {
    response = await fetch("/api/depositors/" + depositorId, { headers: { Authorization: "Bearer " + token } });
  } catch {
    window.location.href = "error.html?code=503";
    return;
  }
  if (response.status === 401) {
    localStorage.removeItem("access_token");
    window.location.href = "auth/login.html";
    return;
  }
  if (response.status === 404) {
    window.location.href = "depositors.html";
    return;
  }
  if (!response.ok) {
    window.location.href = "error.html?code=" + response.status;
    return;
  }
  original = await response.json();
  previewExtra = { active_deposits: original.active_deposits, opened: original.opened };
  fillForm(original);
  deletionCard.hidden = original.active_deposits === 0;
}

async function start() {
  if (!token) {
    window.location.href = "auth/login.html";
    return;
  }
  if (!depositorId) {
    window.location.href = "depositors.html";
    return;
  }
  await loadCountries(token);
  initForm();
  await loadDepositor();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const missing = firstEmptyField();
  if (missing) {
    status.textContent = "Please fill in the " + missing.label + " field";
    status.classList.remove("is-success");
    focusField(missing.id);
    return;
  }
  let response;
  try {
    response = await fetch("/api/depositors/" + depositorId, {
      method: "PUT",
      headers: { "Content-Type": "application/json", Authorization: "Bearer " + token },
      body: JSON.stringify(collectForm()),
    });
  } catch {
    window.location.href = "error.html?code=503";
    return;
  }
  if (response.status === 401) {
    localStorage.removeItem("access_token");
    window.location.href = "auth/login.html";
    return;
  }
  if (response.status === 400) {
    const data = await response.json();
    status.textContent = data.error || "Please check the form";
    status.classList.remove("is-success");
    return;
  }
  if (!response.ok) {
    window.location.href = "error.html?code=" + response.status;
    return;
  }
  window.location.href = "depositors.html";
});

document.getElementById("cancelButton").addEventListener("click", () => {
  if (original) {
    fillForm(original);
    status.textContent = "";
    status.classList.remove("is-success");
  }
});

document.getElementById("deleteButton").addEventListener("click", async () => {
  let response;
  try {
    response = await fetch("/api/depositors/" + depositorId, {
      method: "DELETE",
      headers: { Authorization: "Bearer " + token },
    });
  } catch {
    window.location.href = "error.html?code=503";
    return;
  }
  if (response.status === 401) {
    localStorage.removeItem("access_token");
    window.location.href = "auth/login.html";
    return;
  }
  if (response.status === 409) {
    deletionCard.hidden = false;
    status.textContent = "Deletion is impossible while there are active deposits";
    status.classList.remove("is-success");
    return;
  }
  if (!response.ok) {
    window.location.href = "error.html?code=" + response.status;
    return;
  }
  window.location.href = "depositors.html";
});

start();
