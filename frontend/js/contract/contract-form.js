const CONTRACT_FIELDS = [
  [
    { id: "contract_number", label: "Contract Number", placeholder: "# year/month/Deposit ID", readonly: true, hint: "Automatically generated prefix - year/month/Deposit ID" },
  ],
  [
    { type: "date", id: "contract_date", label: "Date of the contract", placeholder: "Choose date of the contract", required: true },
    { type: "select", id: "signing_status", label: "Signing status", placeholder: "Choose status", options: ["Signed", "Pending", "Rejected"], required: true },
  ],
  [
    { type: "select", id: "deposit_id", label: "Deposit ID", placeholder: "Choose deposit", required: true },
    { type: "select", id: "depositor_id", label: "Depositor", placeholder: "Choose depositor" },
  ],
  [
    { id: "description", label: "Description of the term", placeholder: "Enter description of the term", required: true },
  ],
  [
    { id: "special_conditions", label: "Special conditions", placeholder: "Enter special conditions" },
  ],
];

let deposits = [];

function findDeposit(depositId) {
  for (const deposit of deposits) {
    if (String(deposit.id) === String(depositId)) {
      return deposit;
    }
  }
  return null;
}

function collectContract() {
  return {
    deposit_id: fieldValue("deposit_id"),
    contract_date: fieldValue("contract_date"),
    signing_status: fieldValue("signing_status"),
    description: fieldValue("description"),
    special_conditions: fieldValue("special_conditions"),
  };
}

function renderContractNumber() {
  const values = collectContract();
  const deposit = findDeposit(values.deposit_id);
  const input = document.getElementById("contract_number");
  if (deposit && values.contract_date) {
    input.value = "#" + values.contract_date.slice(0, 4) + "/" + values.contract_date.slice(5, 7) + "/" + deposit.number;
  } else {
    input.value = "";
  }
}

function renderPreview() {
  const values = collectContract();
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
  if (deposit) {
    fillOptions("depositor_id", [{ value: deposit.depositor_id, text: deposit.depositor }]);
    setSelect("depositor_id", deposit.depositor_id, deposit.depositor);
  } else {
    fillOptions("depositor_id", []);
    setSelect("depositor_id", "", "Choose depositor");
  }
}

function updateContractForm() {
  setDepositor(findDeposit(fieldValue("deposit_id")));
  renderContractNumber();
  renderPreview();
}

async function loadDeposits() {
  const data = await apiRead("/api/deposits/options");
  if (!data) {
    return;
  }
  deposits = data.deposits;
  fillOptions("deposit_id", deposits.map((deposit) => ({ value: deposit.id, text: deposit.number })));
}

function fillContractForm(contract) {
  document.getElementById("description").value = contract.description;
  document.getElementById("special_conditions").value = contract.special_conditions;
  setSelect("signing_status", contract.signing_status, contract.signing_status);
  setSelect("deposit_id", contract.deposit_id, contract.deposit_number);
  calendars.contract_date.setIso(contract.contract_date);
  updateContractForm();
}
