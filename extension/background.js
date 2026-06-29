const HOST_NAME = "yt_dlp_host";

browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "check") {
    checkConnection().then(sendResponse);
    return true;
  }
  if (message.action === "download") {
    handleDownload(message.url, message.format, sender.tab.id);
  }
});

function checkConnection() {
  return new Promise((resolve) => {
    try {
      const port = browser.runtime.connectNative(HOST_NAME);

      port.onMessage.addListener(() => {
        port.disconnect();
        resolve({ connected: true });
      });

      port.onDisconnect.addListener(() => {
        if (port.error) {
          openSetupPage();
          resolve({ connected: false });
        }
      });

      port.postMessage({ action: "status" });
    } catch (e) {
      openSetupPage();
      resolve({ connected: false });
    }
  });
}

async function handleDownload(url, format, tabId) {
  notifyTab(tabId, { status: "starting" });

  const port = browser.runtime.connectNative(HOST_NAME);
  let hostConnected = false;

  port.onMessage.addListener((response) => {
    hostConnected = true;
    if (response.type === "progress") {
      notifyTab(tabId, { status: "progress", data: response.data });
    } else if (response.type === "complete") {
      notifyTab(tabId, { status: "complete", filename: response.filename });
      port.disconnect();
    } else if (response.type === "error") {
      notifyTab(tabId, { status: "error", error: response.error });
      port.disconnect();
    }
  });

  port.onDisconnect.addListener(() => {
    if (!hostConnected && port.error) {
      openSetupPage();
      notifyTab(tabId, {
        status: "error",
        error: "Native host not found. Opening setup page..."
      });
    }
  });

  port.postMessage({ action: "download", url: url, format: format });
}

function notifyTab(tabId, message) {
  browser.tabs.sendMessage(tabId, message).catch(() => {});
}

function openSetupPage() {
  browser.tabs.create({ url: "https://yt.wakefield.fyi/setup.html" });
}
