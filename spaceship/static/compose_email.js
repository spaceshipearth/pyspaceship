$(document).ready(function() {
  $(".email-composer").each((i, composer) => {
    const editor = $(composer).find(".email-editor")[0];
    console.log(editor);
    new Quill(editor, { theme: "snow" });
    const sendButton = $(composer).find(".email-send");
    sendButton.click(function() {
      var endpoint = sendButton.data("endpoint");
      var emails = $(composer)
        .find(".email-to-addresses")
        .val();
      const subjectField = $(composer).find(".email-subject");
      if (!subjectField.val().length) {
        subjectField.val(subjectField.data("default"));
      }
      var subject = subjectField.val();
      var message = $(composer)
        .find(".email-editor .ql-editor")
        .html();
      $.post(endpoint, {
        emails: emails,
        subject: subject,
        message: message
      }).done(function(json) {
        if (json["error"]) {
          alert(json["error"]);
        } else {
          alert("Email sent!");
        }
      });
    });
  });
});
