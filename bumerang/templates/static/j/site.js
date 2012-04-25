allowed_photos_extensions_regexp = /.+\.(bmp|jpe|jpg|jpeg|tif|gif|tiff|png)$/i;
allowed_videos_extensions_regexp =
    /.+\.(avi|mkv|vob|mp4|ogv|ogg|m4v|m2ts|mts|m2t|wmv|ogm|mov|qt|mpg|mpeg|mp4v)$/i;

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

function increasePhotoViewsCount(photoId) {
    if (photoId) {
        $.ajax({
            method: 'GET',
            url: '/photo/'+ photoId +'/update-count/',
            success: function() {

            }
        });
    }
};

function invokeUploadMessage() {
    var popup = $('#popup-upload');
    popup.css('margin-left', - popup.width() / 2 + 'px');
    popup.css("top", (($(window).height() - popup.outerHeight()) / 2) + $(window).scrollTop() + "px");
    $('#tint').show();
    popup.show();
};

function invokeConfirmDialog(text, callback) {
    var popup = $('#popup-confirm-video');

    popup.find('*').unbind();

    var cancelButton = $('#' + popup.attr('id') + ' .confirm-popup-cancel');
    var okButton = $('#' + popup.attr('id') + ' .confirm-popup-ok');

    $('#' + popup.attr('id') + ' #dialog-text').text(text);

    cancelButton.bind('click', function(e) {
        e.preventDefault();
        popup.hide();
        $('#tint').hide();
    });

    okButton.bind('click', function(e) {
        e.preventDefault();
        callback();
        cancelButton.trigger('click');
    });

    popup.css('margin-left', - popup.width() / 2 + 'px');
    popup.css("top", (($(window).height() - popup.outerHeight()) / 2) + $(window).scrollTop() + "px");
    $('#tint').show();
    popup.show();
};

function invokeMoveDialog(callback) {
    var popup = $('#popup-move-video');

    popup.find('*').unbind();

    var cancelButton = $('#' + popup.attr('id') + ' .confirm-popup-cancel');
    var closeButton = $('.b-popup__close');
    var okButton = $('#' + popup.attr('id') + ' .confirm-popup-ok');

    cancelButton.click(function(e) {
        e.preventDefault();
        popup.hide();
        $('#tint').hide();
    });

    closeButton.click(function(e) {
        e.preventDefault();
        cancelButton.trigger('click');
    });

    okButton.click(function(e) {
        e.preventDefault();
        var id = popup.find('input:radio:checked').attr('data-album-to-move');
        if (id) {
            callback(id);
        }
        cancelButton.trigger('click');
    });

    popup.css('margin-left', - popup.width() / 2 + 'px');
    popup.css("top", (($(window).height() - popup.outerHeight()) / 2) + $(window).scrollTop() + "px");
    $('#tint').show();
    popup.show();

}

/******************************************************************************
 *
 * Логика работы с видеоальбомами. Реализовано на библиотеке Backbone.js.
 * Так же исользован функционал библиотеки Underscore.js.
 *
 ******************************************************************************/

