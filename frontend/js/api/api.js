let allApis = [];

function apiCard(api) {
  const auth = api.auth === "JWT" ? "JWT" : "Public";
  return `<article class="api-card">
    <div class="api-card-head">
      <span class="api-method api-method-${api.type.toLowerCase()}">${api.type}</span>
      <code class="api-card-path">${escapeHtml(api.path)}</code>
      <button class="api-card-copy" type="button" data-copy="${escapeHtml(api.path)}" aria-label="Copy">
        <img class="api-card-copy-icon" src="/assets/img/copy.svg" alt="">
        <img class="api-card-copy-icon api-card-copy-done" src="/assets/img/check.svg" alt="">
      </button>
    </div>
    <div class="api-card-body">
      <p class="api-card-name">${escapeHtml(api.name)}</p>
      <p class="api-card-description">${escapeHtml(api.description)}</p>
    </div>
    <div class="api-card-tags">
      <span class="api-tag">${escapeHtml(api.module)}</span>
      <span class="api-tag">${escapeHtml(api.service)}</span>
      <span class="api-tag api-tag-authentication">${auth}</span>
    </div>
  </article>`;
}

function matchesSearch(api) {
  const value = listState.search.trim().toLowerCase();
  if (value === "") {
    return true;
  }
  const fields = [api.name, api.type, api.path, api.auth, api.description, api.module, api.service];
  return fields.some((field) => field.toLowerCase().includes(value));
}

function matchesMethod(api) {
  return listState.filter === "" || api.type === listState.filter;
}

function applyState() {
  const filtered = allApis.filter((api) => matchesSearch(api) && matchesMethod(api));
  listState.pages = Math.max(1, Math.ceil(filtered.length / listState.pageSize));
  if (listState.page > listState.pages) {
    listState.page = listState.pages;
  }
  const start = (listState.page - 1) * listState.pageSize;
  const visible = filtered.slice(start, start + listState.pageSize);
  document.getElementById("apiList").innerHTML = entityList({
    title: "Rest API list",
    total: filtered.length,
    emptyText: "No Information",
    cards: visible.map(apiCard),
  });
}

function selectPath(button) {
  const range = document.createRange();
  range.selectNodeContents(button.parentElement.querySelector(".api-card-path"));
  const selection = window.getSelection();
  selection.removeAllRanges();
  selection.addRange(range);
}

function copyPath(button) {
  if (!navigator.clipboard) {
    selectPath(button);
    return;
  }
  navigator.clipboard
    .writeText(button.dataset.copy)
    .then(() => {
      button.classList.add("is-copied");
      setTimeout(() => button.classList.remove("is-copied"), 1500);
    })
    .catch(() => selectPath(button));
}

async function loadApiList() {
  const data = await apiRead("/api/apis", { silent: true });
  if (!data) {
    document.getElementById("apiList").innerHTML = serviceFallback("Service Unavailable");
    return;
  }
  allApis = data.apis;
  applyState();
}

document.getElementById("apiList").addEventListener("click", (event) => {
  const copy = event.target.closest(".api-card-copy");
  if (copy) {
    copyPath(copy);
  }
});

connectList({
  containerId: "apiList",
  placeholder: "Searching in api list",
  reload: applyState,
  filterOptions: [
    { value: "", text: "All methods" },
    { value: "GET", text: "GET" },
    { value: "POST", text: "POST" },
    { value: "PUT", text: "PUT" },
    { value: "DELETE", text: "DELETE" },
  ],
});
loadApiList();
