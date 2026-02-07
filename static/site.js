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
    var lastTouch = 0;

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

    toggle.addEventListener("touchstart", function (e) {
      lastTouch = Date.now();
      onToggle(e);
    }, { passive: false });

    toggle.addEventListener("click", function (e) {
      if (Date.now() - lastTouch < 500) return;
      onToggle(e);
    });
    toggle.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        onToggle(e);
      }
    });
  });
})();

(function () {
  var flashlights = document.querySelectorAll("[data-flashlight]");
  if (!flashlights.length) return;

  flashlights.forEach(function (flashlight) {
    var toggle = flashlight.querySelector("[data-flashlight-toggle]");
    if (!toggle) return;

    toggle.addEventListener("click", function () {
      var isOn = flashlight.classList.toggle("is-on");
      toggle.setAttribute("aria-pressed", isOn ? "true" : "false");
    });
  });
})();
