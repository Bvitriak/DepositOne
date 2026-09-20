const form = document.getElementById("loginForm");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  showAuthError("");
  const response = await publicPost("/api/login", {
    email: form.email.value.trim(),
    password: form.password.value,
  });
  if (!response) {
    return;
  }
  const data = await response.json();
  if (!response.ok) {
    showAuthError(data.error || "Login failed");
    return;
  }
  localStorage.setItem("access_token", data.access_token);
  window.location.href = "/dashboard";
});
