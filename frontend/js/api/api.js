let allApis = [];
let query = "";
let pageSize = 10;
let page = 1;
let pages = 1;

function matchesQuery(api) {
  const value = query.trim().toLowerCase();
  if (value === "") {
    return true;
  }
  const fields = [api.name, api.type, api.path, api.auth, api.description];
  return fields.some((field) => field.toLowerCase().includes(value));
}

function applyState() {
  const filtered = allApis.filter(matchesQuery);
  const total = filtered.length;
  pages = Math.max(1, Math.ceil(total / pageSize));
  if (page > pages) {
    page = pages;
  }
  const start = (page - 1) * pageSize;
  const visible = filtered.slice(start, start + pageSize);
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

document.getElementById("searchArea").innerHTML = searchBar();

document.getElementById("search").addEventListener("input", (event) => {
  query = event.target.value;
  page = 1;
  applyState();
});

const apiListElement = document.getElementById("apiList");
apiListElement.addEventListener("change", (event) => {
  if (event.target.id === "pageSize") {
    pageSize = Number(event.target.value);
    page = 1;
    applyState();
  }
});
apiListElement.addEventListener("click", (event) => {
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

loadApiList();

const menuButton = document.getElementById("menuButton");
const menu = document.getElementById("menu");
const menuClose = document.getElementById("menuClose");
menuButton.addEventListener("click", () => menu.classList.add("open"));
menuClose.addEventListener("click", () => menu.classList.remove("open"));
menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => menu.classList.remove("open")));
