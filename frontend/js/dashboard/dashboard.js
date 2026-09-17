const summaryFields = [
  { key: "depositors", label: "depositors", description: "Total number of depositors" },
  { key: "deposits", label: "deposits", description: "Total number of deposits" },
  { key: "active", label: "Active", description: "Total number of active accounts" },
  { key: "portfolio", label: "portfolio", description: "Total portfolio value" },
  { key: "percents", label: "Percents", description: "Total accrued interest" },
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
    centerLabel: "Amount",
    money: true,
    legend: [
      { key: "usd", name: "USD", color: "#b5b5b5" },
      { key: "eur", name: "EUR", color: "#535353" },
      { key: "rub", name: "RUB", color: "#f4f7fb" },
    ],
  },
];

function chartValueText(value, money) {
  if (value === null || value === undefined) {
    return null;
  }
  if (money) {
    return formatMoney(value);
  }
  return String(value);
}

function render(data) {
  document.getElementById("summary").innerHTML = summaryFields
    .map((field) => summaryCard(field.label, field.description, data.summary[field.key]))
    .join("");
  document.getElementById("status").innerHTML = chartGroups
    .map((group) => {
      const groupData = data[group.key];
      const legend = group.legend.map((item) => ({
        name: item.name,
        color: item.color,
        value: groupData[item.key],
        text: chartValueText(groupData[item.key], group.money),
      }));
      return chartCard(chartValueText(groupData.total, group.money), group.centerLabel, legend);
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
  if (stats) {
    data.summary.deposits = stats.total;
    data.statuses = stats.statuses;
    data.amounts = stats.amounts;
  }
  render(data);
}

async function loadDepositStats(token) {
  let response;
  try {
    response = await fetch("/api/deposits/stats", { headers: { Authorization: "Bearer " + token } });
  } catch {
    return null;
  }
  if (response.status === 401) {
    localStorage.removeItem("access_token");
    window.location.href = "auth/login.html";
    return null;
  }
  if (!response.ok) {
    return null;
  }
  return await response.json();
}

async function loadTopDepositors(token) {
  let response;
  try {
    response = await fetch("/api/depositors?page=1&page_size=10&sort=created&order=desc", { headers: { Authorization: "Bearer " + token } });
  } catch {
    return { list: [], total: null };
  }
  if (response.status === 401) {
    localStorage.removeItem("access_token");
    window.location.href = "auth/login.html";
    return { list: [], total: null };
  }
  if (!response.ok) {
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
