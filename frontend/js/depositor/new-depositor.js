const DEPOSITOR_LIST_URL = "/pages/depositor/depositors.html";

async function start() {
  connectFields(DEPOSITOR_FIELDS, renderPreview);
  await loadCountries();
}

connectFormPage({
  apiPath: "/api/depositors",
  listUrl: DEPOSITOR_LIST_URL,
  fields: DEPOSITOR_FIELDS,
  collect: collectDepositor,
});

start();
