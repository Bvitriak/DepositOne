const API = "http://localhost:8001";

const form = document.getElementById("resetForm");
const error = document.getElementById("authError");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  error.textContent = "";
  const email = form.email.value.trim();
  try {
    const response = await fetch(API + "/api/reset-password/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    const data = await response.json();
    if (!response.ok) {
      error.textContent = data.error || "Reset failed";
      return;
    }
    window.location.href = "set-new-password.html?email=" + encodeURIComponent(email);
  } catch {
    error.textContent = "Service unavailable. Try again later.";
  }
});
