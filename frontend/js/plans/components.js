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

function formatMoney(value) {
  return groupThousands(String(Math.round(Number(value))));
}

function formatPercent(value) {
  if (value === null || value === undefined) {
    return "N/A";
  }
  return value + "%";
}

function monthlyStat(label, value) {
  return `<div class="monthly-stat">
    <p class="monthly-stat-label">${label}</p>
    <p class="monthly-stat-value">${value}</p>
  </div>`;
}

function monthlyCard(monthly) {
  return `<article class="monthly-card">
    <div class="monthly-info">
      <p class="monthly-title">Monthly Results</p>
      <div class="monthly-amount-info">
        <p class="monthly-amount">${currencyMoney(monthly.amount)}</p>
        <p class="monthly-description">The total amount of all scheduled repayments on active deposits for the current month</p>
      </div>
    </div>
    <div class="monthly-stats">
      ${monthlyStat("Returns", monthly.returns)}
      ${monthlyStat("Reserve", formatPercent(monthly.reserve))}
      ${monthlyStat("Tomorrow", monthly.tomorrow)}
      ${monthlyStat("This week", monthly.this_week)}
    </div>
  </article>`;
}

function priorityCard(plan) {
  return `<a class="priority-card" href="return-plan.html?id=${plan.deposit_id}">
    <div class="priority-head">
      <span class="priority-badge">${escapeHtml(plan.deposit_number)}</span>
      <span class="priority-badge">${plan.days_left}D</span>
    </div>
    <p class="priority-name">${escapeHtml(plan.depositor)}</p>
    <div class="priority-stats">
      <div class="priority-stat">
        <span class="priority-stat-label">Percents</span>
        <span class="priority-stat-value">${formatPercent(plan.interest_rate)}</span>
      </div>
      <div class="priority-stat priority-stat-end">
        <span class="priority-stat-label">To Return</span>
        <span class="priority-stat-value">${formatMoney(plan.total_refund)} ${escapeHtml(plan.currency)}</span>
      </div>
    </div>
  </a>`;
}

function emptyPriorityCard() {
  return `<div class="priority-card">
    <div class="priority-head">
      <span class="priority-badge">N/A</span>
      <span class="priority-badge">N/A</span>
    </div>
    <p class="priority-name">N/A</p>
    <div class="priority-stats">
      <div class="priority-stat">
        <span class="priority-stat-label">Percents</span>
        <span class="priority-stat-value">N/A</span>
      </div>
      <div class="priority-stat priority-stat-end">
        <span class="priority-stat-label">To Return</span>
        <span class="priority-stat-value">N/A</span>
      </div>
    </div>
  </div>`;
}

function priorityList(plans) {
  let cards = "";
  for (let index = 0; index < 4; index = index + 1) {
    if (plans[index]) {
      cards += priorityCard(plans[index]);
    } else {
      cards += emptyPriorityCard();
    }
  }
  return `<section class="priority">
    <p class="priority-title">Priority List</p>
    <div class="priority-list">${cards}</div>
  </section>`;
}

function planSearchBar() {
  return `<div class="search-bar">
    <img class="search-bar-icon" src="../assets/img/search.svg" alt="">
    <input class="search-bar-input" id="search" type="text" placeholder="Searching in list of returning plan" autocomplete="off">
  </div>`;
}

function planCard(plan) {
  return `<a class="plan-card" href="return-plan.html?id=${plan.deposit_id}">
    <div class="plan-card-head">
      <p class="plan-card-name">${escapeHtml(plan.deposit_number)}</p>
      <span class="plan-card-badge">${plan.interest_rate}% AI</span>
    </div>
    <div class="plan-card-info">
      <div class="plan-card-field">
        <span class="plan-card-label">PAYOUT DATE:</span>
        <span class="plan-card-value">${formatDate(plan.payout_date)}</span>
      </div>
      <div class="plan-card-field">
        <span class="plan-card-label">TOTAL REFUND:</span>
        <span class="plan-card-value">${formatMoney(plan.total_refund)} ${escapeHtml(plan.currency)}</span>
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

function planList(data) {
  const isEmpty = data.plans.length === 0;
  const grid = isEmpty
    ? `<div class="no-content"><p class="no-content-text">No Returning Plans Found</p></div>`
    : data.plans.map(planCard).join("");
  return `<section class="plan-list">
    <div class="plan-list-head">
      <div class="plan-list-heading">
        <p class="plan-list-title">List of returning plan</p>
        <p class="plan-list-count">${data.total} records found</p>
      </div>
      ${pageSizeSelect(data.page_size)}
    </div>
    <div class="plan-list-grid">${grid}</div>
    <div class="plan-list-foot">${pagination(data.page, data.pages)}</div>
  </section>`;
}
