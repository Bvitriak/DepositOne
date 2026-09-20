function depositorCard(depositor) {
  return entityCard({
    href: "/pages/depositor/depositor-card.html?id=" + depositor.id,
    name: depositor.first_name + " " + depositor.last_name,
    badge: depositor.active_deposits + " DEPOSITS",
    fields: [
      { label: "DOB:", value: formatDate(depositor.date_of_birth) },
      { label: "COUNTRY:", value: depositor.country },
      { label: "EMAIL:", value: depositor.email },
      { label: "ADDRESS:", value: depositor.address },
    ],
  });
}

function depositorList(data) {
  return entityList({
    title: "List of Depositors",
    total: data.total,
    addText: "Add Depositor",
    addHref: "/pages/depositor/new-depositor.html",
    emptyText: "No Depositors Found",
    cards: data.depositors.map(depositorCard),
  });
}

async function loadDepositors() {
  await loadList("/api/depositors", "depositorList", depositorList);
}

connectList({
  containerId: "depositorList",
  placeholder: "Searching in list of depositors",
  reload: loadDepositors,
  sortOrder: "desc",
  sortOptions: [
    { value: "created", text: "Newest" },
    { value: "name", text: "Name" },
    { value: "country", text: "Country" },
    { value: "dob", text: "Date of Birth" },
  ],
});
loadDepositors();
