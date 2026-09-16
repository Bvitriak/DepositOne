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

const TEXT_FIELDS = ["first_name", "last_name", "passport", "tin", "phone", "email", "address"];

const REQUIRED_FIELDS = [
  { id: "first_name", label: "First name" },
  { id: "last_name", label: "Last name" },
  { id: "date_of_birth", label: "Date of Birth" },
  { id: "country_id", label: "Country" },
  { id: "passport", label: "Passport" },
  { id: "tin", label: "TIN" },
  { id: "phone", label: "Phone" },
  { id: "email", label: "Email" },
  { id: "address", label: "Address" },
];

const PREVIEW_ROWS = [
  { label: "First name", key: "first_name" },
  { label: "Last name", key: "last_name" },
  { label: "Date of Birth", key: "date_of_birth", date: true },
  { label: "Country", key: "country" },
  { label: "Passport", key: "passport" },
  { label: "TIN", key: "tin" },
  { label: "Phone", key: "phone" },
  { label: "Email", key: "email" },
  { label: "Address", key: "address" },
];

let calendarWidget = null;
let previewExtra = null;

function getFormValues() {
  const select = document.querySelector("[data-select]");
  const countryId = select.querySelector("input[type=hidden]").value;
  const countryName = select.querySelector("[data-text]").textContent;
  const values = { country_id: countryId, country: countryId ? countryName : "" };
  TEXT_FIELDS.forEach((id) => {
    values[id] = document.getElementById(id).value.trim();
  });
  values.date_of_birth = document.getElementById("date_of_birth").value;
  return values;
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
  let rows = PREVIEW_ROWS.map((row) => {
    let value = values[row.key];
    if (row.date && value) {
      value = formatDate(value);
    }
    return previewRow(row.label, value);
  }).join("");
  if (previewExtra) {
    rows += previewRow("Active deposits", String(previewExtra.active_deposits));
    rows += previewRow("Opened", formatDate(previewExtra.opened));
  }
  document.getElementById("previewRows").innerHTML = rows;
}

function initForm() {
  TEXT_FIELDS.forEach((id) => {
    document.getElementById(id).addEventListener("input", renderPreview);
  });

  const select = document.querySelector("[data-select]");
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
    renderPreview();
  });

  const dateRoot = document.querySelector("[data-calendar]");
  calendarWidget = attachCalendar(dateRoot, renderPreview);

  document.addEventListener("click", (event) => {
    if (!event.target.closest("[data-select]")) {
      select.classList.remove("open");
    }
    if (!event.target.closest("[data-calendar]")) {
      calendarWidget.close();
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      select.classList.remove("open");
      calendarWidget.close();
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
  if (id === "date_of_birth") {
    document.querySelector("[data-calendar] [data-trigger]").focus();
  } else if (id === "country_id") {
    document.querySelector("[data-select] [data-trigger]").focus();
  } else {
    document.getElementById(id).focus();
  }
}

async function loadCountries(token) {
  let response;
  try {
    response = await fetch("/api/countries", { headers: { Authorization: "Bearer " + token } });
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
  document.querySelector("[data-options]").innerHTML = data.countries
    .map((country) => `<li class="field-option" data-value="${country.id}">${escapeHtml(country.name)}</li>`)
    .join("");
}

function fillForm(depositor) {
  TEXT_FIELDS.forEach((id) => {
    document.getElementById(id).value = depositor[id];
  });
  const select = document.querySelector("[data-select]");
  select.querySelector("input[type=hidden]").value = depositor.country_id;
  select.querySelector("[data-text]").textContent = depositor.country;
  calendarWidget.setIso(depositor.date_of_birth);
  renderPreview();
}

function collectForm() {
  const values = getFormValues();
  return {
    first_name: values.first_name,
    last_name: values.last_name,
    date_of_birth: values.date_of_birth,
    country_id: values.country_id,
    passport: values.passport,
    tin: values.tin,
    phone: values.phone,
    email: values.email,
    address: values.address,
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
