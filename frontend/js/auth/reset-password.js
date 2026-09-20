const form = document.getElementById("resetForm");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  showAuthError("");
  const email = form.email.value.trim();
  const response = await publicPost("/api/reset-password/check", { email: email });
  if (!response) {
    return;
  }
  const data = await response.json();
  if (!response.ok) {
    showAuthError(data.error || "Reset failed");
    return;
  }
  window.location.href = "/pages/auth/set-new-password.html?email=" + encodeURIComponent(email);
});
