$(document).ready(function() {
  $('.editable').each(function() {
    var editable = $(this);
    var title = $('<div>');
    title.append('<span>' + ($(this).data('title') || 'Edit') + '</span>');
    var closeButton = $('<span style="float: right; cursor: pointer;">&times;</span>');
    closeButton.click(function() {
      editable.popover('hide');
    });
    title.append(closeButton);
    $(this).popover({
      placement: 'bottom',
      title: title,
      html: true,
      content: function() {
        var dialog = $('<div>');
        var editField = $('<input class="form-control d-inline-block" style="margin: 8px 0" type="text" value="' + $(this).text() + '">');
        var editButton = $('<input class="btn" type="button" value="Update">');
        var table = $(this).data('table');
        var id = $(this).data('id');
        var field = $(this).data('field');
        editButton.click(function() {
          var value = $(this).parent().find('input').first().val();
          $.post('/edit', {
            'table': table,
            'field': field,
            'id': id,
            'value': value
          }).done(function(json) {
            if (json['ok']) {
              editable
                .text(value)
                .popover('hide');
            }
          });
        });
        $(dialog).append(editField).append(editButton);
        return dialog;
      }
    });
  });
});
