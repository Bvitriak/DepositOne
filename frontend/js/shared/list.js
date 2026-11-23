const PAGE_SIZES = [10, 25, 50];

const listState = { search: "", page: 1, pageSize: 10, pages: 1, sort: "", order: "desc", sortOptions: [], filter: "", filterOptions: [] };

function searchBar(placeholder) {
  return `<div class="search-bar">
    <img class="search-bar-icon" src="/assets/img/search.svg" alt="">
    <input class="search-bar-input" id="search" type="text" placeholder="${placeholder}" autocomplete="off">
  </div>`;
}

function listMenu(value, options) {
  const buttons = options
    .map((option) => `<button type="button" class="list-menu-option ${option.active ?"is-active" : ""}" ${option.attribute}>${option.text}</button>`)
    .join("");
  return `<div class="list-menu">
    <button type="button" class="list-menu-trigger" data-menu-trigger>
      <span class="list-menu-value">${value}</span>
      <i class="list-menu-arrow"></i>
    </button>
    <div class="list-menu-options">${buttons}</div>
  </div>`;
}

function pageSizeMenu() {
  const options = PAGE_SIZES.map((size) => ({
    text: size,
    active: size === listState.pageSize,
    attribute: `data-size="${size}"`,
  }));
  return listMenu(listState.pageSize, options);
}

function sortMenu() {
  if (listState.sortOptions.length === 0) {
    return "";
  }
  const current = listState.sortOptions.find((option) => option.value === listState.sort);
  const options = listState.sortOptions.map((option) => ({
    text: option.text,
    active: option.value === listState.sort,
    attribute: `data-sort="${option.value}"`,
  }));
  return listMenu(current.text, options);
}

function filterMenu() {
  if (listState.filterOptions.length === 0) {
    return "";
  }
  const current = listState.filterOptions.find((option) => option.value === listState.filter);
  const options = listState.filterOptions.map((option) => ({
    text: option.text,
    active: option.value === listState.filter,
    attribute: `data-filter="${option.value}"`,
  }));
  return listMenu(current.text, options);
}

function pagination() {
  let numbers = "";
  for (let current = 1; current <= listState.pages; current = current + 1) {
    numbers += `<button class="page-button ${current === listState.page ?"is-active" : ""}" data-page="${current}">${current}</button>`;
  }
  return `<div class="pagination-information">Page ${listState.page} of ${listState.pages}</div>
    <div class="pagination-control">
      <button class="page-button" data-page="prev"><i class="page-arrow page-arrow-left"></i></button>
      ${numbers}
      <button class="page-button" data-page="next"><i class="page-arrow page-arrow-right"></i></button>
    </div>`;
}

function entityCard(card) {
  const fields = card.fields
    .map((field) => `<div class="entity-card-field">
        <span class="entity-card-label">${field.label}</span>
        <span class="entity-card-value">${escapeHtml(field.value)}</span>
      </div>`)
    .join("");
  const body = `<div class="entity-card-head">
      <p class="entity-card-name">${escapeHtml(card.name)}</p>
      <span class="entity-card-badge">${escapeHtml(card.badge)}</span>
    </div>
    <div class="entity-card-information">${fields}</div>`;
  if (card.href) {
    return `<a class="entity-card" href="${card.href}">${body}</a>`;
  }
  return `<article class="entity-card">${body}</article>`;
}

function entityList(options) {
  const isEmpty = options.cards.length === 0;
  const count = isEmpty ? "N/A records found" : options.total + " records found";
  const grid = isEmpty
    ? `<div class="no-content"><p class="no-content-text">${options.emptyText}</p></div>`
    : options.cards.join("");
  const addButton = options.addHref
    ? `<a class="add-button" href="${options.addHref}">${options.addText}</a>`
    : "";
  return `<section class="entity-list panel">
    <div class="entity-list-head">
      <div class="entity-list-heading">
        <p class="entity-list-title">${options.title}</p>
        <p class="entity-list-count">${count}</p>
      </div>
      <div class="entity-list-controls">${addButton}${filterMenu()}${sortMenu()}${pageSizeMenu()}</div>
    </div>
    <div class="entity-list-grid">${grid}</div>
    <div class="entity-list-footer">${pagination()}</div>
  </section>`;
}

function listQuery(extraQuery) {
  let query =
    "?search=" + encodeURIComponent(listState.search) +
    "&page=" + listState.page +
    "&page_size=" + listState.pageSize;
  if (listState.sort) {
    query = query + "&sort=" + listState.sort + "&order=" + listState.order;
  }
  if (listState.filter) {
    query = query + "&status=" + encodeURIComponent(listState.filter);
  }
  if (extraQuery) {
    return query + "&" + extraQuery;
  }
  return query;
}

function serviceFallback(message) {
  return `<section class="entity-list panel">
    <div class="no-content"><p class="no-content-text">${message}</p></div>
  </section>`;
}

async function loadList(path, containerId, build, extraQuery) {
  const data = await apiRead(path + listQuery(extraQuery), { silent: true });
  if (!data) {
    document.getElementById(containerId).innerHTML = serviceFallback("Service Unavailable");
    return;
  }
  listState.page = data.page;
  listState.pages = data.pages;
  document.getElementById(containerId).innerHTML = build(data);
}

function connectList(options) {
  listState.filterOptions = options.filterOptions || [];
  if (listState.filterOptions.length > 0) {
    listState.filter = listState.filterOptions[0].value;
  }
  listState.sortOptions = options.sortOptions || [];
  if (listState.sortOptions.length > 0) {
    listState.sort = listState.sortOptions[0].value;
    listState.order = options.sortOrder;
  }

  document.getElementById("searchArea").innerHTML = searchBar(options.placeholder);
  document.getElementById("search").addEventListener("input", (event) => {
    listState.search = event.target.value;
    listState.page = 1;
    options.reload();
  });

  const listElement = document.getElementById(options.containerId);
  listElement.addEventListener("click", (event) => {
    const trigger = event.target.closest("[data-menu-trigger]");
    if (trigger) {
      trigger.parentElement.classList.toggle("open");
      return;
    }
    const size = event.target.closest("[data-size]");
    if (size) {
      listState.pageSize = Number(size.dataset.size);
      listState.page = 1;
      options.reload();
      return;
    }
    const filter = event.target.closest("[data-filter]");
    if (filter) {
      listState.filter = filter.dataset.filter;
      listState.page = 1;
      options.reload();
      return;
    }
    const sort = event.target.closest("[data-sort]");
    if (sort) {
      listState.sort = sort.dataset.sort;
      listState.page = 1;
      options.reload();
      return;
    }
    const button = event.target.closest(".page-button");
    if (!button) {
      return;
    }
    const value = button.dataset.page;
    if (value === "prev") {
      listState.page = Math.max(1, listState.page - 1);
    } else if (value === "next") {
      listState.page = Math.min(listState.pages, listState.page + 1);
    } else {
      listState.page = Number(value);
    }
    options.reload();
  });

  document.addEventListener("click", (event) => {
    if (!event.target.closest(".list-menu")) {
      const openMenu = listElement.querySelector(".list-menu.open");
      if (openMenu) {
        openMenu.classList.remove("open");
      }
    }
  });
}
