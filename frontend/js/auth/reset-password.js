const form = document.getElementById("resetForm");
const error = document.getElementById("authError");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  error.textContent = "";
  const email = form.email.value.trim();
  const response = await apiPost("/api/reset-password/check", { email });
  if (!response) return;
  const data = await response.json();
  if (!response.ok) {
    error.textContent = data.error || "Reset failed";
    return;
  }
  window.location.href = "set-new-password.html?email=" + encodeURIComponent(email);
});
