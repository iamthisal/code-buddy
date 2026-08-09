document.getElementById("year").textContent = new Date().getFullYear();
const form = document.getElementById("interest-form");
if (form) form.addEventListener("submit", (event) => {
  event.preventDefault();
  document.getElementById("form-message").textContent = "Thanks! This is a preview. Connect a form service before publishing.";
});
