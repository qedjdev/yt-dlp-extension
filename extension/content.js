let button = null;
let panel = null;

function createDownloadButton() {
  if (document.getElementById("ytdlp-download-btn")) return;

  button = document.createElement("button");
  button.id = "ytdlp-download-btn";
  button.innerHTML = '<svg class="ytdlp-icon" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v12M12 16l-5-5M12 16l5-5"/><line x1="5" y1="20" x2="19" y2="20"/></svg>Download';
  button.addEventListener("click", onButtonClick);

  const observer = new MutationObserver(() => {
    const target = document.querySelector(
      "#above-the-fold #top-level-buttons-computed"
    );
    if (target && !document.getElementById("ytdlp-download-btn")) {
      target.appendChild(button);
      observer.disconnect();
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });

  const target = document.querySelector(
    "#above-the-fold #top-level-buttons-computed"
  );
  if (target) {
    target.appendChild(button);
    observer.disconnect();
  }
}

function onButtonClick() {
  if (panel && panel.parentNode) {
    panel.remove();
    panel = null;
    return;
  }
  browser.runtime.sendMessage({ action: "check" }).then((response) => {
    if (response && response.connected) {
      showPanel();
    } else {
      window.open("https://yt.wakefield.fyi/setup.html", "_blank");
    }
  });
}

function showPanel() {
  panel = document.createElement("div");
  panel.id = "ytdlp-panel";
  panel.innerHTML = `
    <div class="ytdlp-panel-title">Download Video</div>
    <div class="ytdlp-formats">
      <button class="ytdlp-fmt-btn" data-format="best">Best Quality (Video + Audio)</button>
      <button class="ytdlp-fmt-btn" data-format="1080">1080p</button>
      <button class="ytdlp-fmt-btn" data-format="720">720p</button>
      <button class="ytdlp-fmt-btn" data-format="480">480p</button>
      <button class="ytdlp-fmt-btn" data-format="audio">Audio Only (MP3)</button>
    </div>
    <div id="ytdlp-status" class="ytdlp-status"></div>
  `;

  document.body.appendChild(panel);
  positionPanel();

  panel.querySelectorAll(".ytdlp-fmt-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      startDownload(btn.dataset.format);
    });
  });

  document.addEventListener("click", closePanelOnClickOutside, true);
}

function positionPanel() {
  if (!button || !panel) return;
  const rect = button.getBoundingClientRect();
  panel.style.top = (rect.bottom + window.scrollY + 8) + "px";
  panel.style.left = (rect.left + window.scrollX) + "px";
}

function closePanelOnClickOutside(e) {
  if (panel && !panel.contains(e.target) && e.target !== button) {
    panel.remove();
    panel = null;
    document.removeEventListener("click", closePanelOnClickOutside, true);
  }
}

function startDownload(format) {
  const url = window.location.href;
  setStatus("Starting download...", "info");
  disableButtons(true);

  browser.runtime.sendMessage({
    action: "download",
    url: url,
    format: format,
  });
}

function setStatus(text, type) {
  const status = document.getElementById("ytdlp-status");
  if (status) {
    status.textContent = text;
    status.className = "ytdlp-status ytdlp-status-" + type;
  }
}

function disableButtons(disabled) {
  if (panel) {
    panel.querySelectorAll(".ytdlp-fmt-btn").forEach((btn) => {
      btn.disabled = disabled;
    });
  }
}

browser.runtime.onMessage.addListener((message) => {
  switch (message.status) {
    case "starting":
      setStatus("Connecting to yt-dlp...", "info");
      break;
    case "progress":
      setStatus(message.data, "info");
      break;
    case "complete":
      setStatus("Downloaded: " + message.filename, "success");
      disableButtons(false);
      break;
    case "error":
      setStatus("Error: " + message.error, "error");
      disableButtons(false);
      break;
  }
});

function init() {
  createDownloadButton();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}

let lastUrl = location.href;
new MutationObserver(() => {
  if (location.href !== lastUrl) {
    lastUrl = location.href;
    if (location.href.includes("/watch")) {
      setTimeout(init, 1000);
    }
  }
}).observe(document.body, { childList: true, subtree: true });
