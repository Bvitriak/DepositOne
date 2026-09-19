const METHODS = ["All", "GET", "POST", "PUT", "DELETE"];

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function searchBar() {
  return `<div class="search-bar">
    <img class="search-bar-icon" src="../assets/img/search.svg" alt="">
    <input class="search-bar-input" id="search" type="text" placeholder="Searching in api list" autocomplete="off">
  </div>`;
}

function methodFilter(method) {
  const buttons = METHODS.map((item) => {
    const active = item === method ? "is-active" : "";
    return `<button class="method-chip ${active}" type="button" data-method="${item}">${item}</button>`;
  }).join("");
  return `<div class="method-filter">${buttons}</div>`;
}

function apiCard(api) {
  const auth = api.auth === "JWT" ? "JWT" : "Public";
  return `<article class="api-card">
    <div class="api-card-head">
      <span class="api-method api-method-${api.type.toLowerCase()}">${api.type}</span>
      <code class="api-card-path">${escapeHtml(api.path)}</code>
      <button class="api-card-copy" type="button" data-copy="${escapeHtml(api.path)}" aria-label="Copy">
        <img class="api-card-copy-icon" src="../assets/img/copy.svg" alt="">
        <img class="api-card-copy-icon api-card-copy-done" src="../assets/img/check.svg" alt="">
      </button>
    </div>
    <div class="api-card-body">
      <p class="api-card-name">${escapeHtml(api.name)}</p>
      <p class="api-card-description">${escapeHtml(api.description)}</p>
    </div>
    <div class="api-card-tags">
      <span class="api-tag">${escapeHtml(api.module)}</span>
      <span class="api-tag">${escapeHtml(api.service)}</span>
      <span class="api-tag api-tag-auth">${auth}</span>
    </div>
  </article>`;
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

function apiList(apis, total, page, pages, pageSize) {
  const isEmpty = apis.length === 0;
  const count = isEmpty ? "N/A records found" : total + " records found";
  const grid = isEmpty
    ? `<div class="no-content"><p class="no-content-text">No Information</p></div>`
    : apis.map((api) => apiCard(api)).join("");
  return `<section class="api-list">
    <div class="api-list-head">
      <div class="api-list-heading">
        <p class="api-list-title">Rest API list</p>
        <p class="api-list-count">${count}</p>
      </div>
      ${pageSizeSelect(pageSize)}
    </div>
    <div class="api-list-grid">${grid}</div>
    <div class="api-list-foot">${pagination(page, pages)}</div>
  </section>`;
}
