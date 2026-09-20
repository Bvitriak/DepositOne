const form = document.getElementById("registerForm");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  showAuthError("");
  if (form.password.value !== form.confirm.value) {
    showAuthError("Passwords do not match");
    return;
  }
  const response = await publicPost("/api/register", {
    username: form.username.value.trim(),
    email: form.email.value.trim(),
    password: form.password.value,
  });
  if (!response) {
    return;
  }
  const data = await response.json();
  if (!response.ok) {
    showAuthError(data.error || "Registration failed");
    return;
  }
  localStorage.setItem("access_token", data.access_token);
  window.location.href = "/dashboard";
});
