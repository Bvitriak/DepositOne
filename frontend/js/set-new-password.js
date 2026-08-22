const API = "http://localhost:8001";

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
  try {
    const response = await fetch(API + "/api/reset-password/confirm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: form.email.value.trim(), password: password.value }),
    });
    const data = await response.json();
    if (!response.ok) {
      error.textContent = data.error || "Reset failed";
      return;
    }
    window.location.href = "login.html";
  } catch {
    error.textContent = "Service unavailable. Try again later.";
  }
});
