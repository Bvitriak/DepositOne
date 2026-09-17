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

const REQUIRED_FIELDS = [
  { id: "deposit_id", label: "Deposit ID" },
  { id: "contract_date", label: "Date of the Contract" },
  { id: "signing_status", label: "Signing Status" },
  { id: "description", label: "Description of the Term" },
  { id: "special_conditions", label: "Special Conditions" },
];

let calendars = {};
let deposits = [];

function findDeposit(depositId) {
  for (const deposit of deposits) {
    if (String(deposit.id) === String(depositId)) {
      return deposit;
    }
  }
  return null;
}

function getFormValues() {
  return {
    deposit_id: document.getElementById("deposit_id").value,
    contract_date: document.getElementById("contract_date").value,
    signing_status: document.getElementById("signing_status").value,
    description: document.getElementById("description").value.trim(),
    special_conditions: document.getElementById("special_conditions").value.trim(),
  };
}

function renderContractNumber() {
  const values = getFormValues();
  const deposit = findDeposit(values.deposit_id);
  const input = document.getElementById("contract_number");
  if (deposit && values.contract_date) {
    const year = values.contract_date.slice(0, 4);
    const month = values.contract_date.slice(5, 7);
    input.value = "#" + year + "/" + month + "/" + deposit.number;
  } else {
    input.value = "";
  }
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
  const deposit = findDeposit(values.deposit_id);
  let rows = "";
  rows += previewRow("Deposit ID", deposit ? deposit.number : "");
  rows += previewRow("Depositor", deposit ? deposit.depositor : "");
  rows += previewRow("Amount", deposit ? formatMoney(deposit.amount, 2) : "");
  rows += previewRow("Currency", deposit ? deposit.currency : "");
  rows += previewRow("Interest rate", deposit ? Number(deposit.interest_rate) + "%" : "");
  rows += previewRow("Term-end accruals", deposit ? formatMoney(deposit.term_end_accruals, 2) : "");
  rows += previewRow("Start date", deposit ? formatDate(deposit.start_date) : "");
  rows += previewRow("End date", deposit ? formatDate(deposit.end_date) : "");
  rows += previewRow("Signing Status", values.signing_status);
  document.getElementById("previewRows").innerHTML = rows;
}

function setDepositor(deposit) {
  const select = document.querySelector('[data-select="depositor_id"]');
  const options = select.querySelector("[data-options]");
  const hidden = select.querySelector("input[type=hidden]");
  const text = select.querySelector("[data-text]");
  if (deposit) {
    options.innerHTML = `<li class="field-option" data-value="${deposit.depositor_id}">${escapeHtml(deposit.depositor)}</li>`;
    hidden.value = deposit.depositor_id;
    text.textContent = deposit.depositor;
  } else {
    options.innerHTML = "";
    hidden.value = "";
    text.textContent = "Choose depositor";
  }
}

function onDepositChange() {
  const deposit = findDeposit(document.getElementById("deposit_id").value);
  setDepositor(deposit);
  renderContractNumber();
  renderPreview();
}

function initForm() {
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
      if (select.dataset.select === "deposit_id") {
        onDepositChange();
      } else {
        renderPreview();
      }
    });
  });

  document.querySelectorAll("[data-calendar]").forEach((root) => {
    calendars[root.dataset.calendar] = attachCalendar(root, () => {
      renderContractNumber();
      renderPreview();
    });
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
  if (id === "contract_date") {
    document.querySelector('[data-calendar="contract_date"] [data-trigger]').focus();
  } else if (id === "deposit_id" || id === "signing_status" || id === "depositor_id") {
    document.querySelector(`[data-select="${id}"] [data-trigger]`).focus();
  } else {
    document.getElementById(id).focus();
  }
}

async function loadDeposits(token) {
  let response;
  try {
    response = await fetch("/api/deposits/options", { headers: { Authorization: "Bearer " + token } });
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
  deposits = data.deposits;
  document.querySelector('[data-select="deposit_id"] [data-options]').innerHTML = deposits
    .map((deposit) => `<li class="field-option" data-value="${deposit.id}">${escapeHtml(deposit.number)}</li>`)
    .join("");
}

function setSelect(name, value, label) {
  const select = document.querySelector(`[data-select="${name}"]`);
  select.querySelector("input[type=hidden]").value = value;
  select.querySelector("[data-text]").textContent = label;
}

function fillForm(contract) {
  document.getElementById("description").value = contract.description;
  document.getElementById("special_conditions").value = contract.special_conditions;
  setSelect("signing_status", contract.signing_status, contract.signing_status);
  setSelect("deposit_id", contract.deposit_id, contract.deposit_number);
  calendars.contract_date.setIso(contract.contract_date);
  onDepositChange();
}

function collectForm() {
  return {
    deposit_id: document.getElementById("deposit_id").value,
    contract_date: document.getElementById("contract_date").value,
    signing_status: document.getElementById("signing_status").value,
    description: document.getElementById("description").value.trim(),
    special_conditions: document.getElementById("special_conditions").value.trim(),
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
