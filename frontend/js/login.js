const API = "http://localhost:8001";

const eye = document.getElementById("eye");
const password = document.getElementById("password");
eye.addEventListener("click", () => {
  const reveal = password.type === "password";
  password.type = reveal ? "text" : "password";
  eye.classList.toggle("off", reveal);
  eye.setAttribute("aria-label", reveal ? "Hide password" : "Show password");
});

const form = document.getElementById("loginForm");
const error = document.getElementById("authError");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  error.textContent = "";
  try {
    const response = await fetch(API + "/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: form.email.value.trim(), password: password.value }),
    });
    const data = await response.json();
    if (!response.ok) {
      error.textContent = data.error || "Login failed";
      return;
    }
    localStorage.setItem("access_token", data.access_token);
    window.location.href = "../index.html";
  } catch {
    error.textContent = "Service unavailable. Try again later.";
  }
});
