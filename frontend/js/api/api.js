let allApis = [];
let query = "";
let method = "All";
let pageSize = 10;
let page = 1;
let pages = 1;

function matchesQuery(api) {
  const value = query.trim().toLowerCase();
  if (value === "") {
    return true;
  }
  const fields = [api.name, api.type, api.path, api.auth, api.description, api.module, api.service];
  return fields.some((field) => field.toLowerCase().includes(value));
}

function matchesMethod(api) {
  return method === "All" || api.type === method;
}

function applyState() {
  const filtered = allApis.filter((api) => matchesQuery(api) && matchesMethod(api));
  const total = filtered.length;
  pages = Math.max(1, Math.ceil(total / pageSize));
  if (page > pages) {
    page = pages;
  }
  const start = (page - 1) * pageSize;
  const visible = filtered.slice(start, start + pageSize);
  document.getElementById("methodArea").innerHTML = methodFilter(method);
  document.getElementById("apiList").innerHTML = apiList(visible, total, page, pages, pageSize);
}

async function loadApiList() {
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "auth/login.html";
    return;
  }
  let response;
  try {
    response = await fetch("/api/apis", { headers: { Authorization: "Bearer " + token } });
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
  allApis = data.apis;
  applyState();
}

function selectPath(button) {
  const range = document.createRange();
  range.selectNodeContents(button.parentElement.querySelector(".api-card-path"));
  const selection = window.getSelection();
  selection.removeAllRanges();
  selection.addRange(range);
}

function copyPath(button) {
  if (!navigator.clipboard) {
    selectPath(button);
    return;
  }
  navigator.clipboard
    .writeText(button.dataset.copy)
    .then(() => {
      button.classList.add("is-copied");
      setTimeout(() => button.classList.remove("is-copied"), 1500);
    })
    .catch(() => selectPath(button));
}

document.getElementById("searchArea").innerHTML = searchBar();

document.getElementById("search").addEventListener("input", (event) => {
  query = event.target.value;
  page = 1;
  applyState();
});

document.getElementById("methodArea").addEventListener("click", (event) => {
  const chip = event.target.closest(".method-chip");
  if (!chip) {
    return;
  }
  method = chip.dataset.method;
  page = 1;
  applyState();
});

const apiListElement = document.getElementById("apiList");
apiListElement.addEventListener("click", (event) => {
  const copy = event.target.closest(".api-card-copy");
  if (copy) {
    copyPath(copy);
    return;
  }
  const trigger = event.target.closest("[data-page-size-trigger]");
  if (trigger) {
    trigger.parentElement.classList.toggle("open");
    return;
  }
  const option = event.target.closest(".page-size-option");
  if (option) {
    pageSize = Number(option.dataset.size);
    page = 1;
    applyState();
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
    page = Math.min(pages, page + 1);
  } else {
    page = Number(value);
  }
  applyState();
});
document.addEventListener("click", (event) => {
  if (!event.target.closest(".page-size")) {
    const openSize = apiListElement.querySelector(".page-size.open");
    if (openSize) {
      openSize.classList.remove("open");
    }
  }
});

loadApiList();

const menuButton = document.getElementById("menuButton");
const menu = document.getElementById("menu");
const menuClose = document.getElementById("menuClose");
menuButton.addEventListener("click", () => menu.classList.add("open"));
menuClose.addEventListener("click", () => menu.classList.remove("open"));
menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => menu.classList.remove("open")));
