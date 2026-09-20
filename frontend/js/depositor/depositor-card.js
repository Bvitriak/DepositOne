const DEPOSITOR_LIST_URL = "/pages/depositor/depositors.html";
const depositorId = new URLSearchParams(window.location.search).get("id");
const deletionCard = document.getElementById("deletionCard");
const deletionText = document.getElementById("deletionText");

let original = null;

function conflictMessage(data) {
  const active = data.error === "depositor has active deposits";
  deletionText.textContent = active
    ? "There are active deposits assigned to the card. Close them before deleting."
    : "There are deposits assigned to the card. Delete them before deleting.";
  deletionCard.hidden = false;
  return active
    ? "Deletion is impossible while there are active deposits"
    : "Deletion is impossible while there are deposits";
}

async function start() {
  if (!depositorId) {
    window.location.href = DEPOSITOR_LIST_URL;
    return;
  }
  connectFields(DEPOSITOR_FIELDS, renderPreview);
  await loadCountries();
  original = await apiReadItem("/api/depositors/" + depositorId, DEPOSITOR_LIST_URL);
  if (!original) {
    return;
  }
  previewExtra = { active_deposits: original.active_deposits, opened: original.opened };
  fillDepositorForm(original);
  deletionCard.hidden = original.active_deposits === 0;
}

connectFormPage({
  apiPath: "/api/depositors",
  listUrl: DEPOSITOR_LIST_URL,
  itemId: depositorId,
  fields: DEPOSITOR_FIELDS,
  collect: collectDepositor,
  restore: () => fillDepositorForm(original),
  onConflict: conflictMessage,
});

start();
