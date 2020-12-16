function readURL(input) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();

    reader.onload = function(e) {
      $('#submit_button').attr('class', 'btn btn-primary');
    }

    reader.readAsDataURL(input.files[0]); // convert to base64 string
  }
}

$("#name_input").change(function() {
  readURL(this);
});