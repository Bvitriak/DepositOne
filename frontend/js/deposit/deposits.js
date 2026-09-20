function depositCard(deposit) {
  return entityCard({
    href: "/pages/deposit/deposit-card.html?id=" + deposit.id,
    name: deposit.depositor,
    badge: deposit.status,
    fields: [
      { label: "ID:", value: deposit.deposit_number },
      { label: "INTEREST RATE:", value: deposit.interest_rate + "%" },
      { label: "CURRENCY:", value: deposit.currency },
      { label: "AMOUNT:", value: formatMoney(deposit.amount) },
      { label: "DEADLINE:", value: formatDate(deposit.start_date) + " - " + formatDate(deposit.end_date) },
    ],
  });
}

function depositList(data) {
  return entityList({
    title: "List of Deposits",
    total: data.total,
    addText: "Add Deposit",
    addHref: "/pages/deposit/new-deposit.html",
    emptyText: "No Deposits Found",
    cards: data.deposits.map(depositCard),
  });
}

async function loadDeposits() {
  await loadList("/api/deposits", "depositList", depositList);
}

connectList({
  containerId: "depositList",
  placeholder: "Searching in list of deposits",
  reload: loadDeposits,
  filterOptions: [
    { value: "", text: "All statuses" },
    { value: "Active", text: "Active" },
    { value: "Pending", text: "Pending" },
    { value: "Closed", text: "Closed" },
    { value: "Blocked", text: "Blocked" },
  ],
  sortOrder: "desc",
  sortOptions: [
    { value: "created", text: "Newest" },
    { value: "name", text: "Depositor" },
    { value: "amount", text: "Amount" },
    { value: "rate", text: "Interest rate" },
    { value: "end", text: "End date" },
  ],
});
loadDeposits();
