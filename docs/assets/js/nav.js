(function () {
  const btn   = document.querySelector('.nav-hamburger');
  const links = document.querySelector('.nav-links');
  if (btn && links) {
    btn.addEventListener('click', () => {
      links.classList.toggle('open');
      btn.setAttribute('aria-expanded', links.classList.contains('open'));
    });
  }
})();
