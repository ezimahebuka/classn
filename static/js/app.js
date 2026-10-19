const loginForm = document.querySelector(".login-form");
const loadingToast = document.querySelector(".loading-toast");

loginForm?.addEventListener("submit", () => {
  loadingToast?.classList.add("is-visible");
  loadingToast?.setAttribute("aria-hidden", "false");

  const submitButton = loginForm.querySelector(".login-button");
  if (submitButton) {
    submitButton.disabled = true;
    submitButton.textContent = "LOGIN ";
    submitButton.style.opacity = "0.6";
  }
});
