(function() {
  window.addEventListener('load', () => {
    if (Cookies.get('spaceshipearth_display_wip') != 'false') {
      $('#wipOverlay').modal({
        keyboard: true
      });
      Cookies.set('spaceshipearth_display_wip', 'false', { expires: 90, path: '' });
    }
  }, false);
})();
