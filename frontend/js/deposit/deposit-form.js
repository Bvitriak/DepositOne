const DEPOSIT_FIELDS = [
  [
    { type: "select", id: "depositor_id", label: "Depositor", placeholder: "Choose depositor", required: true },
  ],
  [
    { type: "select", id: "status", label: "Status", placeholder: "Choose status", options: ["Active", "Pending", "Closed", "Blocked"], required: true },
    { type: "select", id: "currency_id", label: "Currency", placeholder: "Choose currency", required: true },
  ],
  [
    { type: "date", id: "start_date", label: "Start date", placeholder: "Choose start date", required: true },
    { type: "date", id: "end_date", label: "End date", placeholder: "Choose end date", required: true },
  ],
  [
    { id: "amount", label: "Amount", placeholder: "Enter amount", inputMode: "decimal", preview: true, required: true },
    { id: "interest_rate", label: "Interest rate", placeholder: "Enter interest rate", inputMode: "decimal", preview: true, required: true },
  ],
];

let depositNumber = "";
let previewAccrued = null;

function monthsBetween(startIso, endIso) {
  const start = startIso.split("-");
  const end = endIso.split("-");
  let months = (Number(end[0]) - Number(start[0])) * 12 + (Number(end[1]) - Number(start[1]));
  if (Number(end[2]) < Number(start[2])) {
    months = months - 1;
  }
  return months;
}

function daysBetween(startIso, endIso) {
  const start = new Date(startIso);
  const end = new Date(endIso);
  return Math.round((end - start) / 86400000);
}

function termText(months, days) {
  if (months === 0) {
    return days === 1 ? "1 day" : days + " days";
  }
  if (months === 1) {
    return "1 month";
  }
  return months + " months";
}

function collectDeposit() {
  return {
    depositor_id: fieldValue("depositor_id"),
    currency_id: fieldValue("currency_id"),
    status: fieldValue("status"),
    amount: fieldValue("amount"),
    interest_rate: fieldValue("interest_rate"),
    start_date: fieldValue("start_date"),
    end_date: fieldValue("end_date"),
  };
}

function currencyName() {
  const select = document.querySelector('[data-select="currency_id"]');
  return fieldValue("currency_id") ? select.querySelector("[data-text]").textContent : "";
}

function renderPreview() {
  const values = collectDeposit();
  const amountNumber = Number(values.amount);
  const rateNumber = Number(values.interest_rate);
  const hasPeriod = values.start_date && values.end_date && values.end_date > values.start_date;
  let term = null;
  let accruals = null;
  let toPay = null;
  if (hasPeriod) {
    term = monthsBetween(values.start_date, values.end_date);
    if (values.amount !== "" && values.interest_rate !== "") {
      accruals = amountNumber * rateNumber / 100 * daysBetween(values.start_date, values.end_date) / 365;
      toPay = amountNumber + accruals;
    }
  }
  let rows = "";
  rows += previewRow("Deposit ID", depositNumber);
  rows += previewRow("Status", values.status);
  rows += previewRow("Amount", values.amount !== "" ? formatMoney(amountNumber, 2) : "");
  rows += previewRow("Currency", currencyName());
  rows += previewRow("Term", term !== null ? termText(term, daysBetween(values.start_date, values.end_date)) : "");
  rows += previewRow("Interest rate", values.interest_rate !== "" ? values.interest_rate + "%" : "");
  rows += previewRow("Term-end accruals", accruals !== null ? formatMoney(accruals, 2) : "");
  rows += previewRow("Amount to be paid", toPay !== null ? formatMoney(toPay, 2) : "");
  if (previewAccrued !== null) {
    rows += previewRow("Accrued", formatMoney(previewAccrued, 2));
  }
  document.getElementById("previewRows").innerHTML = rows;
}

async function loadDepositOptions() {
  const depositors = await apiRead("/api/depositors/options");
  if (!depositors) {
    return;
  }
  fillOptions("depositor_id", depositors.depositors.map((depositor) => ({ value: depositor.id, text: depositor.name })));
  const currencies = await apiRead("/api/currencies");
  if (!currencies) {
    return;
  }
  fillOptions("currency_id", currencies.currencies.map((currency) => ({ value: currency.id, text: currency.code })));
}

function fillDepositForm(deposit) {
  document.getElementById("amount").value = deposit.amount;
  document.getElementById("interest_rate").value = deposit.interest_rate;
  setSelect("depositor_id", deposit.depositor_id, deposit.depositor);
  setSelect("currency_id", deposit.currency_id, deposit.currency);
  setSelect("status", deposit.status, deposit.status);
  calendars.start_date.setIso(deposit.start_date);
  calendars.end_date.setIso(deposit.end_date);
  renderPreview();
}
