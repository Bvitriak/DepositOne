function contractCard(contract) {
  return entityCard({
    href: "/pages/contract/contract-card.html?id=" + contract.id,
    name: "№" + contract.contract_number,
    badge: contract.signing_status,
    fields: [
      { label: "ID:", value: contract.contract_code },
      { label: "DEPOSITOR:", value: contract.depositor },
      { label: "DATE:", value: formatDate(contract.contract_date) },
      { label: "DEPOSIT ID:", value: contract.deposit_number },
    ],
  });
}

function contractList(data) {
  return entityList({
    title: "List of Contracts",
    total: data.total,
    addText: "Add Contract",
    addHref: "/pages/contract/new-contract.html",
    emptyText: "No Contracts Found",
    cards: data.contracts.map(contractCard),
  });
}

async function loadContracts() {
  await loadList("/api/contracts", "contractList", contractList);
}

connectList({
  containerId: "contractList",
  placeholder: "Searching in list of contracts",
  reload: loadContracts,
  filterOptions: [
    { value: "", text: "All statuses" },
    { value: "Signed", text: "Signed" },
    { value: "Pending", text: "Pending" },
    { value: "Rejected", text: "Rejected" },
  ],
  sortOrder: "desc",
  sortOptions: [
    { value: "created", text: "Newest" },
    { value: "date", text: "Date" },
    { value: "name", text: "Depositor" },
    { value: "status", text: "Status" },
  ],
});
loadContracts();
