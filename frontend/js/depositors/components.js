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

function depositorSearchBar() {
  return `<div class="search-bar">
    <img class="search-bar-icon" src="../assets/img/search.svg" alt="">
    <input class="search-bar-input" id="search" type="text" placeholder="Searching in list of depositors" autocomplete="off">
  </div>`;
}

function depositorCard(depositor) {
  const fullName = escapeHtml(depositor.first_name + " " + depositor.last_name);
  return `<a class="depositor-card" href="depositor-card.html?id=${depositor.id}">
    <div class="depositor-card-head">
      <p class="depositor-card-name">${fullName}</p>
      <span class="depositor-card-badge">${depositor.active_deposits} DEPOSITS</span>
    </div>
    <div class="depositor-card-info">
      <div class="depositor-card-field">
        <span class="depositor-card-label">DOB:</span>
        <span class="depositor-card-value">${formatDate(depositor.date_of_birth)}</span>
      </div>
      <div class="depositor-card-field">
        <span class="depositor-card-label">COUNTRY:</span>
        <span class="depositor-card-value">${escapeHtml(depositor.country)}</span>
      </div>
      <div class="depositor-card-field">
        <span class="depositor-card-label">EMAIL:</span>
        <span class="depositor-card-value">${escapeHtml(depositor.email)}</span>
      </div>
      <div class="depositor-card-field">
        <span class="depositor-card-label">ADDRESS:</span>
        <span class="depositor-card-value">${escapeHtml(depositor.address)}</span>
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

function depositorList(data) {
  const isEmpty = data.depositors.length === 0;
  const grid = isEmpty
    ? `<div class="no-content"><p class="no-content-text">No Depositors Found</p></div>`
    : data.depositors.map(depositorCard).join("");
  return `<section class="depositor-list">
    <div class="depositor-list-head">
      <div class="depositor-list-heading">
        <p class="depositor-list-title">List of Depositors</p>
        <p class="depositor-list-count">${data.total} records found</p>
      </div>
      <div class="depositor-list-controls">
        <a class="add-depositor" href="new-depositor.html">Add Depositor</a>
        ${pageSizeSelect(data.page_size)}
      </div>
    </div>
    <div class="depositor-list-grid">${grid}</div>
    <div class="depositor-list-foot">${pagination(data.page, data.pages)}</div>
  </section>`;
}
