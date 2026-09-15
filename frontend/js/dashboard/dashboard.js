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
    legend: [
      { key: "active", name: "Active", color: "#b5b5b5" },
      { key: "pending", name: "Pending", color: "#535353" },
      { key: "closed", name: "Closed", color: "#f4f7fb" },
      { key: "blocked", name: "Blocked", color: "#eee2dc" },
    ],
  },
  {
    key: "currencies",
    legend: [
      { key: "usd", name: "USD", color: "#b5b5b5" },
      { key: "eur", name: "EUR", color: "#535353" },
      { key: "rub", name: "RUB", color: "#f4f7fb" },
    ],
  },
];

function render(data) {
  document.getElementById("summary").innerHTML = summaryFields
    .map((field) => summaryCard(field.label, field.description, data.summary[field.key]))
    .join("");
  document.getElementById("status").innerHTML = chartGroups
    .map((group) => {
      const groupData = data[group.key];
      const legend = group.legend.map((item) => ({ name: item.name, color: item.color, value: groupData[item.key] }));
      return chartCard(groupData.total, legend);
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
  render(await response.json());
}

loadDashboard();

const menuButton = document.getElementById("menuButton");
const menu = document.getElementById("menu");
const menuClose = document.getElementById("menuClose");
menuButton.addEventListener("click", () => menu.classList.add("open"));
menuClose.addEventListener("click", () => menu.classList.remove("open"));
menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => menu.classList.remove("open")));
