const code = new URLSearchParams(window.location.search).get("code");
if (code) {
  document.getElementById("errorCode").textContent = code;
  document.title = "Error " + code;
}
