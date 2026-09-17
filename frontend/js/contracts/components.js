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

function contractSearchBar() {
  return `<div class="search-bar">
    <img class="search-bar-icon" src="../assets/img/search.svg" alt="">
    <input class="search-bar-input" id="search" type="text" placeholder="Searching in list of contracts" autocomplete="off">
  </div>`;
}

function contractCard(contract) {
  return `<a class="contract-card" href="contract-card.html?id=${contract.id}">
    <div class="contract-card-head">
      <p class="contract-card-name">№${escapeHtml(contract.contract_number)}</p>
      <span class="contract-card-badge">${escapeHtml(contract.signing_status)}</span>
    </div>
    <div class="contract-card-info">
      <div class="contract-card-field">
        <span class="contract-card-label">ID:</span>
        <span class="contract-card-value">${escapeHtml(contract.contract_code)}</span>
      </div>
      <div class="contract-card-field">
        <span class="contract-card-label">DEPOSITOR:</span>
        <span class="contract-card-value">${escapeHtml(contract.depositor)}</span>
      </div>
      <div class="contract-card-field">
        <span class="contract-card-label">DATE:</span>
        <span class="contract-card-value">${formatDate(contract.contract_date)}</span>
      </div>
      <div class="contract-card-field">
        <span class="contract-card-label">DEPOSIT ID:</span>
        <span class="contract-card-value">${escapeHtml(contract.deposit_number)}</span>
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

function contractList(data) {
  const isEmpty = data.contracts.length === 0;
  const grid = isEmpty
    ? `<div class="no-content"><p class="no-content-text">No Contracts Found</p></div>`
    : data.contracts.map(contractCard).join("");
  return `<section class="contract-list">
    <div class="contract-list-head">
      <div class="contract-list-heading">
        <p class="contract-list-title">List of Contracts</p>
        <p class="contract-list-count">${data.total} records found</p>
      </div>
      <div class="contract-list-controls">
        <a class="add-contract" href="new-contract.html">Add Contract</a>
        ${pageSizeSelect(data.page_size)}
      </div>
    </div>
    <div class="contract-list-grid">${grid}</div>
    <div class="contract-list-foot">${pagination(data.page, data.pages)}</div>
  </section>`;
}
