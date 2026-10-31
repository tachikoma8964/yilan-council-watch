(function () {
  var root = document.documentElement;
  var buttons = document.querySelectorAll("[data-theme-btn]");
  var themeColor = document.querySelector('meta[name="theme-color"]');
  var SERIF_URL = "https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400&display=swap";

  function read() {
    var fromUrl = new URLSearchParams(location.search).get("theme");
    if (fromUrl === "a" || fromUrl === "b") return fromUrl;
    try {
      var saved = localStorage.getItem("sample-theme");
      if (saved === "a" || saved === "b") return saved;
    } catch (e) {}
    return "a";
  }

  // 宋體只在 B 風格載入,A 風格不下載任何網路字體
  function loadSerif() {
    if (document.getElementById("font-serif")) return;
    var link = document.createElement("link");
    link.id = "font-serif";
    link.rel = "stylesheet";
    link.href = SERIF_URL;
    document.head.appendChild(link);
  }

  function apply(name) {
    root.setAttribute("data-theme", name);
    if (name === "b") loadSerif();
    buttons.forEach(function (btn) {
      btn.setAttribute("aria-pressed", String(btn.dataset.themeBtn === name));
    });
    if (themeColor) {
      themeColor.setAttribute("content", getComputedStyle(root).getPropertyValue("--bg").trim());
    }
    try {
      localStorage.setItem("sample-theme", name);
    } catch (e) {}
  }

  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      apply(btn.dataset.themeBtn);
    });
  });

  apply(read());
})();
