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

function formatMoney(value, decimals) {
  const fixed = Number(value).toFixed(decimals);
  const parts = fixed.split(".");
  const grouped = groupThousands(parts[0]);
  if (decimals > 0) {
    return grouped + "." + parts[1];
  }
  return grouped;
}

function monthsBetween(startIso, endIso) {
  const start = startIso.split("-");
  const end = endIso.split("-");
  let months = (Number(end[0]) - Number(start[0])) * 12 + (Number(end[1]) - Number(start[1]));
  if (Number(end[2]) < Number(start[2])) {
    months = months - 1;
  }
  return months;
}

function termText(months) {
  if (months === 1) {
    return "1 month";
  }
  return months + " months";
}

const REQUIRED_FIELDS = [
  { id: "depositor_id", label: "Depositor" },
  { id: "status", label: "Status" },
  { id: "currency_id", label: "Currency" },
  { id: "amount", label: "Amount" },
  { id: "interest_rate", label: "Interest Rate" },
  { id: "start_date", label: "Start Date" },
  { id: "end_date", label: "End Date" },
];

let calendars = {};
let depositNumber = "";
let previewAccrued = null;

function getFormValues() {
  const currencySelect = document.querySelector('[data-select="currency_id"]');
  const currencyId = currencySelect.querySelector("input[type=hidden]").value;
  const currencyText = currencySelect.querySelector("[data-text]").textContent;
  return {
    depositor_id: document.getElementById("depositor_id").value,
    currency_id: currencyId,
    currency: currencyId ? currencyText : "",
    status: document.getElementById("status").value,
    amount: document.getElementById("amount").value.trim(),
    interest_rate: document.getElementById("interest_rate").value.trim(),
    start_date: document.getElementById("start_date").value,
    end_date: document.getElementById("end_date").value,
  };
}

function previewRow(label, value) {
  const shown = value === "" || value === null || value === undefined ? "–" : value;
  return `<div class="data-card-row">
    <span class="data-card-label">${label}</span>
    <span class="data-card-value">${escapeHtml(shown)}</span>
  </div>`;
}

function renderPreview() {
  const values = getFormValues();
  const hasAmount = values.amount !== "";
  const hasRate = values.interest_rate !== "";
  const amountNumber = Number(values.amount);
  const rateNumber = Number(values.interest_rate);
  let term = null;
  if (values.start_date && values.end_date && values.end_date > values.start_date) {
    term = monthsBetween(values.start_date, values.end_date);
  }
  let accruals = null;
  let toPay = null;
  if (term !== null && hasAmount && hasRate) {
    accruals = amountNumber * rateNumber / 100 * term / 12;
    toPay = amountNumber + accruals;
  }
  let rows = "";
  rows += previewRow("Deposit ID", depositNumber);
  rows += previewRow("Status", values.status);
  rows += previewRow("Amount", hasAmount ? formatMoney(amountNumber, 2) : "");
  rows += previewRow("Currency", values.currency);
  rows += previewRow("Term", term !== null ? termText(term) : "");
  rows += previewRow("Interest rate", hasRate ? values.interest_rate + "%" : "");
  rows += previewRow("Term-end accruals", accruals !== null ? formatMoney(accruals, 2) : "");
  rows += previewRow("Amount to be paid", toPay !== null ? formatMoney(toPay, 2) : "");
  if (previewAccrued !== null) {
    rows += previewRow("Accrued", formatMoney(previewAccrued, 2));
  }
  document.getElementById("previewRows").innerHTML = rows;
}

