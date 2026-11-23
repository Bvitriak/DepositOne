const CURRENCY_LIST = ["USD", "EUR", "RUB"];
const CURRENCY_SIGNS = { USD: "$", EUR: "€", RUB: "₽" };
const CURRENCY_ICONS = { USD: "currency-usd.svg", EUR: "currency-eur.svg", RUB: "currency-rub.svg" };
const CURRENCY_SIGN_BEFORE = ["USD"];

function currentCurrency() {
  const stored = localStorage.getItem("currency");
  if (CURRENCY_LIST.includes(stored)) {
    return stored;
  }
  return CURRENCY_LIST[0];
}

function nextCurrency() {
  const index = CURRENCY_LIST.indexOf(currentCurrency());
  return CURRENCY_LIST[(index + 1) % CURRENCY_LIST.length];
}

function currencyQuery() {
  return "currency=" + currentCurrency();
}

function currencyAmount(amount) {
  const code = currentCurrency();
  if (CURRENCY_SIGN_BEFORE.includes(code)) {
    return CURRENCY_SIGNS[code] + " " + amount;
  }
  return amount + " " + CURRENCY_SIGNS[code];
}

function compactMoney(value) {
  const number = Number(value);
  const absolute = Math.abs(number);
  if (absolute >= 1000000000) {
    return (number / 1000000000).toFixed(1) + "b";
  }
  if (absolute >= 1000000) {
    return (number / 1000000).toFixed(1) + "m";
  }
  if (absolute >= 1000) {
    return (number / 1000).toFixed(1) + "k";
  }
  return String(Math.round(number));
}

function currencyMoney(value) {
  if (value === null || value === undefined) {
    return "N/A";
  }
  const number = Number(value);
  const minus = number < 0 ? "-" : "";
  return minus + currencyAmount(compactMoney(Math.abs(number)));
}
