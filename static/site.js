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

  var shouldUseTapToggle = function () {
    return window.matchMedia("(max-width: 1022px)").matches ||
      window.matchMedia("(pointer: coarse)").matches;
  };

  stacks.forEach(function (stack) {
    var toggle = stack.querySelector("[data-animated-toggle]") || stack;
    var lastTapTs = 0;

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

    var onTapLike = function (e) {
      if (!shouldUseTapToggle()) return;
      lastTapTs = Date.now();
      onToggle(e);
    };

    // Tablet/mobile: open/close by pressing card 1.
    toggle.addEventListener("pointerup", onTapLike);
    toggle.addEventListener("click", function (e) {
      if (!shouldUseTapToggle()) return;
      // Avoid double-fire when pointer/touch already handled the same tap.
      if (Date.now() - lastTapTs < 350) return;
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

(function () {
  var lamps = document.querySelectorAll("[data-lamp-svg]");
  if (!lamps.length) return;

  lamps.forEach(function (lamp) {
    lamp.addEventListener("pointerup", function (e) {
      var toggle = e.target.closest("[data-lamp-toggle]");
      if (!toggle) return;
      var isOn = lamp.classList.toggle("is-on");
      var lampId = lamp.getAttribute("data-lamp-id");
      if (!lampId) return;
      var overlay = document.querySelector('[data-lamp-target="' + lampId + '"]');
      if (overlay) {
        overlay.classList.toggle("is-visible", isOn);
      }
    });
  });
})();
