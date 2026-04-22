// Lógica de formulario para subir guardados y mostrar información según plataforma.
document.addEventListener('DOMContentLoaded', function() {
  // Obtener configuración del JSON embebido en el HTML
  var configEl = document.getElementById('sv-upload-config');
  if (!configEl) return;

  var config = {};
  try {
    config = JSON.parse(configEl.textContent || '{}');
  } catch (e) {
    console.error('Error al parsear configuración:', e);
    return;
  }

  var GAME_DATA = config.GAME_DATA || {};
  var PLATFORM_EXTENSIONS = config.PLATFORM_EXTENSIONS || {};

  var select = document.getElementById('id_juego');
  var filtro = document.getElementById('filtro-plataforma');
  var panel = document.getElementById('game-info-panel');
  var infoExtPresel = document.getElementById('info-extensions-presel');

  // ========== Para juego preseleccionado ==========
  function actualizarInfoJuegoPreseleccionado() {
    if (!infoExtPresel) return;

    // Si el elemento tiene el atributo data-platform-id, usarlo directamente
    var platformId = infoExtPresel.getAttribute('data-platform-id');
    if (platformId) {
      var exts = PLATFORM_EXTENSIONS[platformId] || [];
      infoExtPresel.textContent = exts.length ? exts.join('  ') : '—';
      return;
    }
  }

  // Ejecutar para juego preseleccionado
  actualizarInfoJuegoPreseleccionado();

  // No hacer nada si select no existe
  if (!select) return;

  // Detectar si es un select o un input hidden
  var isSelect = select.tagName === 'SELECT';
  var opciones = isSelect ? Array.from(select.options) : [];

  // ========== Para selector de juegos (sin juego preseleccionado) ==========
  function filtrarJuegos() {
    if (!isSelect) return;
    var plat = filtro.value;
    var valActual = select.value;
    select.innerHTML = '';
    var vacia = document.createElement('option');
    vacia.value = '';
    vacia.textContent = 'Selecciona un juego';
    select.appendChild(vacia);
    opciones.forEach(function(op) {
      if (!op.value) return;
      if (!plat || (GAME_DATA[op.value] && GAME_DATA[op.value].plataforma_id === plat)) {
        select.appendChild(op.cloneNode(true));
      }
    });
    select.value = valActual;
    actualizarInfoJuego();
  }

  function actualizarInfoJuego() {
    if (!isSelect || !panel) return;
    var val = select.value;
    if (!val || !GAME_DATA[val]) {
      panel.style.display = 'none';
      return;
    }
    var g = GAME_DATA[val];
    var infoPlatform = document.getElementById('info-platform');
    var infoDeveloper = document.getElementById('info-developer');
    var infoExtensions = document.getElementById('info-extensions');

    if (infoPlatform) infoPlatform.textContent = g.plataforma;
    if (infoDeveloper) infoDeveloper.textContent = g.desarrollador;
    if (infoExtensions) {
      var exts = PLATFORM_EXTENSIONS[g.plataforma_id] || [];
      infoExtensions.textContent = exts.length ? exts.join('  ') : '—';
    }
    panel.style.display = 'block';
  }

  // ========== Event listeners ==========
  if (isSelect && filtro) {
    filtro.addEventListener('change', filtrarJuegos);
    select.addEventListener('change', actualizarInfoJuego);
  }

  // Inicializar en carga
  actualizarInfoJuego();
  actualizarInfoJuegoPreseleccionado();
});
