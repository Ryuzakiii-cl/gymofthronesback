 (function () {
    const toggle = document.getElementById('toggleReservas');
    const submenu = document.getElementById('submenuReservas');
    const arrow = document.querySelector('.arrow');
    if (toggle) {
      toggle.addEventListener('click', () => {
        submenu.classList.toggle('show');
        arrow.classList.toggle('rotate');
      });
    }
  })();