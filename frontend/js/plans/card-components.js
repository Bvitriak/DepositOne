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

function groupThousands(digits) {
  let result = "";
  for (let index = 0; index < digits.length; index = index + 1) {
    if (index > 0 && (digits.length - index) % 3 === 0) {
      result = result + " ";
    }
    result = result + digits[index];
  }
  return result;
}

function formatMoney(value) {
  return groupThousands(String(Math.round(Number(value))));
}

function formatText(value) {
  if (value === null || value === undefined || value === "") {
    return "N/A";
  }
  return escapeHtml(value);
}

function summaryCard(label, value) {
  return `<article class="plan-summary-card">
    <p class="plan-summary-label">${label}</p>
    <p class="plan-summary-value">${value}</p>
  </article>`;
}

function summaryCards(plan) {
  const currency = escapeHtml(plan.currency);
  return `<div class="plan-cards">
    ${summaryCard("To be paid", formatMoney(plan.total_refund) + " " + currency)}
    ${summaryCard("Principal amount", formatMoney(plan.amount))}
    ${summaryCard("Accrued", formatMoney(plan.accrued))}
    ${summaryCard("Term-end accruals", formatMoney(plan.term_end_accruals))}
  </div>`;
}

function refundRow(label, value) {
  return `<div class="refund-row">
    <span class="refund-label">${label}</span>
    <span class="refund-value">${value}</span>
  </div>`;
}

function refundCard(plan) {
  const currency = escapeHtml(plan.currency);
  return `<article class="refund-card">
    <p class="refund-title">Refund calculation</p>
    <div class="refund-details">
      ${refundRow("Principal amount", formatMoney(plan.amount))}
      ${refundRow("Opening date", formatDate(plan.start_date))}
      ${refundRow("Interest rate", plan.interest_rate + "%")}
      ${refundRow("Return date", formatDate(plan.payout_date))}
    </div>
    <div class="refund-summary">
      ${refundRow("Deposit body at the end of the term", formatMoney(plan.amount) + " " + currency)}
      ${refundRow("Accrued interest", "+" + formatMoney(plan.term_end_accruals) + " " + currency)}
      ${refundRow("Total Payout", formatMoney(plan.total_refund) + " " + currency)}
    </div>
  </article>`;
}

function accrualRow(accrual) {
  const capitalization = accrual.capitalization
    ? `<img class="accrual-check" src="../assets/img/check.svg" alt="">`
    : "Payout";
  return `<tr>
    <td>${accrual.number}</td>
    <td>${formatDate(accrual.date)}</td>
    <td>${formatMoney(accrual.accrued)}</td>
    <td>${capitalization}</td>
    <td>${formatMoney(accrual.total)}</td>
  </tr>`;
}

function accrualCard(plan) {
  return `<article class="accrual-card">
    <p class="accrual-title">Accrual history</p>
    <div class="accrual-scroll">
      <table class="accrual-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Date</th>
            <th>Accrued</th>
            <th>Capitalization</th>
            <th>Including accruals</th>
          </tr>
        </thead>
        <tbody>${plan.accruals.map(accrualRow).join("")}</tbody>
      </table>
    </div>
  </article>`;
}

function depositorRow(label, value) {
  return `<div class="depositor-details-row">
    <span class="depositor-details-label">${label}</span>
    <span class="depositor-details-value">${value}</span>
  </div>`;
}

function depositorCard(plan) {
  return `<article class="depositor-details-card">
    <p class="depositor-details-title">Depositor</p>
    <div class="depositor-details">
      ${depositorRow("Name", formatText(plan.depositor))}
      ${depositorRow("Phone", formatText(plan.phone))}
      ${depositorRow("Email", formatText(plan.email))}
      ${depositorRow("Deposit ID", formatText(plan.deposit_number))}
      ${depositorRow("Contract", formatText(plan.contract_number))}
    </div>
  </article>`;
}

function planLayout(plan) {
  return `<div class="plan-layout">
    <div class="plan-main">
      ${refundCard(plan)}
      ${accrualCard(plan)}
    </div>
    ${depositorCard(plan)}
  </div>`;
}
