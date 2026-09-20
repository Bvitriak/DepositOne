const EMPTY_DEPOSITORS = { depositors: [], total: null };

const EMPTY_STATS = {
  total: null,
  active: null,
  accrued: null,
  statuses: { total: null, active: 0, pending: 0, closed: 0, blocked: 0 },
  amounts: { total: null, usd: 0, eur: 0, rub: 0 },
};

const SUMMARY_FIELDS = [
  { key: "depositors", label: "depositors", description: "Total number of depositors" },
  { key: "deposits", label: "deposits", description: "Total number of deposits" },
  { key: "active", label: "Active", description: "Total number of active deposits" },
  { key: "portfolio", label: "portfolio", description: "Total portfolio value", money: true },
  { key: "percents", label: "Percents", description: "Total accrued interest", money: true },
];

const CHART_GROUPS = [
  {
    key: "statuses",
    centerLabel: "Deposits",
    legend: [
      { key: "active", name: "Active", color: "#b5b5b5" },
      { key: "pending", name: "Pending", color: "#535353" },
      { key: "closed", name: "Closed", color: "#f4f7fb" },
      { key: "blocked", name: "Blocked", color: "#eee2dc" },
    ],
  },
  {
    key: "amounts",
    centerLabel: "Currency",
    share: true,
    legend: [
      { key: "usd", name: "USD", color: "#b5b5b5" },
      { key: "eur", name: "EUR", color: "#535353" },
      { key: "rub", name: "RUB", color: "#f4f7fb" },
    ],
  },
];

function summaryCard(label, description, value) {
  return `<article class="summary-card panel">
    <div class="summary-card-details">
      <p class="summary-card-label">${label}</p>
      <p class="summary-card-value">${value ?? "N/A"}</p>
    </div>
    <p class="summary-card-description">${description}</p>
  </article>`;
}

function paletteColor(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function chartCard(containerId, centerValue, centerLabel, legend) {
  const rows = legend.map((item) => `<li class="chart-legend-row">
        <span class="chart-legend-name"><span class="chart-legend-marker" style="background:${item.color}"></span>${item.name}</span>
        <span class="chart-legend-value">${item.text ?? "N/A"}</span>
      </li>`).join("");
  return `<article class="chart-card panel">
    <div class="chart-donut">
      <div class="chart-donut-ring" id="${containerId}"></div>
      <div class="chart-donut-center">
        <span class="chart-donut-value">${centerValue ?? "N/A"}</span>
        <span class="chart-donut-label">${centerLabel}</span>
      </div>
    </div>
    <ul class="chart-legend">${rows}</ul>
  </article>`;
}

function drawChart(containerId, legend) {
  if (typeof Highcharts === "undefined") {
    return;
  }
  const total = legend.reduce((sum, item) => sum + (Number(item.value) || 0), 0);
  Highcharts.chart(containerId, {
    chart: { type: "pie", backgroundColor: "transparent", margin: [0, 0, 0, 0] },
    title: { text: "" },
    credits: { enabled: false },
    legend: { enabled: false },
    tooltip: {
      backgroundColor: paletteColor("--card"),
      borderColor: paletteColor("--border"),
      style: { color: paletteColor("--white") },
      headerFormat: "",
      pointFormat: "<b>{point.name}</b>",
      enabled: total > 0,
    },
    plotOptions: {
      pie: {
        innerSize: "80%",
        borderWidth: 0,
        dataLabels: { enabled: false },
        states: { hover: { halo: { size: 0 } } },
      },
    },
    series: [{
      data: legend.map((item) => ({
        name: item.name + ": " + (item.text ?? "N/A"),
        y: total > 0 ? Number(item.value) || 0 : 1,
        color: item.color,
      })),
    }],
  });
}

function topDepositorsSection(depositors) {
  const body = depositors.length === 0
    ? `<div class="no-content"><p class="no-content-text">No Depositors Found</p></div>`
    : depositors.map((depositor) => entityCard({
        href: "/pages/depositor/depositor-card.html?id=" + depositor.id,
        name: depositor.first_name + " " + depositor.last_name,
        badge: depositor.active_deposits + " DEPOSITS",
        fields: [
          { label: "DOB:", value: formatDate(depositor.date_of_birth) },
          { label: "COUNTRY:", value: depositor.country },
          { label: "EMAIL:", value: depositor.email },
          { label: "ADDRESS:", value: depositor.address },
        ],
      })).join("");
  return `<section class="depositors">
    <div class="depositors-heading">
      <p class="depositors-title">List of Top depositors</p>
      <p class="depositors-subtitle">By the amount of the deposit portfolio</p>
    </div>
    <a class="action-button" href="/pages/depositor/depositors.html">See all Depositors<i class="action-button-arrow"></i></a>
    <div class="depositors-body">${body}</div>
  </section>`;
}

function summaryValue(field, summary) {
  const value = summary[field.key];
  if (value === null || value === undefined) {
    return null;
  }
  if (field.money) {
    return currencyMoney(value);
  }
  return value;
}

function chartValueText(value) {
  if (value === null || value === undefined) {
    return null;
  }
  return String(value);
}

function sharePercent(value, total) {
  if (!total) {
    return "0%";
  }
  return (value / total * 100).toFixed(1) + "%";
}

function groupLegend(group, groupData) {
  const total = group.legend.reduce((sum, item) => sum + Number(groupData[item.key] || 0), 0);
  return group.legend.map((item) => ({
    name: item.name,
    color: item.color,
    value: groupData[item.key],
    text: group.share ? sharePercent(Number(groupData[item.key] || 0), total) : chartValueText(groupData[item.key]),
  }));
}

function render(data) {
  document.getElementById("summary").innerHTML = SUMMARY_FIELDS
    .map((field) => summaryCard(field.label, field.description, summaryValue(field, data.summary)))
    .join("");
  const charts = CHART_GROUPS.map((group) => {
    const groupData = data[group.key];
    const center = group.share ? String(group.legend.length) : chartValueText(groupData.total);
    return { containerId: "chart-" + group.key, center: center, legend: groupLegend(group, groupData), label: group.centerLabel };
  });
  document.getElementById("status").innerHTML = charts
    .map((chart) => chartCard(chart.containerId, chart.center, chart.label, chart.legend))
    .join("");
  charts.forEach((chart) => drawChart(chart.containerId, chart.legend));
  document.getElementById("depositors").innerHTML = topDepositorsSection(data.depositors);
}

async function loadDashboard() {
  const data = await apiRead("/api/dashboard");
  if (!data) {
    return;
  }
  const top = await apiRead("/api/depositors?page=1&page_size=10&sort=created&order=desc", { silent: true }) || EMPTY_DEPOSITORS;
  const stats = await apiRead("/api/deposits/stats?" + currencyQuery(), { silent: true }) || EMPTY_STATS;
  data.depositors = top.depositors.slice(0, 6);
  data.summary.depositors = top.total;
  data.summary.deposits = stats.total;
  data.summary.active = stats.active;
  data.summary.portfolio = stats.amounts.total;
  data.summary.percents = stats.accrued;
  data.statuses = stats.statuses;
  data.amounts = stats.amounts;
  render(data);
}

loadDashboard();
