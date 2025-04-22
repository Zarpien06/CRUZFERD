/* Script para cambiar el fondo del navbar al hacer scroll */
document.addEventListener('DOMContentLoaded', function() {
    var navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
      if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    });
  });

  document.addEventListener('DOMContentLoaded', function() {
    // Script para cambiar el fondo del navbar al hacer scroll
    var navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
      if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    });
    
    // Para que el navbar colapsable funcione correctamente en móvil
    var navLinks = document.querySelectorAll('.nav-link');
    var navCollapse = document.querySelector('.navbar-collapse');
    var bsCollapse = new bootstrap.Collapse(navCollapse, {toggle: false});
    
    navLinks.forEach(function(link) {
      link.addEventListener('click', function() {
        if (navCollapse.classList.contains('show')) {
          bsCollapse.toggle();
        }
      });
    });
  });