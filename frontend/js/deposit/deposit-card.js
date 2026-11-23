const DEPOSIT_LIST_URL = "/pages/deposit/deposits.html";
const depositId = new URLSearchParams(window.location.search).get("id");
const deletionCard = document.getElementById("deletionCard");

let original = null;

function conflictMessage() {
  deletionCard.hidden = false;
  return "Deletion is impossible while there is a contract";
}

async function start() {
  if (!depositId) {
    window.location.href = DEPOSIT_LIST_URL;
    return;
  }
  connectFields(DEPOSIT_FIELDS, renderPreview);
  await loadDepositOptions();
  original = await apiReadItem("/api/deposits/" + depositId, DEPOSIT_LIST_URL);
  if (!original) {
    return;
  }
  depositNumber = original.deposit_number;
  previewAccrued = original.accrued;
  fillDepositForm(original);
}

connectFormPage({
  apiPath: "/api/deposits",
  listUrl: DEPOSIT_LIST_URL,
  itemId: depositId,
  fields: DEPOSIT_FIELDS,
  collect: collectDeposit,
  restore: () => fillDepositForm(original),
  onConflict: conflictMessage,
});

start();
