(function () {
  var btn = document.getElementById('backToTop');
  if (!btn) return;

  function toggle() {
    btn.hidden = window.scrollY < 600;
  }

  window.addEventListener('scroll', toggle, { passive: true });
  btn.addEventListener('click', function () {
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
  });
  toggle();
})();
