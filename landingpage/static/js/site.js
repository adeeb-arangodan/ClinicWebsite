(function () {
  var btn = document.getElementById('backToTop');
  if (btn) {
    var toggle = function () {
      btn.hidden = window.scrollY < 600;
    };
    window.addEventListener('scroll', toggle, { passive: true });
    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    toggle();
  }

  // Carousel progress line: restarts on every slide change, and whenever Bootstrap
  // restarts its timer after the pointer or focus leaves the carousel.
  var carousel = document.getElementById('heroCarousel');
  var bar = carousel && carousel.querySelector('.carousel-progress span');
  if (bar) {
    carousel.style.setProperty('--slide-ms', (carousel.getAttribute('data-bs-interval') || 5000) + 'ms');

    var restart = function () {
      bar.classList.remove('run');
      void bar.offsetWidth; // force reflow so the animation starts again
      bar.style.animationPlayState = 'running';
      bar.classList.add('run');
    };
    var hold = function () {
      bar.style.animationPlayState = 'paused'; // Bootstrap pauses sliding too
    };

    carousel.addEventListener('slide.bs.carousel', restart);
    carousel.addEventListener('mouseenter', hold);
    carousel.addEventListener('mouseleave', restart);
    carousel.addEventListener('focusin', hold);
    carousel.addEventListener('focusout', restart);
    restart();
  }
})();
