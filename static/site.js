(function () {
  var toggle = document.querySelector("[data-menu-toggle]");
  var panel = document.querySelector("[data-menu-panel]");
  if (!toggle || !panel) return;

  toggle.addEventListener("click", function () {
    var isOpen = panel.classList.contains("open");
    panel.classList.toggle("open", !isOpen);
  });

  document.addEventListener("click", function (e) {
    if (!panel.classList.contains("open")) return;
    if (panel.contains(e.target) || toggle.contains(e.target)) return;
    panel.classList.remove("open");
  });
})();
