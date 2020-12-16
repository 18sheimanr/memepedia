function like(){
    var meme_id = event.target.getAttribute("meme-id");
    var increment_num_id = event.target.getAttribute("increments");
    $.ajax({
        type: 'POST',
        url: '/like',
        data: {'id': meme_id},
        success: function(data){
            var new_likes=parseInt($(increment_num_id).text(), 10)+1;
            $(increment_num_id).text(new_likes);
        }
    });
}

$(document).ready(function(){
    $(".like-button").click(function(){
        like()
    });
});