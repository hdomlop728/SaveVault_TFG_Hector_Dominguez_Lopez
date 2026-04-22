function toggleFaq(item) {
  item.classList.toggle('open');
}
var svHelpToggle = document.getElementById('sv-help-toggle');
var svHelpMenu   = document.getElementById('sv-help-menu');
if (svHelpToggle && svHelpMenu) {
  svHelpToggle.addEventListener('click', function() {
    svHelpToggle.classList.toggle('abierto');
    svHelpMenu.classList.toggle('abierto');
  });
}
function cerrarMenu() {
  if (svHelpToggle) svHelpToggle.classList.remove('abierto');
  if (svHelpMenu)   svHelpMenu.classList.remove('abierto');
}
document.querySelectorAll('.sv-help-nav a').forEach(function(a) {
  a.addEventListener('click', function(e) {
    e.preventDefault();
    var target = document.querySelector(this.getAttribute('href'));
    if (target) target.scrollIntoView({ behavior: 'smooth' });
  });
});
