document.addEventListener('DOMContentLoaded', function () {
  // Responsive navbar toggle
  var btn = document.querySelector('[data-nav-toggle]');
  var menu = document.querySelector('[data-nav-menu]');
  if (btn && menu) {
    btn.addEventListener('click', function () {
      menu.classList.toggle('hidden');
      btn.classList.toggle('active');
    });
  }

  // Microinteraction: elevate buttons slightly on hover (for non-touch)
  document.querySelectorAll('button, .btn-primary-lg').forEach(function (el) {
    el.addEventListener('mouseenter', function () { el.style.transform = 'translateY(-3px)'; el.style.transition = 'transform .18s ease'; });
    el.addEventListener('mouseleave', function () { el.style.transform = ''; });
  });
});
