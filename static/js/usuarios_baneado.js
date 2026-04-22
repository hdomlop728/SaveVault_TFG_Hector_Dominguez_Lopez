// Actualiza en tiempo real el contador de baneo en la vista de usuario baneado.
(function() {
  var countdownEl = document.getElementById('sv-baneo-countdown');
  if (!countdownEl) return;
  var deadline = countdownEl.getAttribute('data-baneo-hasta');
  if (!deadline) return;

  function formatTiempo(segundos) {
    if (segundos <= 0) {
      return 'menos de un segundo';
    }
    var dias = Math.floor(segundos / 86400);
    var horas = Math.floor((segundos % 86400) / 3600);
    var minutos = Math.floor((segundos % 3600) / 60);
    var s = segundos % 60;
    var partes = [];
    if (dias) partes.push(dias + ' día' + (dias !== 1 ? 's' : ''));
    if (horas) partes.push(horas + ' hora' + (horas !== 1 ? 's' : ''));
    if (minutos) partes.push(minutos + ' minuto' + (minutos !== 1 ? 's' : ''));
    if (s || !partes.length) partes.push(s + ' segundo' + (s !== 1 ? 's' : ''));
    return partes.join(', ');
  }

  function actualizar() {
    var ahora = new Date();
    var fin = new Date(deadline);
    var diff = Math.max(0, Math.floor((fin - ahora) / 1000));
    countdownEl.textContent = formatTiempo(diff);
  }

  actualizar();
  setInterval(actualizar, 1000);
})();
