const CONTRACT_LIST_URL = "/pages/contract/contracts.html";
const contractId = new URLSearchParams(window.location.search).get("id");

let original = null;

async function start() {
  if (!contractId) {
    window.location.href = CONTRACT_LIST_URL;
    return;
  }
  connectFields(CONTRACT_FIELDS, updateContractForm);
  await loadDeposits();
  original = await apiReadItem("/api/contracts/" + contractId, CONTRACT_LIST_URL);
  if (!original) {
    return;
  }
  fillContractForm(original);
}

connectFormPage({
  apiPath: "/api/contracts",
  listUrl: CONTRACT_LIST_URL,
  itemId: contractId,
  fields: CONTRACT_FIELDS,
  collect: collectContract,
  restore: () => fillContractForm(original),
});

start();
