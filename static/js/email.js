function attachListeners() {
  const composeForm = document.getElementById("compose-form");
  const modal = document.getElementById("modal-bg");
  const newEmailForm = document.getElementById("new-email-form");
  const closeBtn = document.getElementById("close-modal");

  if (!composeForm || !modal || !newEmailForm || !closeBtn) {
    console.error("Compose button not found");
    return;
  }

  composeForm.addEventListener("submit", function (e) {
    e.preventDefault();
    modal.style.display = "block";
  });

  newEmailForm.addEventListener("submit", function (e) {
    e.preventDefault();
    modal.style.display = "none";
    
    
  });

  closeBtn.addEventListener("click", function (e) {
    e.preventDefault();
    modal.style.display = "none";
  });
}

window.initializeApp = function () {
  attachListeners();
};
window.cleanupApp = function () {};
