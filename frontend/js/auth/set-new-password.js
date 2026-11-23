const form = document.getElementById("setPasswordForm");
const emailFromUrl = new URLSearchParams(window.location.search).get("email");

if (emailFromUrl) {
  form.email.value = emailFromUrl;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  showAuthError("");
  const response = await publicPost("/api/reset-password/confirm", {
    email: form.email.value.trim(),
    password: form.password.value,
  });
  if (!response) {
    return;
  }
  const data = await response.json();
  if (!response.ok) {
    showAuthError(data.error || "Reset failed");
    return;
  }
  window.location.href = "/pages/auth/login.html";
});
