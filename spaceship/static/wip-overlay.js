$(window).on('load', function() {
  if (Cookies.get('spaceshipearth_display_wip') != 'false') {
    $('#wipOverlay').modal({
      keyboard: true
    });
    Cookies.set('spaceshipearth_display_wip', 'false', { expires: 90, path: '' });
  }
});
