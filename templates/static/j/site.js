// implement JSON.stringify serialization
var JSON = JSON || {};
JSON.stringify = JSON.stringify || function (obj) {
    var t = typeof (obj);
    if (t != "object" || obj === null) {
        // simple data type
        if (t == "string") obj = '"'+obj+'"';
        return String(obj);
    }
    else {
        // recurse array or object
        var n, v, json = [], arr = (obj && obj.constructor == Array);
        for (n in obj) {
            v = obj[n]; t = typeof(v);
            if (t == "string") v = '"'+v+'"';
            else if (t == "object" && v !== null) v = JSON.stringify(v);
            json.push((arr ? "" : '"' + n + '":') + String(v));
        }
        return (arr ? "[" : "{") + String(json) + (arr ? "]" : "}");
    }
};
// implement JSON.parse de-serialization
JSON.parse = JSON.parse || function (str) {
    if (str === "") str = '""';
    eval("var p=" + str + ";");
    return p;
};

// Site variables
var delay_time = 4000;

function show_notification(status, text) {
    var tpl = '<div class="alert-message ' + status +'">' +
              '<a class="close msg-close" href="#">×</a>' +
              '<p>'+text+'</p>' +
              '</div>'
    $('.l-page__i').prepend($(tpl));
    $('.msg-close').click(function(){
        $(this).parent().hide();
    })
    $('.alert-message').delay(delay_time).hide(300);
}

// Site handlers
$(function(){
    // Messages
    $('.msg-close').click(function(){
        $(this).parent().hide();
    })
    $('.alert-message').delay(delay_time).hide(300);

    // Avatar
    $('#id_avatar[type=file]').change(function(event){
        $('form[name=avatar_form]').submit();
    });

    function crop_initial_coords() {
        var coords = $('#id_avatar_coords').val();
        if (coords != undefined && coords != ''){
            var c = JSON.parse($('#id_avatar_coords').val());
            return [c.x, c.y, c.x2, c.y2];
        } else {
            return [0, 0, 150, 150];
        }
    }

    if ($.Jcrop) {
        $('#current_avatar').Jcrop({
            onChange: function(c){
                $('#id_avatar_coords').val(JSON.stringify(c));
            },
            bgColor:     'black',
            bgOpacity:   .5,
            minSize: [150, 150],
            setSelect: crop_initial_coords(),
            aspectRatio: 1
        });
    }
    // Videos

    function get_videos_count(){
        var vcount = ($('form[name=videosdelete] .announ-item:visible').length);
        console.log(vcount);
        $("#videos_count").html('Всего '+vcount+' видео');
    }

    $('#popup-del-video .cancel').click(function(){
        $('#popup-del-video').hide();
        $('#tint').hide();
    });

    $('.one_video_delete').click(function(){
        var checkboxes = [];
        checkboxes.push($(this).attr('videoid'));
        $.ajax({
            type: 'POST',
            url: $('form[name=videosdelete]').attr('action'),
            data: {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                checkboxes: JSON.stringify(checkboxes)
            },
            success: function(response){
                show_notification('success', response['message']);
                $.each(checkboxes, function(i, v){
                    $('#popup-del-video').hide();
                    $('#tint').hide();
                    $('form[name=videosdelete] #video_item' + v).hide(300, function(){
                        get_videos_count();
                    });
                });
            }
        });
    });

    $('#popup-del-video .videos_delete').click(function(){
        var cb_queryset = $('form[name=videosdelete] input[type=checkbox]');
        var checkboxes = [];
        $.each(cb_queryset, function(i, v) {
            if ($(v).attr('checked')) {
                checkboxes.push($(v).attr('value'));
            }
        });
        $.ajax({
            type: 'POST',
            url: $('form[name=videosdelete]').attr('action'),
            data: {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                checkboxes: JSON.stringify(checkboxes)
            },
            success: function(response){
                show_notification('success', response['message']);
                $.each(checkboxes, function(i, v){
                    $('#popup-del-video').hide();
                    $('#tint').hide();
                    $('form[name=videosdelete] #video_item' + v).hide(300, function(){
                        get_videos_count();
                    });
                });
            }
        });
    });

    $('.b-dropdown__link[id*="move_video"]').click(function(){
        var id = $(this).attr('id');
        var video_to_move = parseInt(id.split('move_video')[1]);
        $('#popup-move-video .videos_move').click(function(){
            $.ajax({
                type: 'POST',
                url: $('#popup-move-video form').attr('action'),
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    album_id: $('#popup-move-video input[name=album]:checked').attr('value'),
                    video_id: video_to_move
                },
                success: function(response) {
                    show_notification('success', response['message']);
                    $('#popup-move-video').hide();
                    $('#tint').hide();
                }
            });
        });
    });

    // Submit forms
    $('.button-submit').click(function(){
        $(this).parents('form').submit();
        return false;
    });


});
