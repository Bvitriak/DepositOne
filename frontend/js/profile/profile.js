const EMPTY_SUMMARY = {
  portfolio: { depositors: "N/A", active_deposits: "N/A", total_amount: null },
  operations: { signed_contracts: "N/A", pending_contracts: "N/A", rejected_contracts: "N/A" },
};

const TOKEN_HINT = 'Click the "Release Token" button to get your JWT, and click the "Copy" button to copy the generated JWT token.';

let releasedToken = "";

function profileRow(label, value) {
  return `<p class="profile-label">${label}</p>
    <p class="profile-value">${escapeHtml(value)}</p>`;
}

function profileCard(profile) {
  return `<section class="profile-card panel">
    <div class="profile-user">
      <div class="profile-image">
        <img class="profile-avatar" src="/assets/img/profile.svg" alt="">
        <p class="profile-name">${escapeHtml(profile.nickname)}</p>
      </div>
      <div class="profile-table">
        ${profileRow("Account Id", profile.account_id)}
        ${profileRow("Nickname", profile.nickname)}
        ${profileRow("Email", profile.email)}
        ${profileRow("Status", profile.status)}
        ${profileRow("Created", profile.created)}
        ${profileRow("Last Visit", profile.last_visit)}
      </div>
    </div>
    <div class="profile-settings">
      <button class="profile-setting" id="language" type="button">
        <img class="profile-setting-icon" src="/assets/img/language.svg" alt="">
        English
      </button>
      <button class="profile-setting profile-setting-currency" id="currency" type="button">
        <img class="profile-setting-icon" src="/assets/img/${CURRENCY_ICONS[currentCurrency()]}" alt="">
        ${currentCurrency()}
      </button>
    </div>
  </section>`;
}

function statRow(label, value, extraClass) {
  return `<div class="stat-card-row ${extraClass}">
    <p class="stat-card-label">${label}</p>
    <p class="stat-card-value">${value}</p>
  </div>`;
}

function statCard(title, rows, total) {
  return `<article class="stat-card panel">
    <p class="stat-card-title">${title}</p>
    <div class="stat-card-content">
      <div class="stat-card-group">${rows}</div>
      ${total}
    </div>
  </article>`;
}

function portfolioCard(portfolio) {
  const rows = statRow("Depositors", portfolio.depositors, "") + statRow("Active Deposits", portfolio.active_deposits, "");
  return statCard("Portfolio", rows, statRow("Total Amount", currencyMoney(portfolio.total_amount), "stat-card-total"));
}

function operationsCard(operations) {
  const rows = statRow("Signed Contracts", operations.signed_contracts, "") + statRow("Pending Contracts", operations.pending_contracts, "");
  return statCard("Operations", rows, statRow("Rejected", operations.rejected_contracts, "stat-card-total"));
}

function tokenCard(token) {
  return `<article class="token-card panel">
    <div class="token-head">
      <div class="token-heading">
        <p class="token-title">JWT Access Token</p>
        <p class="token-description">The token is used to access protected endpoints and integrate with the API.</p>
      </div>
      <div class="token-buttons">
        <button class="token-button" id="releaseToken" type="button">Release Token</button>
        <button class="token-button" id="copyToken" type="button">Copy</button>
      </div>
    </div>
    <p class="token-value" id="tokenValue">${token ? escapeHtml(token) : TOKEN_HINT}</p>
  </article>`;
}

function profilePage(profile, summary) {
  return `<div class="profile">
    ${profileCard(profile)}
    <div class="profile-main">
      <div class="profile-stats">
        ${portfolioCard(summary.portfolio)}
        ${operationsCard(summary.operations)}
      </div>
      ${tokenCard(releasedToken)}
    </div>
  </div>`;
}

async function loadPage() {
  const profile = await apiRead("/api/profile");
  if (!profile) {
    return;
  }
  const summary = await apiRead("/api/portfolio?" + currencyQuery(), { silent: true }) || EMPTY_SUMMARY;
  window.history.replaceState(null, "", "/" + profile.nickname);
  document.getElementById("profile").innerHTML = profilePage(profile, summary);
}

async function releaseToken() {
  const data = await apiRead("/api/profile/token", { method: "POST" });
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
  localStorage.setItem("language", currentLanguage() === ENGLISH ? RUSSIAN : ENGLISH);
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
