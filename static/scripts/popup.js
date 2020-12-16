
$(document).ready(function(){
    $(".meme-card-img").click(function(){
        var meme_id = event.target.getAttribute("meme-id");
        $.ajax({
            type: 'POST',
        // make sure you respect the same origin policy with this url:
        // http://en.wikipedia.org/wiki/Same_origin_policy
        url: '/popup',
        data: {'id': meme_id},
        success: function(data){
            $('#popup').html(data);
            $('#popupModal').modal('show');
            }
        });
    });
    window.onclick = function(event) {
       if (event.target.id == "popupModal") {
          hidePopup();
       }
    }
});

function hidePopup(){
    $('#popupModal').modal('hide');
    $('body').removeClass('modal-open');
    $('.modal-backdrop').hide();
}

