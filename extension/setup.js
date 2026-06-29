document.querySelectorAll(".os-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".os-tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".os-content").forEach((c) => c.classList.remove("active"));
    tab.classList.add("active");
    document.querySelectorAll(`.os-content[data-os="${tab.dataset.os}"]`).forEach((c) => c.classList.add("active"));
  });
});

// FAQ expand/collapse
document.querySelectorAll(".faq-question").forEach((btn) => {
  btn.addEventListener("click", () => {
    const item = btn.parentElement;
    const answer = item.querySelector(".faq-answer");
    const isOpen = item.classList.contains("open");

    if (isOpen) {
      answer.style.maxHeight = null;
      item.classList.remove("open");
    } else {
      answer.style.maxHeight = answer.scrollHeight + "px";
      item.classList.add("open");
    }
  });
});

// Auto-detect OS for default tab
const ua = navigator.userAgent.toLowerCase();
let detectedOS = "windows";
if (ua.includes("mac")) detectedOS = "macos";
else if (ua.includes("linux")) detectedOS = "linux";

document.querySelectorAll(".os-tab").forEach((t) => t.classList.remove("active"));
document.querySelectorAll(".os-content").forEach((c) => c.classList.remove("active"));
document.querySelector(`.os-tab[data-os="${detectedOS}"]`).classList.add("active");
document.querySelectorAll(`.os-content[data-os="${detectedOS}"]`).forEach((c) => c.classList.add("active"));

