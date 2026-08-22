const form = document.getElementById("setPasswordForm");
const error = document.getElementById("authError");

const emailFromUrl = new URLSearchParams(window.location.search).get("email");
if (emailFromUrl) form.email.value = emailFromUrl;

const eye = document.querySelector(".auth-eye");
const password = form.password;
eye.addEventListener("click", () => {
  const reveal = password.type === "password";
  password.type = reveal ? "text" : "password";
  eye.classList.toggle("off", reveal);
  eye.setAttribute("aria-label", reveal ? "Hide password" : "Show password");
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  error.textContent = "";
  const response = await apiPost("/api/reset-password/confirm", {
    email: form.email.value.trim(),
    password: password.value,
  });
  if (!response) return;
  const data = await response.json();
  if (!response.ok) {
    error.textContent = data.error || "Reset failed";
    return;
  }
  window.location.href = "login.html";
});
