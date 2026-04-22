// Maneja la selección y recorte de avatar en el formulario de edición de perfil.
(function() {
  var input    = document.getElementById('id_avatar_editar');
  if (!input) return;
  var cropImg  = document.getElementById('sv-crop-image');
  var modal    = new bootstrap.Modal(document.getElementById('sv-cropper-modal'));
  var cropper  = null;
  var preview  = document.getElementById('sv-avatar-current');
  var cropData = document.querySelector('[name="avatar_crop"]');

  input.addEventListener('change', function() {
    var file = this.files[0];
    if (!file) return;
    var reader = new FileReader();
    reader.onload = function(e) {
      if (preview) {
        preview.src = e.target.result;
      } else {
        var img = document.createElement('img');
        img.src = e.target.result;
        img.className = 'sv-avatar-preview';
        img.id = 'sv-avatar-current';
        input.closest('.d-flex').insertBefore(img, input.closest('.d-flex').firstChild);
        preview = img;
      }
      cropImg.src = e.target.result;
      modal.show();
      document.getElementById('sv-cropper-modal').addEventListener('shown.bs.modal', function() {
        if (cropper) cropper.destroy();
        cropper = new Cropper(cropImg, {
          aspectRatio: 1,
          viewMode: 1,
          movable: true,
          zoomable: true,
          scalable: true,
          autoCropArea: 0.9,
          initialAspectRatio: 1,
          responsive: true,
          restore: false,
        });
      }, { once: true });
    };
    reader.readAsDataURL(file);
  });

  document.getElementById('sv-crop-confirm').addEventListener('click', function() {
    if (!cropper) return;
    var canvas = cropper.getCroppedCanvas({
      width: 800,
      height: 800,
      imageSmoothingEnabled: true,
      imageSmoothingQuality: 'high',
    });
    var base64 = canvas.toDataURL('image/png');
    cropData.value = base64;
    if (preview) {
      preview.src = base64;
    } else {
      var img = document.createElement('img');
      img.src = base64;
      img.className = 'sv-avatar-preview';
      img.id = 'sv-avatar-current';
      input.closest('.d-flex').insertBefore(img, input.closest('.d-flex').firstChild);
    }
    modal.hide();
  });

  document.getElementById('sv-cropper-modal').addEventListener('hidden.bs.modal', function() {
    if (cropper) { cropper.destroy(); cropper = null; }
  });
})();
