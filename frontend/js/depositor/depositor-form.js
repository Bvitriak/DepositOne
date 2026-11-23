const DEPOSITOR_FIELDS = [
  [
    { id: "first_name", label: "First name", placeholder: "Enter first name", preview: true, required: true },
    { id: "last_name", label: "Last name", placeholder: "Enter last name", preview: true, required: true },
  ],
  [
    { type: "date", id: "date_of_birth", label: "Date of Birth", placeholder: "Choose date", blockFuture: true, required: true },
    { type: "select", id: "country_id", label: "Country", placeholder: "Choose country", required: true },
  ],
  [
    { id: "passport", label: "Passport", placeholder: "Enter passport", preview: true, required: true },
    { id: "tin", label: "TIN", placeholder: "Enter tax id", preview: true, required: true },
  ],
  [
    { id: "phone", label: "Phone", placeholder: "Enter phone", preview: true, required: true },
    { id: "email", label: "Email", placeholder: "Enter email", preview: true, required: true },
  ],
  [
    { id: "address", label: "Address", placeholder: "Enter address", preview: true, required: true },
  ],
];

const TEXT_FIELDS = ["first_name", "last_name", "passport", "tin", "phone", "email", "address"];

let previewExtra = null;

function collectDepositor() {
  const values = { country_id: fieldValue("country_id"), date_of_birth: fieldValue("date_of_birth") };
  TEXT_FIELDS.forEach((id) => {
    values[id] = fieldValue(id);
  });
  return values;
}

function countryName() {
  const select = document.querySelector('[data-select="country_id"]');
  return fieldValue("country_id") ? select.querySelector("[data-text]").textContent : "";
}

function renderPreview() {
  const values = collectDepositor();
  let rows = "";
  rows += previewRow("First name", values.first_name);
  rows += previewRow("Last name", values.last_name);
  rows += previewRow("Date of Birth", values.date_of_birth ? formatDate(values.date_of_birth) : "");
  rows += previewRow("Country", countryName());
  rows += previewRow("Passport", values.passport);
  rows += previewRow("TIN", values.tin);
  rows += previewRow("Phone", values.phone);
  rows += previewRow("Email", values.email);
  rows += previewRow("Address", values.address);
  if (previewExtra) {
    rows += previewRow("Active deposits", String(previewExtra.active_deposits));
    rows += previewRow("Opened", formatDate(previewExtra.opened));
  }
  document.getElementById("previewRows").innerHTML = rows;
}

async function loadCountries() {
  const data = await apiRead("/api/countries");
  if (!data) {
    return;
  }
  fillOptions("country_id", data.countries.map((country) => ({ value: country.id, text: country.name })));
}

function fillDepositorForm(depositor) {
  TEXT_FIELDS.forEach((id) => {
    document.getElementById(id).value = depositor[id];
  });
  setSelect("country_id", depositor.country_id, depositor.country);
  calendars.date_of_birth.setIso(depositor.date_of_birth);
  renderPreview();
}
