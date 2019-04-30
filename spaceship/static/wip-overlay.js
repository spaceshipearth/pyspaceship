(function() {
  var closeOverlay = (evnt) => {
    document.getElementById('overlay-background').style.display = 'none';
    document.getElementById('overlay').style.display = 'none';
    evnt.preventDefault();
    evnt.stopPropagation();
  };
  // cookie functions based on https://stackoverflow.com/questions/14573223/set-cookie-and-get-cookie-with-javascript#24103596
  var setCookie = (name, value, days) => {
    var expires = '';
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = '; expires=' + date.toUTCString();
    }
    document.cookie = name + '=' + (value || '')  + expires + '; path=/';
  };
  var getCookie = (name) => {
    var nameEQ = name + '=';
    var ca = document.cookie.split(';');
    for(var i=0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
  };
  window.addEventListener('load', () => {
    if (getCookie('spaceshipearth_display_wip') != 'false') {
      document.getElementById('overlay-background').style.display = 'block';
      document.getElementById('overlay').style.display = 'block';
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
      setCookie('spaceshipearth_display_wip', 'false', 90);
    }
  }, false);
})();
