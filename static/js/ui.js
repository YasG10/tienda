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

  // Spinner helpers
  window.showSpinner = function () {
    var spinner = document.getElementById('global-spinner');
    if (spinner) spinner.classList.remove('hidden');
  };
  window.hideSpinner = function () {
    var spinner = document.getElementById('global-spinner');
    if (spinner) spinner.classList.add('hidden');
  };

  // Mostrar spinner solo en formularios que requieren procesamiento
  document.querySelectorAll('form').forEach(function (form) {
    // Solo mostrar spinner en formularios de checkout, login, registro y operaciones importantes
    var isImportantForm = form.closest('.checkout-form, .login-form, .register-form, .payment-form') ||
                          form.action.includes('checkout') || 
                          form.action.includes('login') || 
                          form.action.includes('register') ||
                          form.action.includes('payment');
    
    if (isImportantForm) {
      form.addEventListener('submit', function () {
        showSpinner();
      });
    }
  });

  // NO mostrar spinner en navegación normal - solo en operaciones específicas
  // Si necesitas spinner en algún enlace específico, añade la clase 'show-spinner'
  document.querySelectorAll('a.show-spinner').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var href = a.getAttribute('href');
      if (href && !href.startsWith('#') && !href.startsWith('javascript:') && a.target !== '_blank') {
        showSpinner();
      }
    });
  });

  // DEBUG: Mostrar spinner por 2 segundos al cargar la página para verificar visibilidad
  showSpinner();
  setTimeout(hideSpinner, 2000);
});
