const menuButton = document.getElementById("menuButton");
const menu = document.getElementById("menu");
const menuClose = document.getElementById("menuClose");
menuButton.addEventListener("click", () => menu.classList.add("open"));
menuClose.addEventListener("click", () => menu.classList.remove("open"));
menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => menu.classList.remove("open")));

const selects = document.querySelectorAll("[data-select]");

function closeSelects(except) {
  selects.forEach((select) => {
    if (select !== except) {
      select.classList.remove("open");
      select.querySelector("[data-trigger]").setAttribute("aria-expanded", "false");
    }
  });
}

selects.forEach((select) => {
  const trigger = select.querySelector("[data-trigger]");
  const text = select.querySelector("[data-text]");
  const input = select.querySelector("input");
  trigger.addEventListener("click", () => {
    const willOpen = !select.classList.contains("open");
    closeSelects(select);
    select.classList.toggle("open", willOpen);
    trigger.setAttribute("aria-expanded", String(willOpen));
  });
  select.querySelectorAll(".ticket-option").forEach((option) => {
    option.addEventListener("click", () => {
      input.value = option.dataset.value;
      text.textContent = option.textContent;
      select.classList.remove("open");
      trigger.setAttribute("aria-expanded", "false");
    });
  });
});

document.addEventListener("click", (event) => {
  if (!event.target.closest("[data-select]")) {
    closeSelects(null);
  }
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeSelects(null);
  }
});

const form = document.getElementById("ticketForm");
const status = document.getElementById("ticketStatus");

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const fields = [
    { name: "category", label: "Category" },
    { name: "priority", label: "Priority" },
    { name: "theme", label: "Theme" },
    { name: "description", label: "Description" },
  ];
  for (const field of fields) {
    const control = form[field.name];
    if (control.value.trim() === "") {
      status.textContent = "Please fill in the " + field.label + " field";
      if (control.type === "hidden") {
        control.closest("[data-select]").querySelector("[data-trigger]").focus();
      } else {
        control.focus();
      }
      return;
    }
  }
  status.textContent = "";
  const subject = "Support ticket: " + form.theme.value.trim();
  const body =
    "Category: " + form.category.value + "\n" +
    "Priority: " + form.priority.value + "\n" +
    "Theme: " + form.theme.value.trim() + "\n" +
    "Description: " + form.description.value.trim();
  window.location.href = "mailto:support@depositone.com?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
});
