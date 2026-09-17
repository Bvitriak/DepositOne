let search = "";
let page = 1;
let pageSize = 10;

async function loadContracts() {
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "auth/login.html";
    return;
  }
  const query =
    "?search=" + encodeURIComponent(search) + "&page=" + page + "&page_size=" + pageSize;
  let response;
  try {
    response = await fetch("/api/contracts" + query, { headers: { Authorization: "Bearer " + token } });
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
  document.getElementById("contractList").innerHTML = contractList(data);
}

document.getElementById("searchArea").innerHTML = contractSearchBar();
document.getElementById("search").addEventListener("input", (event) => {
  search = event.target.value;
  page = 1;
  loadContracts();
});

const listElement = document.getElementById("contractList");
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
    loadContracts();
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
  loadContracts();
});
document.addEventListener("click", (event) => {
  if (!event.target.closest(".page-size")) {
    const openSize = listElement.querySelector(".page-size.open");
    if (openSize) {
      openSize.classList.remove("open");
    }
  }
});

loadContracts();

const menuButton = document.getElementById("menuButton");
const menu = document.getElementById("menu");
const menuClose = document.getElementById("menuClose");
menuButton.addEventListener("click", () => menu.classList.add("open"));
menuClose.addEventListener("click", () => menu.classList.remove("open"));
menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => menu.classList.remove("open")));
