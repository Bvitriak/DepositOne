const token = localStorage.getItem("access_token");
const params = new URLSearchParams(window.location.search);
const contractId = params.get("id");
const form = document.getElementById("contractForm");
const status = document.getElementById("formStatus");

let original = null;

async function loadContract() {
  let response;
  try {
    response = await fetch("/api/contracts/" + contractId, { headers: { Authorization: "Bearer " + token } });
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
    window.location.href = "contracts.html";
    return;
  }
  if (!response.ok) {
    window.location.href = "error.html?code=" + response.status;
    return;
  }
  original = await response.json();
  fillForm(original);
}

async function start() {
  if (!token) {
    window.location.href = "auth/login.html";
    return;
  }
  if (!contractId) {
    window.location.href = "contracts.html";
    return;
  }
  await loadDeposits(token);
  initForm();
  await loadContract();
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
    response = await fetch("/api/contracts/" + contractId, {
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
  window.location.href = "contracts.html";
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
    response = await fetch("/api/contracts/" + contractId, {
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
  if (!response.ok) {
    window.location.href = "error.html?code=" + response.status;
    return;
  }
  window.location.href = "contracts.html";
});

start();
