const HOST_NAME = "yt_dlp_host";

document.querySelectorAll(".os-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".os-tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".os-content").forEach((c) => c.classList.remove("active"));
    tab.classList.add("active");
    document.querySelectorAll(`.os-content[data-os="${tab.dataset.os}"]`).forEach((c) => c.classList.add("active"));
  });
});

function checkConnection() {
  const dot = document.getElementById("status-dot");
  const text = document.getElementById("status-text");

  try {
    const port = browser.runtime.connectNative(HOST_NAME);

    port.onMessage.addListener((response) => {
      if (response.type === "status") {
        dot.className = "status-dot connected";
        text.textContent = "Connected! Native host is working. You can close this tab.";
        port.disconnect();
      }
    });

    port.onDisconnect.addListener(() => {
      if (port.error) {
        dot.className = "status-dot error";
        text.textContent = "Not connected — install the native host and restart Firefox.";
      }
    });

    port.postMessage({ action: "status" });
  } catch (e) {
    dot.className = "status-dot error";
    text.textContent = "Not connected — install the native host and restart Firefox.";
  }
}

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

checkConnection();
setInterval(checkConnection, 5000);