var VideoAlbumsView = Backbone.View.extend({

    el: 'body',

    albums: [],
    selected_albums: [],
    selected_videos: [],

    events: {
        'click figure[id*=videoalbum-item-]': 'clickAlbumCheckbox',
        'click article[id*=video-item-]': 'clickVideoCheckbox',

        'click #videoalbum-delete-button': 'clickAlbumDeleteButton',
        'click #video-delete-button': 'clickVideoDeleteButton',
        'click a[id*=videoalbum-delete-]': 'clickSingleAlbumDelete',
        'click a[id*=video-delete-]': 'clickSingleVideoDelete',

        'click #video-move-button': 'clickVideoMoveButton',
        'click a[id*=move-video-]': 'clickSingleVideoMove',

        'click a[id*=make-cover-]': 'clickMakeCover'
    },

    initialize: function() {
        this.updatePage();

        $(document).on('click', '.confirm-popup-cancel', function(e) {
            e.preventDefault();
        });
    },

    clickAlbumCheckbox: function(e) {
        var targetEl = e.toElement || e.relatedTarget;

        var el = $(e.target || e.srcElement);
        var videoAlbumId = parseInt(el.attr('data-videoalbum-id'));

        if (targetEl.tagName == 'INPUT') {
            if (el.is(':checked')) {
                this.selected_albums.push(videoAlbumId);
            } else {
                this.selected_albums = _.without(this.selected_albums, videoAlbumId);
            }

            this.updatePage();
        }
    },

    clickVideoCheckbox: function(e) {
        var targetEl = e.toElement || e.relatedTarget;

        var el = $(e.target || e.srcElement);
        var videoId = parseInt(el.attr('data-video-id'));

        if (targetEl.tagName == 'INPUT') {
            if (el.is(':checked')) {
                this.selected_videos.push(videoId);
            } else {
                // Delete ID from array if checkbox unchecked
                this.selected_videos = _.without(this.selected_videos, videoId);
            }

            this.updatePage();
        }
    },

    clickMakeCover: function(e) {
        e.preventDefault();

        var el = e.target || e.srcElement;

        var album_id = el.getAttribute('data-album-id');
        var video_id = el.getAttribute('data-video-id');

        $.ajax({
            type: 'post',
            url: '/video/album'+album_id+'/set-cover/',
            data: {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                cover: video_id
            },
            success: function(data) {
                if (data['result']) {show_notification('success', 'Обложка успешно изменена');}
            },
            error: function(data) {
                if (!data['result']) {show_notification('error', 'Невозможно изменить обложку');}
            }
        });
    },

    clickVideoMoveButton: function(e) {
        e.preventDefault();

        if (this.selected_albums.length > 1) {
            var msg = 'Вы действительно хотите переместить выбранные видеоролики?';
        } else {
            var msg = 'Вы действительно хотите переместить выбранный видеоролик?';
        }

        var view = this;
        invokeMoveDialog(function(id) {
            if (id) {
                $.ajax({
                    type: 'POST',
                    url: '/video/video-move/',
                    data: {
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                        video_id: JSON.stringify(view.selected_videos),
                        album_id: id
                    },
                    success: function(response) {
                        show_notification('success', response['message']);

                        view.hideVideos();
                        view.showVideosCount();
                        view.selected_videos = [];
                        view.updatePage();
                    }
                });
            }

        });
    },

    clickSingleVideoMove: function(e) {
        e.preventDefault();
        var el = $(e.target || e.srcElement);
        var videoId = parseInt(el.attr('data-video-id'));
        this.selected_videos.push(videoId);

        $(".video input:checkbox[id=checkbox-"+videoId+"]").attr("checked", "checked");
        $(".video input:checkbox[id=checkbox-"+videoId+"]").parents('.announ-item').addClass('checked');

        this.updatePage();

        if (this.selected_videos.length > 1) {
            var msg = 'Вы действительно хотите переместить выбранные видеоролики?';
        } else {
            var msg = 'Вы действительно хотите переместить выбранный видеоролик?';
        }

        var view = this;
        invokeMoveDialog(function(id) {
            if (id) {
                $.ajax({
                    type: 'POST',
                    url: '/video/video-move/',
                    data: {
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                        video_id: JSON.stringify(view.selected_videos),
                        album_id: id
                    },
                    success: function(response) {
                        show_notification('success', response['message']);

                        view.hideVideos();
                        view.showVideosCount();
                        view.selected_videos = [];
                        view.updatePage();
                    }
                });
            }

        });
    },

    clickAlbumDeleteButton: function(e) {
        e.preventDefault();

        if (this.selected_albums.length > 1) {
            var msg = 'Вы действительно хотите удалить выбранные видеольбомы?';
        } else {
            var msg = 'Вы действительно хотите удалить выбранный видеольбом?';
        }

        var view = this;
        invokeConfirmDialog(msg, function() {
            $.ajax({
                type: 'POST',
                url: '/video/albums-delete/',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    ids: JSON.stringify(view.selected_albums)
                },
                success: function(response) {
                    show_notification('success', response['message']);

                    view.hideAlbums();
                    view.showAlbumsCount();
                    view.selected_albums = [];
                    view.updatePage();
                }
            });
        });
    },

    clickSingleAlbumDelete: function(e) {
        e.preventDefault();
        var el = $(e.target || e.srcElement);
        var videoAlbumId = parseInt(el.attr('data-videoalbum-id'));
        this.selected_albums.push(videoAlbumId);
        this.selected_albums = _.uniq(this.selected_albums);

        var msg = 'Вы действительно хотите удалить выбранный видеольбом?';

        var view = this;
        invokeConfirmDialog(msg, function() {
            $.ajax({
                type: 'POST',
                url: '/video/albums-delete/',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    ids: JSON.stringify(view.selected_albums)
                },
                success: function(response) {
                    show_notification('success', response['message']);

                    view.hideAlbums();
                    view.showAlbumsCount();
                    view.selected_albums = [];
                    view.updatePage();
                }
            });
        });
    },

    clickVideoDeleteButton: function(e) {
        e.preventDefault();

        if (this.selected_videos.length > 1) {
            var msg = 'Вы действительно хотите удалить выбранные видеоролики?';
        } else {
            var msg = 'Вы действительно хотите удалить выбранный видеоролик?';
        }

        var view = this;
        invokeConfirmDialog(msg, function() {
            $.ajax({
                type: 'POST',
                url: '/video/videos-delete/',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    ids: JSON.stringify(view.selected_videos)
                },
                success: function(response) {
                    show_notification('success', response['message']);

                    view.hideVideos();
                    view.showVideosCount();
                    view.selected_videos = [];
                    view.updatePage();
                }
            });
        });
    },

    clickSingleVideoDelete: function(e) {
        e.preventDefault();
        var el = $(e.target || e.srcElement);
        var videoId = parseInt(el.attr('data-video-id'));
        this.selected_videos.push(videoId);
        this.selected_videos = _.uniq(this.selected_videos);

        var msg = 'Вы действительно хотите удалить выбранный видеоролик?';

        var view = this;
        invokeConfirmDialog(msg, function() {
            $.ajax({
                type: 'POST',
                url: '/video/videos-delete/',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    ids: JSON.stringify(view.selected_videos)
                },
                success: function(response) {
                    show_notification('success', response['message']);

                    view.hideVideos();
                    view.showVideosCount();
                    view.selected_videos = [];
                    view.updatePage();
                }
            });
        });
    },

    hideAlbums: function() {
        var view = this;
        this.selected_albums.forEach(function(e, i, a) {
            var el = $('#videoalbum-item-' + e);
            el.hide(function() {
                el.remove();
                view.updatePage();
            });
        });
    },

    hideVideos: function() {
        var view = this;
        this.selected_videos.forEach(function(e, i, a) {
            var el = $('#video-item-' + e);
            el.hide(function() {
                el.remove();
                view.updatePage();
            });
        });
    },

    hideAlbumDeleteButton: function() {
        $('#videoalbum-delete-button').hide(300, 'linear');
    },

    showAlbumDeleteButton: function() {
        $('#videoalbum-delete-button').show(300, 'linear');
    },

    hideVideoDeleteButton: function() {
        $('#video-delete-button').hide(300, 'linear');
    },

    showVideoDeleteButton: function() {
        $('#video-delete-button').show(300, 'linear');
    },

    hideVideoMoveButton: function() {
        $('#video-move-button').hide(300, 'linear');
    },

    showVideoMoveButton: function() {
        $('#video-move-button').show(300, 'linear');
    },

    getAlbumsCount: function() {
        return $('form .videoalbum:visible').length;
    },

    getVideosCount: function() {
        return $('form .video:visible').length;
    },

    showAlbumsCount: function() {
        var count = this.getAlbumsCount();
        if (count != 0) {
            $('#albums-count').text('Всего ' + count + ' ' + ru_pluralize(count, $('#videoalbums-plurals').text()));
        } else {
            $('#albums-count').text('Нет ни одного альбома');
        };
    },

    showVideosCount: function() {
        var count = this.getVideosCount();
        if (count != 0) {
            $('#videos-count').text('Всего ' + count + ' ' + ru_pluralize(count, $('#videos-plurals').text()));
        } else {
            $('#videos-count').text('Нет ни одного видеоролика');
        };
    },

    /*
     * Функция обновления страницы. Перерисовывает контролы
     * в соответствии с логикой работы представления
     */
    updatePage: function() {
        var view = this;

        view.albums = [];
        $('figure[id*=videoalbum-item-]:visible').each(function() {
            view.albums.push(this.getAttribute('data-videoalbum-id'));
        });

        if (this.selected_albums.length) {
            this.showAlbumDeleteButton();
        } else {
            this.hideAlbumDeleteButton();
        }

        if (this.selected_videos.length) {
            this.showVideoDeleteButton();
            this.showVideoMoveButton();
        } else {
            this.hideVideoDeleteButton();
            this.hideVideoMoveButton();
        }

        this.showAlbumsCount();

        if (!this.getAlbumsCount() && !$('#videoalbum-empty-block').is(':visible')) {
            var empty_block_tpl = $('#videoalbum-empty-block-tpl');
            $('#videoalbums-container').append(empty_block_tpl);
            empty_block_tpl.show(300, 'linear')
        }

        if (!this.getVideosCount() && !$('#video-empty-block').is(':visible')) {
            var empty_block_tpl = $('#video-empty-block-tpl');
            $('#videos-container').append(empty_block_tpl);
            empty_block_tpl.show(300, 'linear')
        }
    }

});


