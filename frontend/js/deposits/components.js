function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatDate(isoDate) {
  const parts = isoDate.split("-");
  return parts[2] + "." + parts[1] + "." + parts[0];
}

function groupThousands(digits) {
  let result = "";
  for (let index = 0; index < digits.length; index = index + 1) {
    if (index > 0 && (digits.length - index) % 3 === 0) {
      result = result + " ";
    }
    result = result + digits[index];
  }
  return result;
}

function formatMoney(value, decimals) {
  const fixed = Number(value).toFixed(decimals);
  const parts = fixed.split(".");
  const grouped = groupThousands(parts[0]);
  if (decimals > 0) {
    return grouped + "." + parts[1];
  }
  return grouped;
}

function depositSearchBar() {
  return `<div class="search-bar">
    <img class="search-bar-icon" src="../assets/img/search.svg" alt="">
    <input class="search-bar-input" id="search" type="text" placeholder="Searching in list of deposits" autocomplete="off">
  </div>`;
}

function depositCard(deposit) {
  const deadline = formatDate(deposit.start_date) + " - " + formatDate(deposit.end_date);
  return `<a class="deposit-card" href="deposit-card.html?id=${deposit.id}">
    <div class="deposit-card-head">
      <p class="deposit-card-name">${escapeHtml(deposit.depositor)}</p>
      <span class="deposit-card-badge">${escapeHtml(deposit.status)}</span>
    </div>
    <div class="deposit-card-info">
      <div class="deposit-card-field">
        <span class="deposit-card-label">ID:</span>
        <span class="deposit-card-value">${escapeHtml(deposit.deposit_number)}</span>
      </div>
      <div class="deposit-card-field">
        <span class="deposit-card-label">INTEREST RATE:</span>
        <span class="deposit-card-value">${deposit.interest_rate}%</span>
      </div>
      <div class="deposit-card-field">
        <span class="deposit-card-label">CURRENCY:</span>
        <span class="deposit-card-value">${escapeHtml(deposit.currency)}</span>
      </div>
      <div class="deposit-card-field">
        <span class="deposit-card-label">AMOUNT:</span>
        <span class="deposit-card-value">${formatMoney(deposit.amount, 0)}</span>
      </div>
      <div class="deposit-card-field">
        <span class="deposit-card-label">DEADLINE:</span>
        <span class="deposit-card-value">${deadline}</span>
      </div>
    </div>
  </a>`;
}

function pageSizeSelect(pageSize) {
  const sizes = [10, 25, 50];
  const options = sizes
    .map((size) => `<button type="button" class="page-size-option ${size === pageSize ? "is-active" : ""}" data-size="${size}">${size}</button>`)
    .join("");
  return `<div class="page-size">
    <button type="button" class="page-size-trigger" data-page-size-trigger>
      <span class="page-size-value">${pageSize}</span>
      <i class="page-size-arrow"></i>
    </button>
    <div class="page-size-options">${options}</div>
  </div>`;
}

function pagination(page, pages) {
  let numbers = "";
  for (let current = 1; current <= pages; current = current + 1) {
    numbers += `<button class="page-button ${current === page ? "is-active" : ""}" data-page="${current}">${current}</button>`;
  }
  return `<div class="pagination-info">Page ${page} of ${pages}</div>
    <div class="pagination-control">
      <button class="page-button" data-page="prev"><i class="page-arrow page-arrow-left"></i></button>
      ${numbers}
      <button class="page-button" data-page="next"><i class="page-arrow page-arrow-right"></i></button>
    </div>`;
}

function depositList(data) {
  const isEmpty = data.deposits.length === 0;
  const grid = isEmpty
    ? `<div class="no-content"><p class="no-content-text">No Deposits Found</p></div>`
    : data.deposits.map(depositCard).join("");
  return `<section class="deposit-list">
    <div class="deposit-list-head">
      <div class="deposit-list-heading">
        <p class="deposit-list-title">List of Deposits</p>
        <p class="deposit-list-count">${data.total} records found</p>
      </div>
      <div class="deposit-list-controls">
        <a class="add-deposit" href="new-deposit.html">Add Deposit</a>
        ${pageSizeSelect(data.page_size)}
      </div>
    </div>
    <div class="deposit-list-grid">${grid}</div>
    <div class="deposit-list-foot">${pagination(data.page, data.pages)}</div>
  </section>`;
}
