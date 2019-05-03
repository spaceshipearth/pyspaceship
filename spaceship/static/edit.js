$(document).ready(function() {
  $('.editable').each(function() {
    var editable = $(this);
    var textSpan = $(this).find('.edit-text');
    var title = $('<div>');
    var multiline = !!$(this).data('multiline');
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
        var editField = multiline ? $('<textarea cols="72" rows="3" class="edit-value form-control" style="margin: 8px 0">' + $(textSpan).text() + '</textarea>') : $('<input class="edit-value form-control d-inline-block" style="margin: 8px 0" type="text" value="' + $(textSpan).text() + '">');
        var editButton = $('<input class="btn btn-primary" type="button" value="Update">');
        var table = $(this).data('table');
        var id = $(this).data('id');
        var field = $(this).data('field');
        editButton.click(function() {
          var value = $(this).parent().find('.edit-value').val();
          $.post('/edit', {
            'table': table,
            'field': field,
            'id': id,
            'value': value
          }).done(function(json) {
            if (json['ok']) {
              textSpan.text(value);
              editable.popover('hide');
            }
          });
        });
        $(dialog).append(editField).append(editButton);
        return dialog;
      }
    });
  });
});
