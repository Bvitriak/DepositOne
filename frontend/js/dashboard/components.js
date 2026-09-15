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

function depositorList(depositors) {
  const isEmpty = !depositors || depositors.length === 0;
  const body = isEmpty
    ? `<div class="no-content"><p class="no-content-text">No Depositors Found</p></div>`
    : "";
  return `<section class="depositors">
    <div class="depositors-heading">
      <p class="depositors-title">List of Top depositors</p>
      <p class="depositors-subtitle">By the amount of the deposit portfolio</p>
    </div>
    <a class="action-button" href="#">See all Depositors<i class="action-button-arrow"></i></a>
    <div class="depositors-body">${body}</div>
  </section>`;
}
