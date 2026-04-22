(function() {
  // Configuración inyectada desde la plantilla.
  var config = {};
  var configEl = document.getElementById('sv-juegos-crear-data');
  if (configEl) {
    try {
      config = JSON.parse(configEl.textContent || '{}');
    } catch (e) {
      console.warn('SaveVault juegos crear config parse error:', e);
      config = {};
    }
  }
  var EXT      = config.EXT || {};
  var PLATNAME = config.PLATNAME || {};
  var prevIgdb = config.prevIgdb || '';
  var prevTitle = config.prevTitle || '';
  var prevPlat  = config.prevPlat || '';

  var searchEl   = document.getElementById('sv-search');
  var platFilter = document.getElementById('sv-platform-filter');
  var suggestEl  = document.getElementById('sv-suggestions');
  var cardEl     = document.getElementById('sv-selected-card');
  var screensEl  = document.getElementById('sv-screenshots');
  var cardTitle  = document.getElementById('sv-card-title');
  var cardMeta   = document.getElementById('sv-card-meta');
  var changeBtn  = document.getElementById('sv-change-btn');
  var hidIgdb    = document.getElementById('sv-hidden-igdb');
  var hidTitle   = document.getElementById('sv-hidden-title');
  var hidPlat    = document.getElementById('sv-hidden-platform');
  var extHint    = document.getElementById('sv-ext-hint');
  var submitBtn  = document.getElementById('sv-submit');

  if (!searchEl || !platFilter || !suggestEl || !hidIgdb || !hidTitle || !hidPlat || !extHint || !submitBtn) {
    return;
  }

  var debounceTimer = null;
  var activeIdx = -1;
  var currentResults = [];

  if (prevIgdb && prevTitle && prevPlat) {
    fetchDetail(prevIgdb, prevTitle, prevPlat);
  }

  if (prevPlat && !prevIgdb) {
    platFilter.value = prevPlat;
    searchEl.disabled = false;
    searchEl.placeholder = 'Buscar juego en IGDB…';
    searchEl.focus();
  }

  platFilter.addEventListener('change', function () {
    if (this.value) {
      searchEl.disabled = false;
      searchEl.placeholder = 'Escribe el nombre del juego…';
      searchEl.focus();
    } else {
      searchEl.disabled = true;
      searchEl.placeholder = 'Primero selecciona una plataforma…';
      hideSug();
    }
  });

  // Intercepta el texto del buscador y ejecuta la búsqueda tras un breve retraso.
  searchEl.addEventListener('input', function () {
    clearTimeout(debounceTimer);
    var q = this.value.trim();
    if (q.length < 2) { hideSug(); return; }
    showStatus('Buscando…');
    debounceTimer = setTimeout(function () { doSearch(q); }, 350);
  });

  function doSearch(q) {
    var platform = platFilter.value;
    if (!platform) { hideSug(); return; }
    var url = '/juegos/api/juegos/?q=' + encodeURIComponent(q) + (platform ? '&platform=' + platform : '');
    fetch(url)
      .then(function(r) { return r.json(); })
      .then(function(d) {
        currentResults = d.games || [];
        if (d.error) { showStatus('Búsqueda no disponible — revisa las credenciales IGDB.'); return; }
        renderSug(currentResults, q);
      })
      .catch(function() { showStatus('Error en la búsqueda. Comprueba tu conexión.'); });
  }

  function showStatus(msg) {
    suggestEl.innerHTML = '<div class="sv-ac-status"><i class="bi bi-hourglass-split me-1"></i>' + esc(msg) + '</div>';
    positionSug();
    suggestEl.style.display = 'block';
  }

  function renderSug(hits, q) {
    suggestEl.innerHTML = '';
    if (!hits.length) {
      suggestEl.innerHTML = '<div class="sv-ac-status"><i class="bi bi-emoji-neutral me-1"></i>Sin resultados</div>';
    } else {
      hits.forEach(function(g, i) {
        var el = document.createElement('div');
        el.className = 'sv-item';
        el.dataset.idx = i;

        var platName = PLATNAME[g.platform] || g.platform.replace(/_/g, ' ');
        var thumb = g.cover_url
          ? '<img class="sv-item-thumb" src="' + esc(g.cover_url.replace('t_cover_big','t_thumb')) + '" loading="lazy" alt="">'
          : '<div class="sv-item-thumb-placeholder"><i class="bi bi-controller"></i></div>';
        var year = g.year ? ' · ' + g.year : '';

        el.innerHTML = thumb +
          '<div class="sv-item-info"><div class="sv-item-title">' + hl(g.title, q) + '</div><div class="sv-item-sub">' + esc(platName) + year + '</div></div>' +
          '<span class="sv-item-plat">' + esc(platName) + '</span>';

        el.addEventListener('click', function() { fetchDetail(g.igdb_id, g.title, g.platform); });
        suggestEl.appendChild(el);
      });
    }
    positionSug();
    suggestEl.style.display = 'block';
    activeIdx = -1;
  }

  function positionSug() {
    var rect = searchEl.getBoundingClientRect();
    suggestEl.style.top   = rect.bottom + 'px';
    suggestEl.style.left  = rect.left + 'px';
    suggestEl.style.width = rect.width + 'px';
  }
  window.addEventListener('scroll', function() { if (suggestEl.style.display !== 'none') positionSug(); }, true);
  window.addEventListener('resize', function() { if (suggestEl.style.display !== 'none') positionSug(); });

  searchEl.addEventListener('keydown', function (e) {
    var items = suggestEl.querySelectorAll('.sv-item');
    if (!items.length) return;
    if (e.key === 'ArrowDown') { e.preventDefault(); activeIdx = Math.min(activeIdx + 1, items.length - 1); mark(items); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); activeIdx = Math.max(activeIdx - 1, -1); mark(items); }
    else if (e.key === 'Enter' && activeIdx >= 0) { e.preventDefault(); items[activeIdx].click(); }
    else if (e.key === 'Escape') hideSug();
  });

  function mark(items) {
    items.forEach(function(el, i) {
      el.classList.toggle('sv-active', i === activeIdx);
      if (i === activeIdx) el.scrollIntoView({ block: 'nearest' });
    });
  }

  // Carga los datos del juego seleccionado y actualiza la interfaz del formulario.
  function fetchDetail(igdbId, title, platform) {
    hideSug();
    hidIgdb.value   = igdbId;
    hidTitle.value  = title;
    hidPlat.value   = platform;

    var platName = PLATNAME[platform] || platform.replace(/_/g, ' ');
    cardTitle.textContent = title;
    cardMeta.textContent  = platName + ' · Loading…';
    screensEl.style.display = 'none';
    screensEl.innerHTML = '';
    cardEl.style.display   = 'block';
    searchEl.style.display = 'none';
    submitBtn.disabled = false;
    updateExtHint(platform);

    fetch('/juegos/api/juego/?igdb_id=' + encodeURIComponent(igdbId))
      .then(function(r) { return r.json(); })
      .then(function(d) {
        if (!d.game) return;
        var g = d.game;
        var parts = [platName];
        if (g.developer) parts.push(g.developer);
        if (g.year)      parts.push(g.year);
        cardMeta.innerHTML = parts.map(esc).join(' · ');
        if (g.description) {
          cardMeta.innerHTML += '<br><span style="font-size:.72rem;opacity:.7">' + esc(g.description.slice(0,120)) + (g.description.length > 120 ? '…' : '') + '</span>';
        }

        if (g.screenshots && g.screenshots.length) {
          screensEl.style.display = 'flex';
          g.screenshots.forEach(function(url) {
            var img = document.createElement('img');
            img.src = url;
            img.alt = '';
            img.title = 'Screenshot';
            screensEl.appendChild(img);
          });
        }
      })
      .catch(function() {
        cardMeta.textContent = platName;
      });
  }

  changeBtn.addEventListener('click', function () {
    hidIgdb.value = hidTitle.value = hidPlat.value = '';
    cardEl.style.display   = 'none';
    searchEl.style.display = '';
    searchEl.value = '';
    searchEl.disabled = !platFilter.value;
    if (!searchEl.disabled) searchEl.focus();
    submitBtn.disabled = true;
    extHint.textContent = 'Selecciona un juego para ver las extensiones válidas.';
  });

  function updateExtHint(platform) {
    var exts = EXT[platform];
    var name = PLATNAME[platform] || platform;
    extHint.innerHTML = (exts && exts.length)
      ? '<span style="color:#00ff9d">✓ Valid for ' + esc(name) + ':</span> ' + exts.join(', ')
      : 'No extension restrictions for ' + esc(name) + '.';
  }

  function hideSug() { suggestEl.style.display = 'none'; suggestEl.innerHTML = ''; activeIdx = -1; }

  function hl(text, q) {
    var i = text.toLowerCase().indexOf(q.toLowerCase());
    if (i < 0) return esc(text);
    return esc(text.slice(0,i))
      + '<strong style="color:var(--sv-accent)">' + esc(text.slice(i, i+q.length)) + '</strong>'
      + esc(text.slice(i+q.length));
  }

  function esc(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  document.addEventListener('click', function(e) { if (!e.target.closest('#sv-ac-wrap')) hideSug(); });
})();
