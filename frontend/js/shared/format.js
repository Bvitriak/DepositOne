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

function formatMoney(value, decimals) {
  const places = decimals || 0;
  const fixed = Number(value).toFixed(places);
  const parts = fixed.split(".");
  const grouped = groupThousands(parts[0]);
  if (places > 0) {
    return grouped + "." + parts[1];
  }
  return grouped;
}

function formatPercent(value) {
  if (value === null || value === undefined) {
    return "N/A";
  }
  return value + "%";
}

function formatText(value) {
  if (value === null || value === undefined || value === "") {
    return "N/A";
  }
  return escapeHtml(value);
}
