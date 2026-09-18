function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
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

function formatMoney(value) {
  return groupThousands(String(Math.round(Number(value))));
}

function formatCompactMoney(value) {
  const number = Number(value);
  const absolute = Math.abs(number);
  if (absolute >= 1000000000) {
    return (number / 1000000000).toFixed(2) + " B";
  }
  if (absolute >= 1000000) {
    return (number / 1000000).toFixed(2) + " M";
  }
  if (absolute >= 1000) {
    return (number / 1000).toFixed(2) + " K";
  }
  return number.toFixed(2);
}

function cashFlowAmount(value, withCurrency) {
  if (value === null || value === undefined) {
    return "N/A";
  }
  if (withCurrency) {
    return "$" + formatCompactMoney(value);
  }
  return formatCompactMoney(value);
}

function reportSearchBar() {
  return `<div class="search-bar">
    <img class="search-bar-icon" src="../assets/img/search.svg" alt="">
    <input class="search-bar-input" id="search" type="text" placeholder="Searching in list of reports" autocomplete="off">
  </div>`;
}

function cashFlowCard(card) {
  return `<article class="cash-flow-card">
    <p class="cash-flow-period">${escapeHtml(card.period)}</p>
    <div class="cash-flow-content">
      <div class="cash-flow-group">
        <div class="cash-flow-row">
          <span class="cash-flow-label">Total Inflow</span>
          <span class="cash-flow-value">${cashFlowAmount(card.inflow, true)}</span>
        </div>
        <div class="cash-flow-row">
          <span class="cash-flow-label">Expected Outflow</span>
          <span class="cash-flow-value">${cashFlowAmount(card.outflow, true)}</span>
        </div>
      </div>
      <div class="cash-flow-row cash-flow-total">
        <span class="cash-flow-label">Net Liquidity</span>
        <span class="cash-flow-value">${cashFlowAmount(card.net, false)}</span>
      </div>
    </div>
  </article>`;
}

function cashFlow(cards) {
  return `<section class="cash-flow">
    <p class="cash-flow-title">Key cash flow indicators</p>
    <div class="cash-flow-list">${cards.map(cashFlowCard).join("")}</div>
  </section>`;
}

function reportCard(report) {
  return `<article class="report-card">
    <div class="report-card-head">
      <p class="report-card-name">${escapeHtml(report.depositor)}</p>
      <span class="report-card-badge">${report.deposits} DEPOSITS</span>
    </div>
    <div class="report-card-info">
      <div class="report-card-field">
        <span class="report-card-label">TOTAL AMOUNT:</span>
        <span class="report-card-value">${formatMoney(report.total_amount)}</span>
      </div>
      <div class="report-card-field">
        <span class="report-card-label">TOTAL INCOME:</span>
        <span class="report-card-value">${formatMoney(report.total_income)}</span>
      </div>
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

function reportList(data) {
  const isEmpty = data.reports.length === 0;
  const count = isEmpty ? "N/A records found" : data.total + " records found";
  const grid = isEmpty
    ? `<div class="no-content"><p class="no-content-text">No Reports Found</p></div>`
    : data.reports.map(reportCard).join("");
  return `<section class="report-list">
    <div class="report-list-head">
      <div class="report-list-heading">
        <p class="report-list-title">List of Reports</p>
        <p class="report-list-count">${count}</p>
      </div>
      ${pageSizeSelect(data.page_size)}
    </div>
    <div class="report-list-grid">${grid}</div>
    <div class="report-list-foot">${pagination(data.page, data.pages)}</div>
  </section>`;
}
