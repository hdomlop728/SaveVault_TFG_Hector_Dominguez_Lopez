// Autocompletado de búsqueda dentro de la página de detalle de una plataforma.
(function() {
  var input    = document.getElementById('sv-plataforma-search-input');
  var dropdown = document.getElementById('sv-plataforma-dropdown');
  if (!input || !dropdown) return;

  var slug  = window.SAVEVAULT_PLATAFORMA_SLUG || '';
  var timer = null;
  var indice = -1;

  input.addEventListener('input', function() {
    clearTimeout(timer);
    var q = this.value.trim();
    if (q.length < 2) { dropdown.style.display = 'none'; return; }
    timer = setTimeout(function() {
      fetch('/juegos/api/buscar/?q=' + encodeURIComponent(q) + '&plataforma=' + slug)
        .then(function(r) { return r.json(); })
        .then(function(d) {
          if (!d.resultados.length) { dropdown.style.display = 'none'; return; }
          dropdown.innerHTML = d.resultados.map(function(r) {
            var img = r.portada ? '<img src="' + r.portada + '" alt="">' : '<div style="width:28px;height:36px;background:#222;border-radius:3px;flex-shrink:0"></div>';
            return '<a class="sv-search-result" href="' + r.url + '">' + img + '<div class="sv-search-result-info"><div class="sv-search-result-titulo">' + r.titulo + '</div><div class="sv-search-result-plat">' + r.plataforma + '</div></div></a>';
          }).join('');
          dropdown.style.display = 'block';
          indice = -1;
        })
        .catch(function() { dropdown.style.display = 'none'; });
    }, 250);
  });

  input.addEventListener('keydown', function(e) {
    var items = dropdown.querySelectorAll('.sv-search-result');
    if (!items.length) return;
    if (e.key === 'ArrowDown') { e.preventDefault(); items.forEach(function(i) { i.classList.remove('activo'); }); indice = (indice + 1) % items.length; items[indice] && items[indice].classList.add('activo'); }
    if (e.key === 'ArrowUp')   { e.preventDefault(); items.forEach(function(i) { i.classList.remove('activo'); }); indice = (indice - 1 + items.length) % items.length; items[indice] && items[indice].classList.add('activo'); }
    if (e.key === 'Escape')    { dropdown.style.display = 'none'; }
    if (e.key === 'Enter')     { var a = dropdown.querySelector('.sv-search-result.activo'); if (a) { e.preventDefault(); window.location = a.href; } }
  });

  input.addEventListener('blur', function() {
    setTimeout(function() { dropdown.style.display = 'none'; }, 150);
  });
})();
