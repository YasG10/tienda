document.addEventListener('DOMContentLoaded', function () {
  function refreshFloating(el) {
    var wrapper = el.closest('.floating-field');
    if (!wrapper) return;
    if (el.value && el.value.trim().length > 0) wrapper.classList.add('has-value'); else wrapper.classList.remove('has-value');
  }

  document.querySelectorAll('.floating-input').forEach(function (el) {
    // initialize
    refreshFloating(el);
    el.addEventListener('input', function () { refreshFloating(el); });
    el.addEventListener('focus', function () { el.closest('.floating-field')?.classList.add('focused'); });
    el.addEventListener('blur', function () { el.closest('.floating-field')?.classList.remove('focused'); refreshFloating(el); });
  });

  // Simple password strength meter for registration password1
  var pw = document.querySelector('input[name="password1"]');
  var meter = document.getElementById('pw-strength');
  var meterText = document.getElementById('pw-strength-text');
  if (pw && meter && meterText) {
    pw.addEventListener('input', function () {
      var val = pw.value || '';
      var score = 0;
      if (val.length >= 8) score++;
      if (/[0-9]/.test(val)) score++;
      if (/[A-Z]/.test(val)) score++;
      if (/[^A-Za-z0-9]/.test(val)) score++;
      var pct = Math.min(100, (score / 4) * 100);
      meter.style.width = pct + '%';
      if (score <= 1) { meter.className = 'pw-weak'; meterText.textContent = 'Débil'; }
      else if (score == 2) { meter.className = 'pw-fair'; meterText.textContent = 'Aceptable'; }
      else if (score == 3) { meter.className = 'pw-good'; meterText.textContent = 'Fuerte'; }
      else { meter.className = 'pw-strong'; meterText.textContent = 'Muy fuerte'; }
    });
  }
});
