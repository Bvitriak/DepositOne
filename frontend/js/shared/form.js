const calendars = {};

function textFieldMarkup(field) {
  const inputMode = field.inputMode ? ` inputmode="${field.inputMode}"` : "";
  const readonly = field.readonly ? " readonly" : ' autocomplete="off"';
  const preview = field.preview ? " data-preview" : "";
  const hint = field.hint ? `\n      <span class="field-hint">${field.hint}</span>` : "";
  return `<div class="field">
      <label class="field-label" for="${field.id}">${field.label}</label>
      <input class="field-control" id="${field.id}" type="text"${inputMode} placeholder="${field.placeholder}"${readonly}${preview}>${hint}
    </div>`;
}

function textareaFieldMarkup(field) {
  return `<div class="field">
      <label class="field-label" for="${field.id}">${field.label}</label>
      <textarea class="field-control field-textarea" id="${field.id}" placeholder="${field.placeholder}"></textarea>
    </div>`;
}

function selectFieldMarkup(field) {
  const options = (field.options || [])
    .map((option) => `<li class="field-option" data-value="${option}">${option}</li>`)
    .join("");
  return `<div class="field">
      <span class="field-label">${field.label}</span>
      <div class="field-select" data-select="${field.id}">
        <button class="field-control field-trigger" type="button" data-trigger aria-haspopup="listbox" aria-expanded="false">
          <span class="field-trigger-text" data-text>${field.placeholder}</span>
          <i class="field-arrow"></i>
        </button>
        <input type="hidden" id="${field.id}">
        <ul class="field-options" data-options role="listbox" aria-label="${field.label}">${options}</ul>
      </div>
    </div>`;
}

function dateFieldMarkup(field) {
  const blockFuture = field.blockFuture ? " data-block-future" : "";
  return `<div class="field">
      <span class="field-label">${field.label}</span>
      <div class="field-date" data-calendar="${field.id}"${blockFuture}>
        <button class="field-control field-trigger" type="button" data-trigger>
          <span class="field-trigger-text" data-text>${field.placeholder}</span>
          <img class="field-calendar-icon" src="/assets/img/calendar.svg" alt="">
        </button>
        <input type="hidden" id="${field.id}">
        <div class="field-calendar" data-panel></div>
      </div>
    </div>`;
}

function fieldMarkup(field) {
  if (field.type === "select") {
    return selectFieldMarkup(field);
  }
  if (field.type === "date") {
    return dateFieldMarkup(field);
  }
  if (field.type === "textarea") {
    return textareaFieldMarkup(field);
  }
  return textFieldMarkup(field);
}

function renderFields(rows) {
  const markup = rows
    .map((row) => `<div class="form-row">${row.map(fieldMarkup).join("")}</div>`)
    .join("");
  document.getElementById("formStatus").insertAdjacentHTML("beforebegin", markup);
}

function previewRow(label, value) {
  const shown = value === "" || value === null || value === undefined ? "–" : value;
  return `<div class="data-card-row">
    <span class="data-card-label">${label}</span>
    <span class="data-card-value">${escapeHtml(shown)}</span>
  </div>`;
}

function fieldValue(id) {
  return document.getElementById(id).value.trim();
}

function setSelect(name, value, label) {
  const select = document.querySelector(`[data-select="${name}"]`);
  select.querySelector("input[type=hidden]").value = value;
  select.querySelector("[data-text]").textContent = label;
}

function fillOptions(name, options) {
  document.querySelector(`[data-select="${name}"] [data-options]`).innerHTML = options
    .map((option) => `<li class="field-option" data-value="${option.value}">${escapeHtml(option.text)}</li>`)
    .join("");
}

function openSelect(select, open) {
  select.classList.toggle("open", open);
  select.querySelector("[data-trigger]").setAttribute("aria-expanded", String(open));
}

function closePopups(keepSelect, keepCalendar) {
  document.querySelectorAll("[data-select]").forEach((select) => {
    if (select !== keepSelect) {
      openSelect(select, false);
    }
  });
  document.querySelectorAll("[data-calendar]").forEach((root) => {
    if (root !== keepCalendar) {
      calendars[root.dataset.calendar].close();
    }
  });
}

function connectFields(rows, onChange) {
  renderFields(rows);

  document.querySelectorAll("[data-preview]").forEach((input) => {
    input.addEventListener("input", () => onChange(input.id));
  });

  document.querySelectorAll("[data-select]").forEach((select) => {
    select.querySelector("[data-trigger]").addEventListener("click", () => {
      openSelect(select, !select.classList.contains("open"));
    });
    select.querySelector("[data-options]").addEventListener("click", (event) => {
      const option = event.target.closest(".field-option");
      if (!option) {
        return;
      }
      select.querySelector("input[type=hidden]").value = option.dataset.value;
      select.querySelector("[data-text]").textContent = option.textContent;
      openSelect(select, false);
      onChange(select.dataset.select);
    });
  });

  document.querySelectorAll("[data-calendar]").forEach((root) => {
    calendars[root.dataset.calendar] = attachCalendar(root, () => onChange(root.dataset.calendar));
  });

  document.addEventListener("click", (event) => {
    closePopups(event.target.closest("[data-select]"), event.target.closest("[data-calendar]"));
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closePopups(null, null);
    }
  });

  onChange("");
}

function focusField(id) {
  const calendar = document.querySelector(`[data-calendar="${id}"] [data-trigger]`);
  if (calendar) {
    calendar.focus();
    return;
  }
  const select = document.querySelector(`[data-select="${id}"] [data-trigger]`);
  if (select) {
    select.focus();
    return;
  }
  document.getElementById(id).focus();
}

function firstEmptyField(rows) {
  for (const row of rows) {
    for (const field of row) {
      if (field.required && fieldValue(field.id) === "") {
        return field;
      }
    }
  }
  return null;
}

function connectFormPage(options) {
  const form = document.getElementById("entityForm");
  const status = document.getElementById("formStatus");
  const deleteButton = document.getElementById("deleteButton");
  const itemPath = options.itemId ? options.apiPath + "/" + options.itemId : options.apiPath;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const missing = firstEmptyField(options.fields);
    if (missing) {
      status.textContent = "Please fill in the " + missing.label + " field";
      focusField(missing.id);
      return;
    }
    status.textContent = "";
    const response = await apiRequest(itemPath, {
      method: options.itemId ? "PUT" : "POST",
      body: JSON.stringify(options.collect()),
      expectedStatuses: [400],
    });
    if (!response) {
      return;
    }
    if (response.status === 400) {
      const data = await response.json();
      status.textContent = data.error || "Please check the form";
      return;
    }
    window.location.href = options.listUrl;
  });

  document.getElementById("cancelButton").addEventListener("click", () => {
    if (options.itemId) {
      options.restore();
      status.textContent = "";
      return;
    }
    window.location.href = options.listUrl;
  });

  if (!deleteButton) {
    return;
  }
  deleteButton.addEventListener("click", async () => {
    const response = await apiRequest(itemPath, { method: "DELETE", expectedStatuses: [409] });
    if (!response) {
      return;
    }
    if (response.status === 409) {
      const data = await response.json();
      status.textContent = options.onConflict(data);
      return;
    }
    window.location.href = options.listUrl;
  });
}
