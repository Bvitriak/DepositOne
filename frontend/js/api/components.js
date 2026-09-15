function searchBar() {
  return `<div class="search-bar">
    <img class="search-bar-icon" src="../assets/img/search.svg" alt="">
    <input class="search-bar-input" id="search" type="text" placeholder="Searching in api list" autocomplete="off">
  </div>`;
}

function apiCard(api) {
  return `<article class="api-card">
    <div class="api-card-head">
      <p class="api-card-name">${api.name}</p>
      <span class="api-card-badge">${api.type}</span>
    </div>
    <div class="api-card-info">
      <div class="api-card-field">
        <span class="api-card-label">PATH:</span>
        <span class="api-card-value">${api.path}</span>
      </div>
      <div class="api-card-field">
        <span class="api-card-label">DESCRIPTION:</span>
        <span class="api-card-value">${api.description}</span>
      </div>
      <div class="api-card-field">
        <span class="api-card-label">AUTH:</span>
        <span class="api-card-value">${api.auth}</span>
      </div>
    </div>
  </article>`;
}

function pageSizeSelect(pageSize) {
  const sizes = [10, 25, 50];
  const options = sizes
    .map((size) => `<option value="${size}" ${size === pageSize ? "selected" : ""}>${size}</option>`)
    .join("");
  return `<div class="page-size">
    <select class="page-size-select" id="pageSize">${options}</select>
    <i class="page-size-arrow"></i>
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
