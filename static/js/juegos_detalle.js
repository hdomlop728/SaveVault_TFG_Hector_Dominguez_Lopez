// Gestor del lightbox de capturas en la página de detalle del juego.
(function() {
  var lb        = document.getElementById('sv-lightbox');
  var lbOverlay = document.getElementById('sv-lightbox-overlay');
  var lbImg     = document.getElementById('sv-lightbox-img');
  var lbClose   = document.getElementById('sv-lightbox-close');
  var lbLabel   = document.getElementById('sv-lightbox-label');
  var lbPrev    = document.getElementById('sv-lightbox-prev');
  var lbNext    = document.getElementById('sv-lightbox-next');
  if (!lb || !lbOverlay || !lbImg || !lbClose || !lbLabel || !lbPrev || !lbNext) return;

  var lbItems = [];
  var lbIndex = 0;

  function recopilarImagenes() {
    // Reunir las imágenes disponibles del carrusel para navegar en el lightbox.
    lbItems = [];
    document.querySelectorAll('#mediaCarousel .carousel-item').forEach(function(item) {
      var img = item.querySelector('img');
      var badge = item.querySelector('.carousel-caption span');
      if (img) lbItems.push({ src: img.src, label: badge ? badge.textContent : '' });
    });
  }

  window.abrirLightbox = function(src, label) {
    // Abrir el lightbox en la imagen seleccionada y bloquear el scroll.
    recopilarImagenes();
    lbIndex = lbItems.findIndex(function(i) { return i.src === src; });
    if (lbIndex < 0) lbIndex = 0;
    mostrarImagen(lbIndex);
    lbOverlay.style.display = 'block';
    lb.style.display = 'flex';
    lb.style.alignItems = 'center';
    lb.style.justifyContent = 'center';
    document.body.style.overflow = 'hidden';
  };

  function mostrarImagen(idx) {
    var item = lbItems[idx];
    if (!item) return;
    lbImg.src = item.src;
    lbLabel.textContent = item.label;
    lbPrev.style.visibility = lbItems.length > 1 ? 'visible' : 'hidden';
    lbNext.style.visibility = lbItems.length > 1 ? 'visible' : 'hidden';
  }

  function cerrar() {
    // Cerrar el lightbox y restaurar el estado de scroll del body.
    lbOverlay.style.display = 'none';
    lb.style.display = 'none';
    document.body.style.overflow = '';
    lbImg.src = '';
  }

  lbPrev.addEventListener('click', function() {
    lbIndex = (lbIndex - 1 + lbItems.length) % lbItems.length;
    mostrarImagen(lbIndex);
  });
  lbNext.addEventListener('click', function() {
    lbIndex = (lbIndex + 1) % lbItems.length;
    mostrarImagen(lbIndex);
  });
  lbOverlay.addEventListener('click', cerrar);
  lbClose.addEventListener('click', cerrar);
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') cerrar();
    if (e.key === 'ArrowLeft')  { lbIndex = (lbIndex - 1 + lbItems.length) % lbItems.length; mostrarImagen(lbIndex); }
    if (e.key === 'ArrowRight') { lbIndex = (lbIndex + 1) % lbItems.length; mostrarImagen(lbIndex); }
  });
})();
