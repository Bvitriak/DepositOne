document.querySelectorAll(".auth-eye").forEach((eye) => {
  const field = eye.previousElementSibling;
  eye.addEventListener("click", () => {
    const reveal = field.type === "password";
    field.type = reveal ? "text" : "password";
    eye.classList.toggle("off", reveal);
    eye.setAttribute("aria-label", reveal ? "Hide password" : "Show password");
  });
});

const form = document.getElementById("registerForm");
const error = document.getElementById("authError");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  error.textContent = "";
  if (form.password.value !== form.confirm.value) {
    error.textContent = "Passwords do not match";
    return;
  }
  const response = await apiPost("/api/register", {
    username: form.username.value.trim(),
    email: form.email.value.trim(),
    password: form.password.value,
  });
  if (!response) return;
  const data = await response.json();
  if (!response.ok) {
    error.textContent = data.error || "Registration failed";
    return;
  }
  localStorage.setItem("access_token", data.access_token);
  window.location.href = "../../index.html";
});
