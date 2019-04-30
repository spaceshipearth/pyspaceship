(function() {
  var closeOverlay = (event) => {
    document.getElementById('overlay-background').style.display = 'none';
    document.getElementById('overlay').style.display = 'none';
    event.preventDefault();
    event.stopPropagation();
  };
  window.addEventListener('load', () => {
    const elmts = document.getElementsByClassName('close-overlay');
    const handleclicks = Array.prototype.filter.call(elmts, (elmt) => {
      elmt.addEventListener('click', closeOverlay, false);
    });
    document.addEventListener('keydown', (e) => {
      // close overlay when escape key is pressed
      if (e.keyCode == 27) {
        closeOverlay(e);
      }
    }, false);
  }, false);
})();
