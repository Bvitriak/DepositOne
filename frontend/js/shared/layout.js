const NAVIGATION_LINKS = [
  { text: "Dashboard", href: "/dashboard" },
  { text: "Depositor", href: "/pages/depositor/depositors.html" },
  { text: "Deposit", href: "/pages/deposit/deposits.html" },
  { text: "Contract", href: "/pages/contract/contracts.html" },
  { text: "Report", href: "/pages/report/reports.html" },
  { text: "Return Plan", href: "/pages/plan/return-plans.html" },
];

const PROFILE_LINK = { text: "Profile", href: "/profile" };

function navigationLinks(className) {
  return NAVIGATION_LINKS.concat(PROFILE_LINK)
    .map((link) => `<a class="${className}" href="${link.href}">${link.text}</a>`)
    .join("");
}

function backgroundMarkup() {
  return `<div class="background">
    <img class="background-glow background-glow-sunset" src="/assets/img/glow-sunset.svg" alt="">
    <img class="background-glow background-glow-ambient" src="/assets/img/glow-ambient.svg" alt="">
    <div class="stars" id="stars"></div>
    <img class="background-mountain background-mountain-far" src="/assets/img/mountains-far.svg" alt="">
    <img class="background-mountain background-mountain-middle" src="/assets/img/mountains-mid.svg" alt="">
    <img class="background-mountain background-mountain-near" src="/assets/img/mountains-near.svg" alt="">
    <img class="background-mountain background-mountain-front" src="/assets/img/mountains-foreground.svg" alt="">
    <div class="background-overlay"></div>
  </div>`;
}

function headerMarkup() {
  return `<header class="page-header">
    <nav class="page-navigation">${navigationLinks("page-navigation-link")}</nav>
    <button class="page-menu-button" id="menuButton" aria-label="Open menu">
      <img src="/assets/img/menu.svg" alt="">
    </button>
  </header>`;
}

function footerMarkup() {
  const links = NAVIGATION_LINKS.map((link) => `<a href="${link.href}">${link.text}</a>`).join("");
  return `<footer class="footer-section">
    <div class="container">
      <div class="footer">
        <div class="footer-top">
          <div class="footer-brand">
            <a class="footer-logo" href="/index.html" aria-label="DepositOne home">
              <img class="footer-logo-image" src="/assets/img/logo.svg" alt="">
            </a>
            <p class="footer-description">DepositOne is an internal platform for the operational tracking of deposit agreements and the viewing of analytics.</p>
          </div>
          <nav class="footer-navigation">${links}</nav>
        </div>
        <div class="footer-line"></div>
        <div class="footer-bottom">
          <p class="copyright">© 2026 DepositOne. All rights reserved.</p>
          <div class="footer-utility">
            <a href="/about">About</a>
            <a href="/pages/api/api.html">API</a>
            <a href="/pages/support/support.html">Support</a>
          </div>
        </div>
      </div>
    </div>
  </footer>`;
}

function menuMarkup() {
  return `<div class="page-menu" id="menu">
    <button class="page-menu-close" id="menuClose" aria-label="Close menu"><img src="/assets/img/close.svg" alt=""></button>
    <nav class="page-menu-navigation">${navigationLinks("")}</nav>
  </div>`;
}

function createStars() {
  const stars = document.getElementById("stars");
  if (!stars) {
    return;
  }
  for (let index = 0; index < 25; index = index + 1) {
    const star = document.createElement("span");
    star.className = "star";
    star.style.left = Math.random() * 100 + "%";
    star.style.top = Math.random() * 45 + "%";
    stars.appendChild(star);
  }
}

function connectMenu() {
  const menuButton = document.getElementById("menuButton");
  const menu = document.getElementById("menu");
  const menuClose = document.getElementById("menuClose");
  if (!menuButton || !menu || !menuClose) {
    return;
  }
  menuButton.addEventListener("click", () => menu.classList.add("open"));
  menuClose.addEventListener("click", () => menu.classList.remove("open"));
  menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => menu.classList.remove("open")));
}

function renderLayout() {
  const layout = document.body.dataset.layout;
  if (layout === "page") {
    const scene = document.querySelector(".page-scene");
    scene.insertAdjacentHTML("afterbegin", backgroundMarkup() + headerMarkup());
    scene.insertAdjacentHTML("afterend", footerMarkup());
    document.body.insertAdjacentHTML("beforeend", menuMarkup());
  }
  if (layout === "home") {
    document.querySelector(".call-to-action-section").insertAdjacentHTML("afterend", footerMarkup());
  }
  if (layout === "plain") {
    document.querySelector("main").insertAdjacentHTML("afterbegin", backgroundMarkup());
  }
  createStars();
  connectMenu();
}

renderLayout();
