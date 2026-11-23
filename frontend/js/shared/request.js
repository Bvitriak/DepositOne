function goToError(code) {
  window.location.href = "/pages/error/error.html?code=" + code;
}

function goToLogin() {
  localStorage.removeItem("access_token");
  window.location.href = "/pages/auth/login.html";
}

async function apiRequest(path, options) {
  const settings = options || {};
  const token = localStorage.getItem("access_token");
  if (!token) {
    goToLogin();
    return null;
  }
  const headers = { Authorization: "Bearer " + token };
  if (settings.body) {
    headers["Content-Type"] = "application/json";
  }
  let response;
  try {
    response = await fetch(path, { method: settings.method, headers: headers, body: settings.body });
  } catch {
    if (!settings.silent) {
      goToError(503);
    }
    return null;
  }
  if (response.status === 401) {
    goToLogin();
    return null;
  }
  const expected = settings.expectedStatuses || [];
  if (response.ok || expected.includes(response.status)) {
    return response;
  }
  if (!settings.silent) {
    goToError(response.status);
  }
  return null;
}

async function apiRead(path, options) {
  const response = await apiRequest(path, options);
  if (!response) {
    return null;
  }
  return response.json();
}

async function apiReadItem(path, listUrl) {
  const response = await apiRequest(path, { expectedStatuses: [404] });
  if (!response) {
    return null;
  }
  if (response.status === 404) {
    window.location.href = listUrl;
    return null;
  }
  return response.json();
}

async function publicPost(path, body) {
  let response;
  try {
    response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    goToError(503);
    return null;
  }
  if (response.status >= 500) {
    goToError(response.status);
    return null;
  }
  return response;
}
