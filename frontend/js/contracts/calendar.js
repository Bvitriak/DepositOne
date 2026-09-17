const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

function padNumber(number) {
  return String(number).padStart(2, "0");
}

function attachCalendar(root, onChange) {
  const trigger = root.querySelector("[data-trigger]");
  const panel = root.querySelector("[data-panel]");
  const text = root.querySelector("[data-text]");
  const hidden = root.querySelector("input[type=hidden]");
  const today = new Date();
  let view = "days";
  let year = today.getFullYear();
  let month = today.getMonth();
  let selected = null;

  function daysInMonth(targetYear, targetMonth) {
    return new Date(targetYear, targetMonth + 1, 0).getDate();
  }

  function isSelected(day) {
    return selected &&
      selected.getFullYear() === year &&
      selected.getMonth() === month &&
      selected.getDate() === day;
  }

  function cell(label, action, value, active) {
    return `<button type="button" class="calendar-cell ${active ? "is-active" : ""}" data-action="${action}" data-value="${value}">${label}</button>`;
  }

  function renderDays() {
    let cells = "";
    const total = daysInMonth(year, month);
    for (let day = 1; day <= total; day = day + 1) {
      cells += cell(day, "day", day, isSelected(day));
    }
    panel.innerHTML = `<div class="calendar-header">
      <button type="button" class="calendar-nav" data-action="prev"><i class="calendar-arrow calendar-arrow-left"></i></button>
      <div class="calendar-title">
        <button type="button" data-action="view-months">${MONTH_NAMES[month]}</button>
        <button type="button" data-action="view-years">${year}</button>
      </div>
      <button type="button" class="calendar-nav" data-action="next"><i class="calendar-arrow calendar-arrow-right"></i></button>
    </div>
    <div class="calendar-grid calendar-grid-days">${cells}</div>`;
  }

  function renderMonths() {
    let cells = "";
    for (let index = 0; index < 12; index = index + 1) {
      const active = selected && selected.getFullYear() === year && selected.getMonth() === index;
      cells += cell(MONTH_NAMES[index], "month", index, active);
    }
    panel.innerHTML = `<div class="calendar-header">
      <button type="button" class="calendar-nav" data-action="prev"><i class="calendar-arrow calendar-arrow-left"></i></button>
      <div class="calendar-title">
        <button type="button" data-action="view-years">${year}</button>
      </div>
      <button type="button" class="calendar-nav" data-action="next"><i class="calendar-arrow calendar-arrow-right"></i></button>
    </div>
    <div class="calendar-grid calendar-grid-months">${cells}</div>`;
  }

  function renderYears() {
    let cells = "";
    const start = year - 5;
    for (let value = start; value < start + 12; value = value + 1) {
      const active = selected && selected.getFullYear() === value;
      cells += cell(value, "year", value, active);
    }
    panel.innerHTML = `<div class="calendar-header">
      <button type="button" class="calendar-nav" data-action="prev"><i class="calendar-arrow calendar-arrow-left"></i></button>
      <div class="calendar-title">
        <span>${start} - ${start + 11}</span>
      </div>
      <button type="button" class="calendar-nav" data-action="next"><i class="calendar-arrow calendar-arrow-right"></i></button>
    </div>
    <div class="calendar-grid calendar-grid-years">${cells}</div>`;
  }

  function render() {
    if (view === "months") {
      renderMonths();
    } else if (view === "years") {
      renderYears();
    } else {
      renderDays();
    }
  }

  function setDate(date, notify) {
    selected = date;
    year = date.getFullYear();
    month = date.getMonth();
    hidden.value = date.getFullYear() + "-" + padNumber(date.getMonth() + 1) + "-" + padNumber(date.getDate());
    text.textContent = padNumber(date.getDate()) + "." + padNumber(date.getMonth() + 1) + "." + date.getFullYear();
    if (notify) {
      onChange();
    }
  }

  function open() {
    view = "days";
    root.classList.remove("open-up");
    root.classList.add("open");
    render();
    const card = root.closest(".form-card");
    if (card) {
      const spaceBelow = card.getBoundingClientRect().bottom - trigger.getBoundingClientRect().bottom;
      if (spaceBelow < panel.offsetHeight + 12) {
        root.classList.add("open-up");
      }
    }
  }

  function close() {
    root.classList.remove("open");
  }

  trigger.addEventListener("click", () => {
    if (root.classList.contains("open")) {
      close();
    } else {
      open();
    }
  });

  panel.addEventListener("click", (event) => {
    event.stopPropagation();
    const button = event.target.closest("[data-action]");
    if (!button) {
      return;
    }
    const action = button.dataset.action;
    if (action === "prev") {
      if (view === "months") {
        year = year - 1;
      } else if (view === "years") {
        year = year - 12;
      } else {
        month = month - 1;
        if (month < 0) {
          month = 11;
          year = year - 1;
        }
      }
      render();
    } else if (action === "next") {
      if (view === "months") {
        year = year + 1;
      } else if (view === "years") {
        year = year + 12;
      } else {
        month = month + 1;
        if (month > 11) {
          month = 0;
          year = year + 1;
        }
      }
      render();
    } else if (action === "view-months") {
      view = "months";
      render();
    } else if (action === "view-years") {
      view = "years";
      render();
    } else if (action === "month") {
      month = Number(button.dataset.value);
      view = "days";
      render();
    } else if (action === "year") {
      year = Number(button.dataset.value);
      view = "months";
      render();
    } else if (action === "day") {
      setDate(new Date(year, month, Number(button.dataset.value)), true);
      close();
    }
  });

  return {
    setIso(iso) {
      if (iso) {
        const parts = iso.split("-");
        setDate(new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2])), false);
      } else {
        selected = null;
        hidden.value = "";
        text.textContent = "Choose date";
        year = today.getFullYear();
        month = today.getMonth();
      }
    },
    close,
  };
}
