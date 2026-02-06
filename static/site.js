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

(function () {
  var stacks = document.querySelectorAll("[data-animated-stack]");
  if (!stacks.length) return;

  stacks.forEach(function (stack) {
    var toggle = stack.querySelector("[data-animated-toggle]") || stack;

    var setOpen = function (next) {
      stack.classList.toggle("is-open", next);
      if (toggle && toggle.setAttribute) {
        toggle.setAttribute("aria-expanded", next ? "true" : "false");
      }
    };

    var onToggle = function (e) {
      e.preventDefault();
      setOpen(!stack.classList.contains("is-open"));
    };

    toggle.addEventListener("pointerup", onToggle);
    toggle.addEventListener("touchend", onToggle, { passive: false });
    toggle.addEventListener("click", onToggle);
    toggle.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        onToggle(e);
      }
    });
  });
})();
