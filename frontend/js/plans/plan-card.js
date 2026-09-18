const planId = new URLSearchParams(window.location.search).get("id");

async function loadPlan() {
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "auth/login.html";
    return;
  }
  if (!planId) {
    window.location.href = "return-plans.html";
    return;
  }
  let response;
  try {
    response = await fetch("/api/plans/" + planId, { headers: { Authorization: "Bearer " + token } });
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
    window.location.href = "return-plans.html";
    return;
  }
  if (!response.ok) {
    window.location.href = "error.html?code=" + response.status;
    return;
  }
  const plan = await response.json();
  document.getElementById("summaryCards").innerHTML = summaryCards(plan);
  document.getElementById("planLayout").innerHTML = planLayout(plan);
}

loadPlan();

const menuButton = document.getElementById("menuButton");
const menu = document.getElementById("menu");
const menuClose = document.getElementById("menuClose");
menuButton.addEventListener("click", () => menu.classList.add("open"));
menuClose.addEventListener("click", () => menu.classList.remove("open"));
menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => menu.classList.remove("open")));