var PhotoAlbumsView = Backbone.View.extend({

    el: 'body',

    albums: [],
    selected_albums: [],
    selected_photos: [],

    events: {
        'click figure[id*=photoalbums-item-]': 'clickAlbumCheckbox',
        'click article[id*=photo-item-]': 'clickPhotoCheckbox',

        'click #photoalbum-delete-button': 'clickAlbumDeleteButton',
        'click #photo-delete-button': 'clickPhotoDeleteButton',
        'click a[id*=photoalbum-delete-]': 'clickSingleAlbumDelete',
        'click a[id*=photo-del-]': 'clickSinglePhotoDelete',

        'click #photo-move-button': 'clickPhotoMoveButton',
        'click a[id*=move-photo-]': 'clickSinglePhotoMove',

        'click a[id*=make-cover-]': 'clickMakeCover'
    },

    initialize: function() {
        this.updatePage();

        var view = this;
        $(document).on('click', '.confirm-popup-cancel', function(e) {
            e.preventDefault();
            //view.selected_photos = [];

//            $('.announ-item.photo').each(function() {
//                var el = $(this);
//                el.removeClass('checked');
//                el.find('input:checkbox').attr('checked', false);
//                view.updatePage();
//            });

        });
    },

    clickAlbumCheckbox: function(e) {
        var targetEl = e.toElement || e.relatedTarget;

        var el = $(e.target || e.srcElement);
        var photoAlbumId = parseInt(el.attr('data-photoalbum-id'));

        if (targetEl.tagName == 'INPUT') {
            if (el.is(':checked')) {
                this.selected_albums.push(photoAlbumId);
            } else {
                this.selected_albums = _.without(this.selected_albums, photoAlbumId);
            }

            this.updatePage();
        }        
    },

    clickPhotoCheckbox: function(e) {
        // Which element was clicked? It may be delete link, not checkbox, lol
        var targetEl = e.toElement || e.relatedTarget;

        var el = $(e.target || e.srcElement);
        var photoId = parseInt(el.attr('data-photo-id'));

        // And we process event only if checkbox was clicked
        if (targetEl.tagName == 'INPUT') {
            if (el.is(':checked')) {
                this.selected_photos.push(photoId);
            } else {
                // Delete ID from array if checkbox unchecked
                this.selected_photos = _.without(this.selected_photos, photoId);
            }

            this.updatePage();
        }
    },

    hideAlbums: function() {
        var view = this;
        this.selected_albums.forEach(function(e, i) {
            var el = $('#photoalbums-item-' + e);
            el.hide(function() {
                el.remove();
                view.updatePage();
            });
        });
    },

    clickAlbumDeleteButton: function(e) {
        e.preventDefault();

        if (this.selected_albums.length > 1) {
            var msg = 'Вы действительно хотите удалить выбранные фотоальбомы?';
        } else {
            var msg = 'Вы действительно хотите удалить выбранный фотоальбом?';
        }

        console.log(this.selected_albums);

        var view = this;
        invokeConfirmDialog(msg, function() {
            $.ajax({
                type: 'POST',
                url: '/photo/albums-delete/',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    ids: JSON.stringify(view.selected_albums)
                },
                success: function(response) {
                    show_notification('success', response['message']);

                    view.hideAlbums();
                    view.showAlbumsCount();
                    view.selected_albums = [];
                    view.updatePage();
                }
            });
        });
    },

    clickSingleAlbumDelete: function(e) {
        e.preventDefault();
        var el = $(e.target || e.srcElement);
        var photoAlbumId = parseInt(el.attr('data-photoalbum-id'));
        this.selected_albums.push(photoAlbumId);
        this.selected_albums = _.uniq(this.selected_albums);

        var msg = 'Вы действительно хотите удалить выбранный фотоальбом?';

        var view = this;
        invokeConfirmDialog(msg, function() {
            $.ajax({
                type: 'POST',
                url: '/photo/albums-delete/',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    ids: JSON.stringify(view.selected_albums)
                },
                success: function(response) {
                    show_notification('success', response['message']);

                    view.hideAlbums();
                    view.showAlbumsCount();
                    view.selected_albums = [];
                    view.updatePage();
                }
            });
        });
    },

    clickPhotoDeleteButton: function(e) {
        e.preventDefault();

        if (this.selected_photos.length > 1) {
            var msg = 'Вы действительно хотите удалить выбранные фотографии?';
        } else {
            var msg = 'Вы действительно хотите удалить выбранную фотографию?';
        }

        var view = this;
        invokeConfirmDialog(msg, function() {
            $.ajax({
                type: 'POST',
                url: '/photo/photos-delete/',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    ids: JSON.stringify(view.selected_photos)
                },
                success: function(response) {
                    show_notification('success', response['message']);

                    view.hidePhotos();
                    //view.showPhotosCount();
                    view.selected_photos = [];
                    view.updatePage();
                }
            });
        });
    },

    clickSinglePhotoDelete: function(e) {
        e.preventDefault();
        var el = $(e.target || e.srcElement);
        var photoId = parseInt(el.attr('data-photo-id'));
        this.selected_photos.push(photoId);
        this.selected_photos = _.uniq(this.selected_photos);

        var msg = 'Вы действительно хотите удалить выбранную фотографию?';

        var view = this;
        invokeConfirmDialog(msg, function() {
            $.ajax({
                type: 'POST',
                url: '/photo/photos-delete/',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    ids: JSON.stringify(view.selected_photos)
                },
                success: function(response) {
                    show_notification('success', response['message']);

                    view.hidePhotos();
                    view.showPhotosCount();
                    view.selected_photos = [];
                    view.updatePage();
                }
            });
        });
    },

    clickMakeCover: function(e) {
        e.preventDefault();

        var el = e.target || e.srcElement;

        var album_id = el.getAttribute('data-album-id');
        var photo_id = el.getAttribute('data-photo-id');

        $.ajax({
            type: 'POST',
            url: '/photo/album'+album_id+'/set-cover/',
            data: {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                cover: photo_id
            },
            success: function(response) {
                show_notification('success', response['message']);
            },
            error: function(data) {
                if (!data['result']) {show_notification('error', 'Невозможно изменить обложку');}
            }
        });
    },

    clickPhotoMoveButton: function(e) {
        e.preventDefault();

        if (this.selected_albums.length > 1) {
            var msg = 'Вы действительно хотите переместить выбранные фотографии?';
        } else {
            var msg = 'Вы действительно хотите переместить выбранную фотографию?';
        }

        var view = this;
        invokeMoveDialog(function(id) {
            if (id) {
                $.ajax({
                    type: 'POST',
                    url: '/photo/photo-move/',
                    data: {
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                        photo_id: JSON.stringify(view.selected_photos),
                        album_id: id
                    },
                    success: function(response) {
                        show_notification('success', response['message']);

                        view.hidePhotos();
                        view.showPhotosCount();
                        view.selected_photos = [];
                        view.updatePage();
                    }
                });
            }

        });
    },

    clickSinglePhotoMove: function(e) {
        e.preventDefault();
        var el = $(e.target || e.srcElement);
        var photoId = parseInt(el.attr('data-photo-id'));
        this.selected_photos.push(photoId);
        this.selected_photos = _.uniq(this.selected_photos);

        $(".photo input:checkbox[id=checkbox-"+photoId+"]").attr("checked", "checked");
        $(".photo input:checkbox[id=checkbox-"+photoId+"]").parents('.announ-item').addClass('checked');

        this.updatePage();

        if (this.selected_photos.length > 1) {
            var msg = 'Вы действительно хотите переместить выбранные фотографии?';
        } else {
            var msg = 'Вы действительно хотите переместить выбранную фотографию?';
        }

        var view = this;
        invokeMoveDialog(function(id) {
            if (id) {
                $.ajax({
                    type: 'POST',
                    url: '/photo/photo-move/',
                    data: {
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                        photo_id: JSON.stringify(view.selected_photos),
                        album_id: id
                    },
                    success: function(response) {
                        show_notification('success', response['message']);

                        view.hidePhotos();
                        view.showPhotosCount();
                        view.selected_photos = [];
                        view.updatePage();
                    }
                });
            }

        });
    },

    hideAlbumDeleteButton: function() {
        $('#photoalbum-delete-button').hide(300, 'linear');
    },

    showAlbumDeleteButton: function() {
        $('#photoalbum-delete-button').show(300, 'linear');
    },

    hidePhotoDeleteButton: function() {
        $('#photo-delete-button').hide(300, 'linear');
    },

    showPhotoDeleteButton: function() {
        $('#photo-delete-button').show(300, 'linear');
    },

    hidePhotoMoveButton: function() {
        $('#photo-move-button').hide(300, 'linear');
    },

    showPhotoMoveButton: function() {
        $('#photo-move-button').show(300, 'linear');
    },

    getAlbumsCount: function() {
        return $('form .photoalbum:visible').length;
    },

    getPhotosCount: function() {
        return $('form .photo:visible').length;
    },

    showAlbumsCount: function() {
        var count = this.getAlbumsCount();
        if (count != 0) {
            $('#albums-count').text('Всего ' + count + ' ' + ru_pluralize(count, $('#photoalbums-plurals').text()));
        } else {
            $('#albums-count').text('Нет ни одного альбома');
        };
    },

    hidePhotos: function() {
        var view = this;
        this.selected_photos.forEach(function(e, i, a) {
            var el = $('#photo-item-' + e);
            el.hide(function() {
                el.remove();
                view.updatePage();
            });
        });
    },

    showPhotosCount: function() {
        var count = this.getPhotosCount();
        if (count != 0) {
            $('#photos-count').text('Всего ' + count + ' ' + ru_pluralize(count, $('#photos-plurals').text()));
        } else {
            $('#photos-count').text('Нет ни одной фотографии');
        };
    },

    updatePage: function() {
        var view = this;
        view.albums = [];
        $('figure[id*=photoalbum-item-]:visible').each(function() {
            view.albums.push(this.getAttribute('data-photoalbum-id'));
        });

        if (this.selected_albums.length) {
            this.showAlbumDeleteButton();
        } else {
            this.hideAlbumDeleteButton();
        }

        if (this.selected_photos.length) {
            this.showPhotoDeleteButton();
            this.showPhotoMoveButton();
        } else {
            this.hidePhotoDeleteButton();
            this.hidePhotoMoveButton();
        }

        this.showAlbumsCount();
        this.showPhotosCount();

        if (!this.getAlbumsCount() && !$('#photoalbum-empty-block').is(':visible')) {
            var empty_block_tpl = $('#photoalbum-empty-block-tpl');
            $('#photoalbums-container').append(empty_block_tpl);
            empty_block_tpl.show(300, 'linear')
        }

        if (!this.getPhotosCount() && !$('#photo-empty-block').is(':visible')) {
            var empty_block_tpl = $('#photo-empty-block-tpl');
            $('#photos-container').append(empty_block_tpl);
            empty_block_tpl.show(300, 'linear')
        }
    }
});

