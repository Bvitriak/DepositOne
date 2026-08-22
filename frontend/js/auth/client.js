function goToError(code) {
  window.location.href = "../error.html?code=" + code;
}

async function apiPost(path, body) {
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
