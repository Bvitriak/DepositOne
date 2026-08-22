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
  const response = await apiPost("/api/login", {
    email: form.email.value.trim(),
    password: password.value,
  });
  if (!response) return;
  const data = await response.json();
  if (!response.ok) {
    error.textContent = data.error || "Login failed";
    return;
  }
  localStorage.setItem("access_token", data.access_token);
  window.location.href = "../../index.html";
});
