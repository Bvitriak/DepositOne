const token = localStorage.getItem("access_token");
const form = document.getElementById("contractForm");
const status = document.getElementById("formStatus");

async function start() {
  if (!token) {
    window.location.href = "auth/login.html";
    return;
  }
  await loadDeposits(token);
  initForm();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const missing = firstEmptyField();
  if (missing) {
    status.textContent = "Please fill in the " + missing.label + " field";
    focusField(missing.id);
    return;
  }
  status.textContent = "";
  let response;
  try {
    response = await fetch("/api/contracts", {
      method: "POST",
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
    return;
  }
  if (!response.ok) {
    window.location.href = "error.html?code=" + response.status;
    return;
  }
  window.location.href = "contracts.html";
});

document.getElementById("cancelButton").addEventListener("click", () => {
  window.location.href = "contracts.html";
});

start();