/******************************************************************************/



/*
* Site handlers
* */
$(function() {

    _.templateSettings = {
        interpolate : /\{=(.+?)\}/g
    };

    /*
    * Make cover of album
    * */
//    $('.b-dropdown__link[id*=make-cover-]').click(function() {
//        var aid = parseInt($('div[id*=videoalbum-id-]').attr('id').split('videoalbum-id-')[1]);
//        var vid = parseInt($(this).attr('id').split('make-cover-')[1]);
//
//        $.ajax({
//            type: 'post',
//            url: '/video/album'+aid+'/set-cover/',
//            data: {
//                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
//                cover: vid
//            },
//            success: function() {
////                window.location.reload();
//            }
//        });
//    });


    /*
    * Enter key handler for login forms
    * */
    $(document).keypress(function(e) {
        if (e.keyCode == 13) {
            if ($('#popup-login').is(':visible')) {
                $('form[name=login_form]').submit();
            } else {
                if (!$('.modal.notification').is(':visible')) {
                    $('form[name=loginform]').submit();
                } else {
                    return;
                }
            }
        }
    });

    /*
    * Обработчик ссылки "назад"
    * */
    $('.return-to-previous-page').click(function(e) {
        if (document.referrer.match(window.location.hostname)) {
            e.preventDefault();
            window.location = document.referrer;
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
            if (e.keyCode == 27 || e.keyCode == 13) {
                close.trigger('click');
            }
        });
    });

    $('.button-video-upload').bind('click', function(e) {
        e.preventDefault();

        var filename = $("#video-upload-form input[name=original_file]").val();
        if(filename != '')
        {
            if(!allowed_videos_extensions_regexp.test(filename))
            {
                $('#popup-upload').hide();
                $('#tint').hide();
                show_notification('error',
                    'Неверный формат видеофайла'
                );
                return false;
            } else {
                invokeUploadMessage();
                $('#video-upload-form').submit();
            }
        }
    });

    $('.button-photo-upload').bind('click', function(e) {
        e.preventDefault();

        var filename = $("#photo-upload-form input[name=original_file]").val();
        if(filename != '')
        {
            if(!allowed_photos_extensions_regexp.test(filename))
            {
                $('#popup-upload').hide();
                $('#tint').hide();
                show_notification('error',
                    'Неверный формат изображения'
                );
                return false;
            } else {
                invokeUploadMessage();
                $('#photo-upload-form').submit();
            }
        } else {
            show_notification('error',
                'Выберите изображение'
            );
        }
    });

    $('.button-video-edit-upload').bind('click', function(e) {
        e.preventDefault();

        var filename = $("#video-upload-form input[name=original_file]").val();
        if(filename != '') {
            if(!allowed_videos_extensions_regexp.test(filename))
            {
                $('#popup-upload').hide();
                $('#tint').hide();
                show_notification('error',
                    'Неверный формат видеофайла'
                );
                return false;
            }
        } else {
            invokeUploadMessage();
            $('#video-upload-form').submit();
        }
    });

    $('.button-photo-edit-upload').bind('click', function(e) {
        e.preventDefault();

        var filename = $("#photo-upload-form input[name=original_file]").val();
        if (filename) {
            if(!allowed_photos_extensions_regexp.test(filename))
            {
                $('#popup-upload').hide();
                $('#tint').hide();
                show_notification('error',
                    'Неверный формат изображения'
                );
                return false;
            }
        } else {
            invokeUploadMessage();
            $('#photo-upload-form').submit();
        }
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
            minSize: [175, 175],
            setSelect: [0, 0, 175, 175],
            aspectRatio: 1
        });
    }

    $(window).bind('hashchange', function(e) {
        var hash = location.hash.replace('#','');
        if(hash == '') $(window).scrollTop(window.lastPosition);
    });
});
