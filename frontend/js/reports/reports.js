const periods = ["Today", "Month", "Year", "5 Years"];
let search = "";
let page = 1;
let pageSize = 10;
let cashFlowCards = [];

function emptyCashFlow() {
  return periods.map((period) => ({ period: period, opening: null, inflow: null, outflow: null, net: null }));
}

async function loadCashFlow(token) {
  let response;
  try {
    response = await fetch("/api/reports/cash-flow?" + currencyQuery(), { headers: { Authorization: "Bearer " + token } });
  } catch {
    return emptyCashFlow();
  }
  if (response.status === 401) {
    localStorage.removeItem("access_token");
    window.location.href = "auth/login.html";
    return emptyCashFlow();
  }
  if (!response.ok) {
    return emptyCashFlow();
  }
  const data = await response.json();
  return data.cash_flow;
}

async function loadReports() {
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "auth/login.html";
    return;
  }
  const query =
    "?search=" + encodeURIComponent(search) + "&page=" + page + "&page_size=" + pageSize + "&" + currencyQuery();
  let response;
  try {
    response = await fetch("/api/reports" + query, { headers: { Authorization: "Bearer " + token } });
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
  const data = await response.json();
  page = data.page;
  document.getElementById("reportList").innerHTML = reportList(data);
}

async function loadPage() {
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "auth/login.html";
    return;
  }
  cashFlowCards = await loadCashFlow(token);
  renderCashFlow();
  await loadReports();
}

function renderCashFlow() {
  document.getElementById("cashFlow").innerHTML = cashFlow(cashFlowCards);
}

document.getElementById("searchArea").innerHTML = reportSearchBar();
document.getElementById("search").addEventListener("input", (event) => {
  search = event.target.value;
  page = 1;
  loadReports();
});

const listElement = document.getElementById("reportList");
listElement.addEventListener("click", (event) => {
  const trigger = event.target.closest("[data-page-size-trigger]");
  if (trigger) {
    trigger.parentElement.classList.toggle("open");
    return;
  }
  const option = event.target.closest(".page-size-option");
  if (option) {
    pageSize = Number(option.dataset.size);
    page = 1;
    loadReports();
    return;
  }
  const button = event.target.closest(".page-button");
  if (!button) {
    return;
  }
  const value = button.dataset.page;
  if (value === "prev") {
    page = Math.max(1, page - 1);
  } else if (value === "next") {
    page = page + 1;
  } else {
    page = Number(value);
  }
  loadReports();
});
document.addEventListener("click", (event) => {
  if (!event.target.closest(".page-size")) {
    const openSize = listElement.querySelector(".page-size.open");
    if (openSize) {
      openSize.classList.remove("open");
    }
  }
});

loadPage();

const menuButton = document.getElementById("menuButton");
const menu = document.getElementById("menu");
const menuClose = document.getElementById("menuClose");
menuButton.addEventListener("click", () => menu.classList.add("open"));
menuClose.addEventListener("click", () => menu.classList.remove("open"));
menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => menu.classList.remove("open")));
