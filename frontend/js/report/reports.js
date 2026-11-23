const CASH_FLOW_PERIODS = ["Today", "Month", "Year", "5 Years"];

function cashFlowRow(label, value) {
  return `<div class="cash-flow-row">
    <span class="cash-flow-label">${label}</span>
    <span class="cash-flow-value">${currencyMoney(value)}</span>
  </div>`;
}

function cashFlowCard(card) {
  return `<article class="cash-flow-card panel">
    <p class="cash-flow-period">${escapeHtml(card.period)}</p>
    <div class="cash-flow-content">
      <div class="cash-flow-group">
        ${cashFlowRow("Opening Balance", card.opening)}
        ${cashFlowRow("Total Inflow", card.inflow)}
        ${cashFlowRow("Expected Outflow", card.outflow)}
      </div>
      <div class="cash-flow-row cash-flow-total">
        <span class="cash-flow-label">Net Liquidity</span>
        <span class="cash-flow-value">${currencyMoney(card.net)}</span>
      </div>
    </div>
  </article>`;
}

function cashFlowSection(cards) {
  return `<section class="cash-flow">
    <p class="cash-flow-title">Key cash flow indicators</p>
    <div class="cash-flow-list">${cards.map(cashFlowCard).join("")}</div>
  </section>`;
}

function emptyCashFlow() {
  return CASH_FLOW_PERIODS.map((period) => ({ period: period, opening: null, inflow: null, outflow: null, net: null }));
}

function reportCard(report) {
  return entityCard({
    name: report.depositor,
    badge: report.deposits + " DEPOSITS",
    fields: [
      { label: "TOTAL AMOUNT:", value: currencyAmount(formatMoney(report.total_amount)) },
      { label: "TOTAL INCOME:", value: currencyAmount(formatMoney(report.total_income)) },
    ],
  });
}

function reportList(data) {
  return entityList({
    title: "List of Reports",
    total: data.total,
    emptyText: "No Reports Found",
    cards: data.reports.map(reportCard),
  });
}

async function loadReports() {
  await loadList("/api/reports", "reportList", reportList, currencyQuery());
}

async function loadCashFlow() {
  const data = await apiRead("/api/reports/cash-flow?" + currencyQuery(), { silent: true });
  const cards = data ? data.cash_flow : emptyCashFlow();
  document.getElementById("cashFlow").innerHTML = cashFlowSection(cards);
}

async function loadPage() {
  await loadCashFlow();
  await loadReports();
}

connectList({
  containerId: "reportList",
  placeholder: "Searching in list of reports",
  reload: loadReports,
  sortOrder: "desc",
  sortOptions: [
    { value: "amount", text: "Total amount" },
    { value: "income", text: "Total income" },
    { value: "deposits", text: "Deposits" },
    { value: "name", text: "Depositor" },
  ],
});
loadPage();
