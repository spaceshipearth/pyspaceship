$(document).ready(function() {
  if ($('#email-editor').length) {
    new Quill('#email-editor', {theme: 'snow'});
    $('#email-send').click(function() {
      var endpoint = $('#email-send').data('endpoint');
      var emails = $('#emails').val();
      var subject = $('#subject').val();
      var message = $('#email-editor .ql-editor').html();
      $.post(endpoint, {
        'emails': emails,
        'subject': subject,
        'message': message
      }).done(function(json) {
        if (json['error']) {
          alert(json['error']);
        } else {
          alert('Email sent!');
        }
      });
    });
  }
});
