function attachListeners() {
  const messages = document.getElementById("messages");
  const composeForm = document.getElementById("compose-form");
  const modal = document.getElementById("modal-bg");
  const newEmailForm = document.getElementById("new-email-form");
  const closeBtn = document.getElementById("close-modal");

  if (!composeForm || !modal || !newEmailForm || !closeBtn || !messages) {
    console.error("Compose button not found");
    return;
  }

  composeForm.addEventListener("submit", function (e) {
    e.preventDefault();

    modal.style.display = "block";
  });

  newEmailForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    modal.style.display = "none";

    const formData = new FormData(newEmailForm);

    const subject = formData.get("subject");
    const recipient = formData.get("recipient");
    const body = formData.get("body");

    const response = await fetch("/apps/email/send", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ subject, recipient, body }),
    });

    const newMessage = document.createElement("div");
    newMessage.classList.add("message");

    if (response.ok) {
      newMessage.textContent = "Email sent successfully";
    }
    
    

    messages.appendChild(newMessage);
  });

  closeBtn.addEventListener("click", function (e) {
    e.preventDefault();
    modal.style.display = "none";
  });
}

async function fetchEmails() {
  const response = await fetch("/apps/email");
  if (!response.ok) throw new Error("Failed to load email");

  const html = await response.text();

  console.log(html);
}

window.initializeApp = function () {
  attachListeners();
  fetchEmails();
};
window.cleanupApp = function () {};
