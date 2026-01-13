document.addEventListener('DOMContentLoaded', function () {
  // Añadir clase uniforme a inputs generados por Django cuando sea necesario
  document.querySelectorAll('input, select, textarea').forEach(function (el) {
    if (!el.classList.contains('tg-field')) {
      // sólo añadir a campos dentro de formularios (evitar otros inputs del sitio)
      if (el.closest('form')) el.classList.add('tg-field');
    }
  });

  // Mostrar mensajes amigables al intentar submit si hay campos inválidos
  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      // desactivar doble submit
      var submitButtons = form.querySelectorAll('button[type=submit], input[type=submit]');
      submitButtons.forEach(function (btn) { btn.disabled = true; btn.classList.add('opacity-60', 'cursor-not-allowed'); });

      // usar validación HTML5; si hay inválidos, prevenir y mostrar indicador
      if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
        // reactivar botones
        submitButtons.forEach(function (btn) { btn.disabled = false; btn.classList.remove('opacity-60', 'cursor-not-allowed'); });

        var firstInvalid = form.querySelector(':invalid');
        if (firstInvalid) {
          firstInvalid.focus();
        }
      }
    }, false);
  });

  // Añadir listeners para togglear atributo aria-invalid según validez
  document.addEventListener('input', function (e) {
    var target = e.target;
    if (target.matches('.tg-field')) {
      if (target.checkValidity()) {
        target.removeAttribute('aria-invalid');
      } else {
        target.setAttribute('aria-invalid', 'true');
      }
    }
  }, true);
});
