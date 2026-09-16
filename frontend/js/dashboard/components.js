function summaryCard(label, description, value) {
  return `<article class="summary-card">
    <div class="summary-card-details">
      <p class="summary-card-label">${label}</p>
      <p class="summary-card-value">${value ?? "N/A"}</p>
    </div>
    <p class="summary-card-description">${description}</p>
  </article>`;
}

function ringGradient(colors) {
  const step = 100 / colors.length;
  const stops = colors.map((color, index) => `${color} ${step * index}% ${step * (index + 1)}%`);
  return `conic-gradient(${stops.join(", ")})`;
}

function chartCard(total, legend) {
  const colors = legend.map((item) => item.color);
  const rows = legend.map((item) => `<li class="chart-legend-row">
        <span class="chart-legend-name"><span class="chart-legend-marker" style="background:${item.color}"></span>${item.name}</span>
        <span class="chart-legend-value">${item.value ?? "N/A"}</span>
      </li>`).join("");
  return `<article class="chart-card">
    <div class="chart-donut">
      <div class="chart-donut-ring" style="background:${ringGradient(colors)}"></div>
      <div class="chart-donut-center">${total ?? "N/A"}</div>
    </div>
    <ul class="chart-legend">${rows}</ul>
  </article>`;
}

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

function depositorCard(depositor) {
  const fullName = escapeHtml(depositor.first_name + " " + depositor.last_name);
  return `<a class="depositor-card" href="depositor-card.html?id=${depositor.id}">
    <div class="depositor-card-head">
      <p class="depositor-card-name">${fullName}</p>
      <span class="depositor-card-badge">${depositor.active_deposits} DEPOSITS</span>
    </div>
    <div class="depositor-card-info">
      <div class="depositor-card-field">
        <span class="depositor-card-label">DOB:</span>
        <span class="depositor-card-value">${formatDate(depositor.date_of_birth)}</span>
      </div>
      <div class="depositor-card-field">
        <span class="depositor-card-label">COUNTRY:</span>
        <span class="depositor-card-value">${escapeHtml(depositor.country)}</span>
      </div>
      <div class="depositor-card-field">
        <span class="depositor-card-label">EMAIL:</span>
        <span class="depositor-card-value">${escapeHtml(depositor.email)}</span>
      </div>
      <div class="depositor-card-field">
        <span class="depositor-card-label">ADDRESS:</span>
        <span class="depositor-card-value">${escapeHtml(depositor.address)}</span>
      </div>
    </div>
  </a>`;
}

function depositorList(depositors) {
  const isEmpty = !depositors || depositors.length === 0;
  const body = isEmpty
    ? `<div class="no-content"><p class="no-content-text">No Depositors Found</p></div>`
    : depositors.map(depositorCard).join("");
  return `<section class="depositors">
    <div class="depositors-heading">
      <p class="depositors-title">List of Top depositors</p>
      <p class="depositors-subtitle">By the amount of the deposit portfolio</p>
    </div>
    <a class="action-button" href="depositors.html">See all Depositors<i class="action-button-arrow"></i></a>
    <div class="depositors-body">${body}</div>
  </section>`;
}
