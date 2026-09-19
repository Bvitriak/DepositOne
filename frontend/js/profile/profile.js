let releasedToken = "";
let profileData = null;

async function requestProfile(path, method) {
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "auth/login.html";
    return null;
  }
  let response;
  try {
    response = await fetch(path, { method: method, headers: { Authorization: "Bearer " + token } });
  } catch {
    window.location.href = "error.html?code=503";
    return null;
  }
  if (response.status === 401) {
    localStorage.removeItem("access_token");
    window.location.href = "auth/login.html";
    return null;
  }
  if (!response.ok) {
    window.location.href = "error.html?code=" + response.status;
    return null;
  }
  return response.json();
}

async function loadPage() {
  const profile = await requestProfile("/api/profile", "GET");
  if (!profile) {
    return;
  }
  const summary = await requestProfile("/api/portfolio?" + currencyQuery(), "GET");
  if (!summary) {
    return;
  }
  profileData = { profile: profile, summary: summary };
  renderProfile();
}

function renderProfile() {
  if (profileData) {
    const data = profileData;
    document.getElementById("profile").innerHTML = profilePage(data.profile, data.summary.portfolio, data.summary.operations, releasedToken);
  }
}

async function releaseToken() {
  const data = await requestProfile("/api/profile/token", "POST");
  if (!data) {
    return;
  }
  releasedToken = data.access_token;
  localStorage.setItem("access_token", releasedToken);
  document.getElementById("tokenValue").textContent = releasedToken;
}

function selectToken() {
  const range = document.createRange();
  range.selectNodeContents(document.getElementById("tokenValue"));
  const selection = window.getSelection();
  selection.removeAllRanges();
  selection.addRange(range);
}

function copyToken() {
  if (!releasedToken) {
    return;
  }
  if (!navigator.clipboard) {
    selectToken();
    return;
  }
  navigator.clipboard.writeText(releasedToken).catch(selectToken);
}

function switchLanguage() {
  const next = currentLanguage() === ENGLISH ? RUSSIAN : ENGLISH;
  localStorage.setItem("language", next);
  window.location.reload();
}

function switchCurrency() {
  localStorage.setItem("currency", nextCurrency());
  window.location.reload();
}

document.getElementById("profile").addEventListener("click", (event) => {
  if (event.target.closest("#releaseToken")) {
    releaseToken();
    return;
  }
  if (event.target.closest("#copyToken")) {
    copyToken();
    return;
  }
  if (event.target.closest("#language")) {
    switchLanguage();
    return;
  }
  if (event.target.closest("#currency")) {
    switchCurrency();
  }
});

loadPage();

const menuButton = document.getElementById("menuButton");
const menu = document.getElementById("menu");
const menuClose = document.getElementById("menuClose");
menuButton.addEventListener("click", () => menu.classList.add("open"));
menuClose.addEventListener("click", () => menu.classList.remove("open"));
menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => menu.classList.remove("open")));
