const TOKEN_HINT = 'Click the "Release Token" button to get your JWT, and click the "Copy" button to copy the generated JWT token.';

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function profileRow(label, value) {
  return `<p class="profile-label">${label}</p>
    <p class="profile-value">${escapeHtml(value)}</p>`;
}

function profileCard(profile) {
  return `<section class="profile-card">
    <div class="profile-user">
      <div class="profile-image">
        <img class="profile-avatar" src="../assets/img/profile.svg" alt="">
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
        <img class="profile-setting-icon" src="../assets/img/language.svg" alt="">
        English
      </button>
      <button class="profile-setting profile-setting-currency" id="currency" type="button">
        <img class="profile-setting-icon" src="../assets/img/${CURRENCY_ICONS[currentCurrency()]}" alt="">
        ${currentCurrency()}
      </button>
    </div>
  </section>`;
}

function statRow(label, value) {
  return `<div class="stat-card-row">
    <p class="stat-card-label">${label}</p>
    <p class="stat-card-value">${value}</p>
  </div>`;
}

function statTotalRow(label, value) {
  return `<div class="stat-card-row stat-card-total">
    <p class="stat-card-label">${label}</p>
    <p class="stat-card-value">${value}</p>
  </div>`;
}

function statCard(title, rows, total) {
  return `<article class="stat-card">
    <p class="stat-card-title">${title}</p>
    <div class="stat-card-content">
      <div class="stat-card-group">${rows}</div>
      ${total}
    </div>
  </article>`;
}

function portfolioCard(portfolio) {
  const rows = statRow("Depositors", portfolio.depositors) + statRow("Active Deposits", portfolio.active_deposits);
  return statCard("Portfolio", rows, statTotalRow("Total Amount", currencyMoney(portfolio.total_amount)));
}

function operationsCard(operations) {
  const rows = statRow("Signed Contracts", operations.signed_contracts) + statRow("Pending Contracts", operations.pending_contracts);
  return statCard("Operations", rows, statTotalRow("Rejected", operations.rejected_contracts));
}

function tokenCard(token) {
  return `<article class="token-card">
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

function profilePage(profile, portfolio, operations, token) {
  return `<div class="profile">
    ${profileCard(profile)}
    <div class="profile-main">
      <div class="profile-stats">
        ${portfolioCard(portfolio)}
        ${operationsCard(operations)}
      </div>
      ${tokenCard(token)}
    </div>
  </div>`;
}
