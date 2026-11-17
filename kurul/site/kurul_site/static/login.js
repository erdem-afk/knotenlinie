"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  $("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = $("email").value.trim();
    $("login-error").textContent = "";
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      $("login-error").textContent = "Please enter a valid email address.";
      $("email").focus();
      return;
    }
    $("login-send").disabled = true;
    try {
      await K.api("POST", "/auth/request", { email });
      $("sent-to").textContent = email;
      $("step-email").hidden = true;
      $("step-sent").hidden = false;
    } catch (err) {
      $("login-error").textContent = err.message;
    }
    $("login-send").disabled = false;
  });
  $("again").addEventListener("click", () => {
    $("step-sent").hidden = true;
    $("step-email").hidden = false;
    $("email").focus();
  });
  $("email").focus();
})();
