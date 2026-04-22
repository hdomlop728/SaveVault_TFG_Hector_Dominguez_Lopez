// Búsqueda en vivo dentro de la lista de juegos.
(function() {
  var input    = document.getElementById('busqueda-lista-input');
  var dropdown = document.getElementById('busqueda-lista-dropdown');
  if (!input || !dropdown) return;

  var timer = null;

  input.addEventListener('input', function() {
    clearTimeout(timer);
    var q = this.value.trim();
    if (q.length < 2) {
      dropdown.style.display = 'none';
      dropdown.innerHTML = '';
      return;
    }
    timer = setTimeout(function() {
      var slug = document.querySelector('select[name="plataforma"]').value;
      var url = '/juegos/api/buscar/?q=' + encodeURIComponent(q);
      if (slug) url += '&plataforma=' + encodeURIComponent(slug);
      fetch(url)
        .then(function(r) { return r.json(); })
        .then(function(d) {
          dropdown.innerHTML = '';
          dropdown.style.display = 'none';
          if (!d.resultados.length) return;
          d.resultados.forEach(function(r) {
            var a = document.createElement('a');
            a.className = 'sv-search-result';
            a.href = r.url;
            a.innerHTML = (r.portada ? '<img src="' + r.portada + '" alt="">' : '<div style="width:28px;height:36px;background:#222;border-radius:3px;flex-shrink:0"></div>') +
              '<div class="sv-search-result-info"><div class="sv-search-result-titulo">' + r.titulo + '</div><div class="sv-search-result-plat">' + r.plataforma + '</div></div>';
            dropdown.appendChild(a);
          });
          dropdown.style.display = 'block';
        })
        .catch(function() {
          dropdown.style.display = 'none';
        });
    }, 300);
  });

  document.addEventListener('click', function(e) {
    if (!input.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.style.display = 'none';
    }
  });
})();
