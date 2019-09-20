function copyText(from_id, confirm_id) {
  const source = document.getElementById(from_id)

  source.select();
  source.setSelectionRange(0, 99999); /*For mobile devices*/

  document.execCommand("copy");

  const dest = document.getElementById(confirm_id);
  dest.innerHTML = 'Copied!';
}
