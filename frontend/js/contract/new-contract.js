const CONTRACT_LIST_URL = "/pages/contract/contracts.html";

async function start() {
  connectFields(CONTRACT_FIELDS, updateContractForm);
  await loadDeposits();
}

connectFormPage({
  apiPath: "/api/contracts",
  listUrl: CONTRACT_LIST_URL,
  fields: CONTRACT_FIELDS,
  collect: collectContract,
});

start();
