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

/*
* RU pluralize
* */
function ru_pluralize(value, args) {
    var args_array = args.split(',');
    var count = parseInt(value);
    var a = count % 10;
    var b = count % 100;

    if (a == 1 && b != 11) {
        return args_array[0];
    } else if ((a >= 2) && (a <= 4) && ((b < 10) || (b >= 20))) {
        return args_array[1];
    } else {
        return args_array[2];
    }
};

// Site variables
var delay_time = 10000;

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
};


/*
* Video functions
* */
function get_albums_count() {
    return $('form[name=videoalbums] .b-gallery__item:visible').length;
};

function get_videos_count() {
    return $('form[name=videos] .announ-item:visible').length;
};

/*
* Returns selected items from formname
* */
function get_selected_items(formname) {
    var checkboxes = [];
    $.each($('form[name='+formname+'] input[type=checkbox]:checked'), function(i, v) {
        checkboxes.push(parseInt($(v).attr('value')));
    });
    return checkboxes;
};

function show_albums_count() {
    var count = get_albums_count();
    if (count != 0) {
        $('#albums-count').text('Всего ' + count + ' ' + ru_pluralize(count, $('#videoalbums-plurals').text()));
    } else {
        $('#albums-count').text('Нет ни одного альбома');
    };
};

function show_videos_count() {
    var count = get_videos_count();
    if (count != 0) {
        $('#videos-count').text('Всего ' + count + ' ' + ru_pluralize(count, $('#videos-plurals').text()));
    } else {
        $('#videos-count').text('Нет ни одного видео');
    };
};

function hide_videoalbums_by_ids(ids) {
    $.each(ids, function(i, val) {
        $('#videoalbum-item-'+val).hide(300, function() {
            if (get_albums_count() == 0) {
                $('#videoalbum-empty-block').show();
            };
            show_albums_count();
        });
    });
};

function hide_videos_by_ids(ids) {
    $.each(ids, function(i, val) {
        $('#video-item-'+val).hide(300, function() {
            console.log($(this).val());
            if (get_videos_count() == 0) {
                $('#video-empty-block').show();
            };
            show_videos_count();
        });
    });
};

function delete_video(ids) {
    var url = $('form[name=videos]').attr('action');

    $.ajax({
        type: 'post',
        url: url,
        data: {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            ids: JSON.stringify(ids)
        },
        success: function(response) {
            show_notification('success', response['message']);
            hide_videos_by_ids(ids);
            show_videos_count();
        }
    })
};

function delete_albums(ids) {
    var url = $('form[name=videoalbums]').attr('action');

    $.ajax({
        type: 'post',
        url: url,
        data: {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            ids: JSON.stringify(ids)
        },
        success: function(response) {
            show_notification('success', response['message']);
            hide_videoalbums_by_ids(ids);
            show_albums_count();
        }
    })
};


function show_popup_notification(popup_id) {
    var popup = $("#" + popup_id);
    $('#tint').show();
    popup.css('margin-left', - pop.width() / 2 + 'px');
    popup.css("top", (($(window).height() - pop.outerHeight()) / 2) + $(window).scrollTop() + "px");
    popup.show();
}


/*
* Site handlers
* */
$(function() {
/*
* Video objects handlers
* */


    /*
    * Close button popup video delete handler
    * */
     $('#del-popup-cancel').click(function() {
        $('#popup-del-video').hide();
        $('#tint').hide();
     });

    /*
     * Single videoalbum delete handler
     * */
    $('.b-dropdown__link[id*=videoalbum-delete-]').click(function() {
        var id = parseInt($(this).attr('id').split('videoalbum-delete-')[1]);
        delete_albums([id]);
        return false;
    });

    /*
    * Selected videoalbums delete handler
    * */
    $('#videoalbum-delete-buton').click(function() {
        delete_albums(get_selected_items('videoalbums'));
        return false;
    });

    /*
    * Single video delete handler
    * */
    $('.b-dropdown__link[id*=video-delete-]').click(function() {
        delete_video([parseInt($(this).attr('id').split('video-delete-')[1])]);
        return false;
    });

    /*
     * Selected videos delete handler
     * */
    $('#video-delete-button').click(function() {
        var ids = get_selected_items('videos');
        if (ids.length) {
            getPopup($(this), $(this).attr('rel'));
            $('#del-popup-confirm').click(function() {
                delete_video(ids);
                $('#popup-del-video').hide();
                $('#tint').hide();
                return false;
            });
            return false;
        }
        return false;
    });

    /*
    * Single video move handler
    * */
    $('.b-dropdown__link[id*=move-video-]').click(function() {
        var id_to_move = parseInt($(this).attr('id').split('move-video-')[1]);
        $('.popup-videos-move-button').click(function() {
            $.ajax({
                type: 'POST',
                url: $('#popup-move-video form').attr('action'),
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    album_id: $('#popup-move-video input[name=album]:checked').attr('value'),
                    video_id: id_to_move
                },
                success: function(response) {
                    hide_videos_by_ids([id_to_move])
                    show_notification('success', response['message']);
                    $('#popup-move-video').hide();
                    $('#tint').hide();
                }
            });
        });
    })

    /*
    * Selected videos move
    * */
    $('#move-video-button').click(function() {
        var ids_to_move = get_selected_items('videos');
        $('.popup-videos-move-button').click(function() {
            $.ajax({
                type: 'POST',
                url: $('#popup-move-video form').attr('action'),
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    album_id: $('#popup-move-video input[name=album]:checked').attr('value'),
                    video_id: ids_to_move
                },
                success: function(response) {
                    hide_videos_by_ids(ids_to_move)
                    show_notification('success', response['message']);
                    $('#popup-move-video').hide();
                    $('#tint').hide();
                }
            });
        });
        return false;
    });

    /*
    * Make cover of album
    * */
    $('.b-dropdown__link[id*=make-cover-]').click(function() {
        var aid = parseInt($('div[id*=videoalbum-id-]').attr('id').split('videoalbum-id-')[1]);
        var vid = parseInt($(this).attr('id').split('make-cover-')[1]);

        $.ajax({
            type: 'post',
            url: '/video/album'+aid+'/set-cover/',
            data: {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                cover: vid
            },
            success: function() {
//                window.location.reload();
            }
        });
    });


    /*
    * Enter key handler for login forms
    * */
    $(document).keypress(function(e) {
        if (e.keyCode == 13) {
            if ($('#popup-login').is(':visible')) {
                $('form[name=login_form]').submit();
            } else {
                $('form[name=loginform]').submit();
            }
        }
    });

    // Submit forms
    $('.button-submit').click(function(e){
        e.preventDefault();
        $(this).parents('form').submit();
        return false;
    });

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


    /*
    * Хэндлер уведомлений
    * */
    $('.modal.notification').show(function() {
        var popup = $(this);
        var close = popup.find('.popup-close');

        $('#tint').show();
        popup.css('margin-left', - popup.width() / 2 + 'px');
        popup.css("top", (($(window).height() - popup.outerHeight()) / 2) + $(window).scrollTop() + "px");
        popup.show();

        close.bind('click', function(e) {
            e.preventDefault();
            popup.fadeOut('fast');
            $('#tint').fadeOut('fast');
        });

        window.setTimeout(function() {
            close.trigger('click');
        }, delay_time);

        $(document).keydown(function(e) {
            if (e.keyCode == 27) {
                close.trigger('click');
            }
        });
    });

    /*
     * JCrop handler
     * */
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

});
