const DEPOSIT_LIST_URL = "/pages/deposit/deposits.html";

async function start() {
  connectFields(DEPOSIT_FIELDS, renderPreview);
  await loadDepositOptions();
  const data = await apiRead("/api/deposits/stats");
  if (!data) {
    return;
  }
  depositNumber = data.next_number;
  renderPreview();
}

connectFormPage({
  apiPath: "/api/deposits",
  listUrl: DEPOSIT_LIST_URL,
  fields: DEPOSIT_FIELDS,
  collect: collectDeposit,
});

start();
