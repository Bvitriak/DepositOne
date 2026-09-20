function monthlyStat(label, value) {
  return `<div class="monthly-stat panel">
    <p class="monthly-stat-label">${label}</p>
    <p class="monthly-stat-value">${value}</p>
  </div>`;
}

function monthlyCard(monthly) {
  return `<article class="monthly-card panel">
    <div class="monthly-information">
      <p class="monthly-title">Monthly Results</p>
      <div class="monthly-amount-information">
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
  if (!plan) {
    return `<div class="priority-card panel">
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
  return `<a class="priority-card panel" href="/pages/plan/return-plan.html?id=${plan.deposit_id}">
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

function priorityList(plans) {
  let cards = "";
  for (let index = 0; index < 4; index = index + 1) {
    cards += priorityCard(plans[index]);
  }
  return `<section class="priority">
    <p class="priority-title">Priority List</p>
    <div class="priority-list">${cards}</div>
  </section>`;
}

function planCard(plan) {
  return entityCard({
    href: "/pages/plan/return-plan.html?id=" + plan.deposit_id,
    name: plan.deposit_number,
    badge: plan.interest_rate + "% AI",
    fields: [
      { label: "PAYOUT DATE:", value: formatDate(plan.payout_date) },
      { label: "TOTAL REFUND:", value: formatMoney(plan.total_refund) + " " + plan.currency },
    ],
  });
}

function planList(data) {
  return entityList({
    title: "List of returning plan",
    total: data.total,
    emptyText: "No Returning Plans Found",
    cards: data.plans.map(planCard),
  });
}

async function loadPlans() {
  await loadList("/api/plans", "planList", planList);
}

const EMPTY_MONTHLY = { amount: null, returns: "N/A", reserve: null, tomorrow: "N/A", this_week: "N/A" };

async function loadSummary() {
  const data = await apiRead("/api/plans/summary?" + currencyQuery(), { silent: true });
  const monthly = data ? data.monthly : EMPTY_MONTHLY;
  const priority = data ? data.priority : [];
  document.getElementById("monthly").innerHTML = monthlyCard(monthly);
  document.getElementById("priority").innerHTML = priorityList(priority);
}

async function loadPage() {
  await loadSummary();
  await loadPlans();
}

connectList({
  containerId: "planList",
  placeholder: "Searching in list of returning plan",
  reload: loadPlans,
  sortOrder: "asc",
  sortOptions: [
    { value: "payout", text: "Payout date" },
    { value: "amount", text: "Amount" },
    { value: "rate", text: "Interest rate" },
    { value: "name", text: "Depositor" },
  ],
});
loadPage();
