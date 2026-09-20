const TICKET_FIELDS = [
  [
    { type: "select", id: "category", label: "Category", placeholder: "Choose category", required: true,
      options: ["Deposit", "Contract", "Payment", "Account", "Technical issue", "Other"] },
    { type: "select", id: "priority", label: "Priority", placeholder: "Choose priority", required: true,
      options: ["Low", "Medium", "High", "Urgent"] },
  ],
  [
    { id: "theme", label: "Theme", placeholder: "Enter theme", required: true },
  ],
  [
    { type: "textarea", id: "description", label: "Description", placeholder: "Please describe your problem in detail", required: true },
  ],
];

const status = document.getElementById("formStatus");

connectFields(TICKET_FIELDS, () => {});

document.getElementById("entityForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const missing = firstEmptyField(TICKET_FIELDS);
  if (missing) {
    status.textContent = "Please fill in the " + missing.label + " field";
    focusField(missing.id);
    return;
  }
  status.textContent = "";
  const subject = "Support ticket: " + fieldValue("theme");
  const body =
    "Category: " + fieldValue("category") + "\n" +
    "Priority: " + fieldValue("priority") + "\n" +
    "Theme: " + fieldValue("theme") + "\n" +
    "Description: " + fieldValue("description");
  window.location.href = "mailto:support@depositone.com?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
});