function initForm() {
  ["amount", "interest_rate"].forEach((id) => {
    document.getElementById(id).addEventListener("input", renderPreview);
  });

  document.querySelectorAll("[data-select]").forEach((select) => {
    const trigger = select.querySelector("[data-trigger]");
    const text = select.querySelector("[data-text]");
    const hidden = select.querySelector("input[type=hidden]");
    trigger.addEventListener("click", () => select.classList.toggle("open"));
    select.querySelector("[data-options]").addEventListener("click", (event) => {
      const option = event.target.closest(".field-option");
      if (!option) {
        return;
      }
      hidden.value = option.dataset.value;
      text.textContent = option.textContent;
      select.classList.remove("open");
      renderPreview();
    });
  });

  document.querySelectorAll("[data-calendar]").forEach((root) => {
    calendars[root.dataset.calendar] = attachCalendar(root, renderPreview);
  });

  document.addEventListener("click", (event) => {
    const openSelect = event.target.closest("[data-select]");
    document.querySelectorAll("[data-select]").forEach((select) => {
      if (select !== openSelect) {
        select.classList.remove("open");
      }
    });
    const openCalendar = event.target.closest("[data-calendar]");
    document.querySelectorAll("[data-calendar]").forEach((root) => {
      if (root !== openCalendar) {
        calendars[root.dataset.calendar].close();
      }
    });
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      document.querySelectorAll("[data-select]").forEach((select) => select.classList.remove("open"));
      Object.values(calendars).forEach((calendar) => calendar.close());
    }
  });

  const menuButton = document.getElementById("menuButton");
  const menu = document.getElementById("menu");
  const menuClose = document.getElementById("menuClose");
  menuButton.addEventListener("click", () => menu.classList.add("open"));
  menuClose.addEventListener("click", () => menu.classList.remove("open"));
  menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => menu.classList.remove("open")));

  renderPreview();
}

function focusField(id) {
  if (id === "start_date" || id === "end_date") {
    document.querySelector(`[data-calendar="${id}"] [data-trigger]`).focus();
  } else if (id === "depositor_id" || id === "currency_id" || id === "status") {
    document.querySelector(`[data-select="${id}"] [data-trigger]`).focus();
  } else {
    document.getElementById(id).focus();
  }
}

async function loadDepositors(token) {
  let response;
  try {
    response = await fetch("/api/depositors/options", { headers: { Authorization: "Bearer " + token } });
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
  document.querySelector('[data-select="depositor_id"] [data-options]').innerHTML = data.depositors
    .map((depositor) => `<li class="field-option" data-value="${depositor.id}">${escapeHtml(depositor.name)}</li>`)
    .join("");
}

async function loadCurrencies(token) {
  let response;
  try {
    response = await fetch("/api/currencies", { headers: { Authorization: "Bearer " + token } });
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
  document.querySelector('[data-select="currency_id"] [data-options]').innerHTML = data.currencies
    .map((currency) => `<li class="field-option" data-value="${currency.id}">${escapeHtml(currency.code)}</li>`)
    .join("");
}

function setSelect(name, value, label) {
  const select = document.querySelector(`[data-select="${name}"]`);
  select.querySelector("input[type=hidden]").value = value;
  select.querySelector("[data-text]").textContent = label;
}

function fillForm(deposit) {
  document.getElementById("amount").value = deposit.amount;
  document.getElementById("interest_rate").value = deposit.interest_rate;
  setSelect("depositor_id", deposit.depositor_id, deposit.depositor);
  setSelect("currency_id", deposit.currency_id, deposit.currency);
  setSelect("status", deposit.status, deposit.status);
  calendars.start_date.setIso(deposit.start_date);
  calendars.end_date.setIso(deposit.end_date);
  renderPreview();
}

function collectForm() {
  return {
    depositor_id: document.getElementById("depositor_id").value,
    currency_id: document.getElementById("currency_id").value,
    status: document.getElementById("status").value,
    amount: document.getElementById("amount").value.trim(),
    interest_rate: document.getElementById("interest_rate").value.trim(),
    start_date: document.getElementById("start_date").value,
    end_date: document.getElementById("end_date").value,
  };
}

function firstEmptyField() {
  for (const field of REQUIRED_FIELDS) {
    if (document.getElementById(field.id).value.trim() === "") {
      return field;
    }
  }
  return null;
}
