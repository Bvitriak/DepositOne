const summaryFields = [
  { key: "depositors", label: "depositors", description: "Total number of depositors" },
  { key: "deposits", label: "deposits", description: "Total number of deposits" },
  { key: "active", label: "Active", description: "Total number of active deposits" },
  { key: "portfolio", label: "portfolio", description: "Total portfolio value", money: true },
  { key: "percents", label: "Percents", description: "Total accrued interest", money: true },
];

const chartGroups = [
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

let dashboardData = null;

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

function chartValueText(value, money) {
  if (value === null || value === undefined) {
    return null;
  }
  if (money) {
    return formatMoney(value);
  }
  return String(value);
}

function sharePercent(value, total) {
  if (!total) {
    return "0%";
  }
  return (value / total * 100).toFixed(1) + "%";
}

function countLegend(group, groupData) {
  return group.legend.map((item) => ({
    name: item.name,
    color: item.color,
    value: groupData[item.key],
    text: chartValueText(groupData[item.key], group.money),
  }));
}

function shareLegend(group, groupData) {
  const total = group.legend.reduce((sum, item) => sum + Number(groupData[item.key] || 0), 0);
  return group.legend.map((item) => ({
    name: item.name,
    color: item.color,
    value: groupData[item.key],
    text: sharePercent(Number(groupData[item.key] || 0), total),
  }));
}

function render(data) {
  document.getElementById("summary").innerHTML = summaryFields
    .map((field) => summaryCard(field.label, field.description, summaryValue(field, data.summary)))
    .join("");
  document.getElementById("status").innerHTML = chartGroups
    .map((group) => {
      const groupData = data[group.key];
      if (group.share) {
        return chartCard(String(group.legend.length), group.centerLabel, shareLegend(group, groupData));
      }
      return chartCard(chartValueText(groupData.total, group.money), group.centerLabel, countLegend(group, groupData));
    })
    .join("");
  document.getElementById("depositors").innerHTML = depositorList(data.depositors);
}

async function loadDashboard() {
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "auth/login.html";
    return;
  }
  let response;
  try {
    response = await fetch("/api/dashboard", { headers: { Authorization: "Bearer " + token } });
  } catch {
    window.location.href = "error.html?code=503";
    return;
  }
  if (response.status === 401) {
    localStorage.removeItem("access_token");
    window.location.href = "auth/login.html";
    return;
  }
  if (!response.ok) {
    window.location.href = "error.html?code=" + response.status;
    return;
  }
  const data = await response.json();
  const top = await loadTopDepositors(token);
  data.depositors = top.list;
  data.summary.depositors = top.total;
  const stats = await loadDepositStats(token);
  if (!stats) {
    return;
  }
  data.summary.deposits = stats.total;
  data.summary.active = stats.active;
  data.summary.portfolio = stats.amounts.total;
  data.summary.percents = stats.accrued;
  data.statuses = stats.statuses;
  data.amounts = stats.amounts;
  dashboardData = data;
  render(data);
}

async function loadDepositStats(token) {
  let response;
  try {
    response = await fetch("/api/deposits/stats?" + currencyQuery(), { headers: { Authorization: "Bearer " + token } });
  } catch {
    window.location.href = "error.html?code=503";
    return null;
  }
  if (response.status === 401) {
    localStorage.removeItem("access_token");
    window.location.href = "auth/login.html";
    return null;
  }
  if (!response.ok) {
    window.location.href = "error.html?code=" + response.status;
    return null;
  }
  return await response.json();
}

async function loadTopDepositors(token) {
  let response;
  try {
    response = await fetch("/api/depositors?page=1&page_size=10&sort=created&order=desc", { headers: { Authorization: "Bearer " + token } });
  } catch {
    window.location.href = "error.html?code=503";
    return { list: [], total: null };
  }
  if (response.status === 401) {
    localStorage.removeItem("access_token");
    window.location.href = "auth/login.html";
    return { list: [], total: null };
  }
  if (!response.ok) {
    window.location.href = "error.html?code=" + response.status;
    return { list: [], total: null };
  }
  const result = await response.json();
  return { list: result.depositors.slice(0, 6), total: result.total };
}

loadDashboard();

const menuButton = document.getElementById("menuButton");
const menu = document.getElementById("menu");
const menuClose = document.getElementById("menuClose");
menuButton.addEventListener("click", () => menu.classList.add("open"));
menuClose.addEventListener("click", () => menu.classList.remove("open"));
menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => menu.classList.remove("open")));
