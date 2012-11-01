"use strict";

/*
 * Confirm dialog handler
 * */
function confirmModalDialog(selector, message) {
    var deferred_result = $.Deferred();

    var dialog = $(selector);
    var dialog_id = dialog.attr('id');

    var btnCancel = $('#{0} .confirm-modal-cancel'.format(dialog_id));
    var btnConfirm = $('#{0} .confirm-modal-confirm'.format(dialog_id));

    $('#{0} #dialog-message'.format(dialog_id)).text(message);

    dialog.find('*').unbind();

    btnCancel.bind('click', function(e) {
        e.preventDefault();
        close_n_hide();
        $(window).unbind('resize');
        deferred_result.reject();
    });

    btnConfirm.bind('click', function(e) {
        e.preventDefault();
        close_n_hide();
        deferred_result.resolve();
    });

    dialog.on('click', '.close-btn', function() {
        btnCancel.click();
    });

    $(document).on('keydown', function(e) {
        if (e.which == 27) btnCancel.click();
    });

    var resize = function() {
        var w = $(window);
        dialog.css({
            'margin-left': (w.width()-dialog.outerWidth())/2+'px',
            'top': ((w.height()-dialog.outerHeight())/2)+ w.scrollTop()+"px"
        });
    };

    var show = function() {
        $('#tint').show();
        dialog.resize();
        dialog.show();
    };

    var close_n_hide = function() {
        dialog.hide();
        $('#tint').hide();
    };

    $(window).resize(function(e) {
        resize();
    });

    show();

    return deferred_result;
}

function confirmMoveModalDialog() {
    var deferred_result = $.Deferred();

    var dialog = $('#popup-move');
    var dialog_id = dialog.attr('id');

    var btnClose = dialog.find('.close-btn');
    var btnConfirm = dialog.find('.confirm-modal-confirm');

    dialog.find('*').unbind();

    btnClose.bind('click', function(e) {
        e.preventDefault();
        close_n_hide();
        $(window).unbind('resize');
        deferred_result.reject();
    });

    dialog.on('click', 'input:radio:checked', function(e) {
        btnConfirm.removeClass('disabled');
    });

    btnConfirm.bind('click', function(e) {
        e.preventDefault();
        var id = dialog.find('input:radio:checked').attr('data-album-to-move');
        if (id) {
            close_n_hide();
            deferred_result.resolve(id);
        }
    });

    $(document).on('keydown', function(e) {
        if (e.which == 27) btnClose.click();
    });

    var resize = function() {
        var w = $(window);
        dialog.css({
            'margin-left': (w.width()-dialog.outerWidth())/2+'px',
            'top': ((w.height()-dialog.outerHeight())/2)+ w.scrollTop()+"px"
        });
    };

    var show = function() {
        $('#tint').show();
        dialog.resize();
        dialog.show();
    };

    var close_n_hide = function() {
        dialog.hide();
        $('#tint').hide();
    };

    $(window).resize(function(e) {
        resize();
    });

    show();

    return deferred_result;

}


(function($) {
    $.fn.videoItemsHandler = function() {
        var $this = $(this);

        var items_list = [];
        var plurals = $this.attr('data-plurals');
        var items_count = $this.attr('data-items-count');
        var items_on_page_count = $('form .video:visible').length;
        var items_on_other_pages_count = items_count - items_on_page_count;

        var addItem = function(i) {
            items_list.push(toi(i));
            items_list = _.uniq(items_list);
        };

        var removeItem = function(i) {
            items_list = _.without(items_list, toi(i));
        };

        var getItems = function() {
            return items_list;
        };

        var deleteItems = function() {
            items_list = [];
        };

        var getOnPageItemsCount = function() {
            return $('form .video:visible').length;
        };

        var getItemsCount = function() {
            return items_on_other_pages_count + getOnPageItemsCount();
        };

        var makevideosCountText = function() {
            var count = getItemsCount();

            if (count) {
                var plural_form = ru_pluralize(count, plurals);
                return 'Всего {0} {1}'.format(count, plural_form);
            } else {
                return 'Нет ни одного видео';
            }
        };

        var showvideosCount = function() {
            $('#videos-count').text(makevideosCountText());
        };

        var hideItems = function() {
            var list = getItems();

            _.each(list, function(id) {
                var el = $('.video[data-item-id={0}]'.format(id));

                el.hide(function() {
                    el.remove();
                    updatePage();
                });
            });
        };

        var showServiceButtons = function() {
            $('#video-delete-button').show(300, 'linear');
            $('#video-move-button').show(300, 'linear');
        };

        var hideServiceButtons = function() {
            $('#video-delete-button').hide(300, 'linear');
            $('#video-move-button').hide(300, 'linear');
        };

        var updatePage = function() {
            if (getItems().length) {
                showServiceButtons();
            } else {
                hideServiceButtons();
            }
            showvideosCount();
        };

        var getDeleteMsg = function() {
            if (getItems().length > 1) {
                return 'Вы действительно хотите удалить выбранные видео?';
            } else {
                return 'Вы действительно хотите удалить выбранное видео?';
            }
        };

        var getCSRF = function() {
            return $('input[name=csrfmiddlewaretoken]').val()
        };

        updatePage();

        this.each(function() {

            $(this).on('click', '.video input[name=videos]', function(e) {
                var el = $(this);
                var id = el.val();

                if (el.is(':checked')) {
                    addItem(id);
                } else {
                    removeItem(id);
                }
                updatePage();
            });

            $(this).on('click', '#video-delete-button', function(e) {
                e.preventDefault();
                var decision = confirmModalDialog('#popup-confirm', getDeleteMsg());
                decision.done(function() {
                    $.ajax({
                        url: '/video/videos-delete/',
                        type: 'post',
                        data: {
                            csrfmiddlewaretoken: getCSRF(),
                            ids: JSON.stringify(getItems())
                        }
                    })
                        .success(function(data) {
                            if (getItems().length > 1) {
                                var msg = 'Видео удалены';
                            } else {
                                var msg = 'Видео удалено';
                            }
                            hideItems();
                            deleteItems();
                            updatePage();
                            Notify(NF_SUCCESS, msg);
                        })
                        .error(function() {
                            var msg = 'Произошла ошибка';
                            Notify(NF_ERROR, msg);
                        });
                });
            });

            $(this).on('click', '.video-menu-delete-link', function(e) {
                e.preventDefault();
                var el = $(this);
                var id = toi(el.attr('data-item-id'));

                addItem(id);

                var decision = confirmModalDialog('#popup-confirm', getDeleteMsg());
                decision.done(function() {

                    console.log(getItems());

                    $.ajax({
                        url: '/video/videos-delete/',
                        type: 'post',
                        data: {
                            csrfmiddlewaretoken: getCSRF(),
                            ids: JSON.stringify(getItems())
                        }
                    })
                        .success(function(data) {
                            if (getItems().length > 1) {
                                var msg = 'Видео удалены';
                            } else {
                                var msg = 'Видео удалено';
                            }
                            hideItems();
                            deleteItems();
                            updatePage();
                            Notify(NF_SUCCESS, msg);
                        })
                        .error(function() {
                            var msg = 'Произошла ошибка';
                            Notify(NF_ERROR, msg);
                        });
                });
            });

            $(this).on('click', '.video-menu-move-link', function(e) {
                e.preventDefault();
                var el = $(this);
                var id = toi(el.attr('data-item-id'));
                addItem(id);

                var decision = confirmMoveModalDialog();
                decision.done(function(album) {
                    $.ajax({
                        type: 'post',
                        url: '/video/video-move/',
                        data: {
                            csrfmiddlewaretoken: getCSRF(),
                            video_id: JSON.stringify(getItems()),
                            album_id: album
                        }
                    })
                        .success(function(data) {
                            if (getItems().length > 1) {
                                var msg = 'Видео перемещены';
                            } else {
                                var msg = 'Видео перемещено';
                            }
                            hideItems();
                            deleteItems();
                            updatePage();
                            Notify(NF_SUCCESS, msg);
                        })
                        .error(function() {
                            var msg = 'Произошла ошибка';
                            Notify(NF_ERROR, msg);
                        });
                });
            });

            $(this).on('click', '#video-move-button', function(e) {
                e.preventDefault();
                var count = getItems().length;

                var decision = confirmMoveModalDialog();
                decision.done(function(album) {
                    $.ajax({
                        type: 'post',
                        url: '/video/video-move/',
                        data: {
                            csrfmiddlewaretoken: getCSRF(),
                            video_id: JSON.stringify(getItems()),
                            album_id: album
                        }
                    })
                        .success(function(data) {
                            if (count > 1) {
                                var msg = 'Видео перемещены';
                            } else {
                                var msg = 'Видео перемещено';
                            }
                            hideItems();
                            deleteItems();
                            updatePage();
                            Notify(NF_SUCCESS, msg);
                        })
                        .error(function() {
                            var msg = 'Произошла ошибка';
                            Notify(NF_ERROR, msg);
                        });
                });
            });

            $(this).on('click', '.video-menu-makecover-link', function(e) {
                e.preventDefault();
                var el = $(this);
                var album_id = el.attr('data-album-id');
                var video_id = el.attr('data-video-id');

                $.ajax({
                    type: 'POST',
                    url: '/video/album'+album_id+'/set-cover/',
                    data: {
                        csrfmiddlewaretoken: getCSRF(),
                        cover: video_id
                    }
                })
                    .success(function(data) {
                        var msg = 'Обложка изменена';
                        Notify(NF_SUCCESS, msg);
                    })
                    .error(function(data) {
                        var msg = 'Произошла ошибка';
                        Notify(NF_ERROR, msg);
                    })
            });
        });
    };
})(jQuery);


(function($) {
    $.fn.videoAlbumsHandler = function() {
        var $this = $(this);

        var items_list = [];
        var plurals = $this.attr('data-plurals');
        var items_count = $this.attr('data-items-count');
        var items_on_page_count = $('form .videoalbum:visible').length;
        var items_on_other_pages_count = items_count - items_on_page_count;

        var addItem = function(i) {
            items_list.push(toi(i));
            items_list = _.uniq(items_list);
        };

        var removeItem = function(i) {
            items_list = _.without(items_list, toi(i));
        };

        var getItems = function() {
            return items_list;
        };

        var deleteItems = function() {
            items_list = [];
        };

        var getOnPageItemsCount = function() {
            return $('form .videoalbum:visible').length;
        };

        var getItemsCount = function() {
            return items_on_other_pages_count + getOnPageItemsCount();
        };

        var makevideosCountText = function() {
            var count = getItemsCount();

            if (count) {
                var plural_form = ru_pluralize(count, plurals);
                return 'Всего {0} {1}'.format(count, plural_form);
            } else {
                return 'Нет ни одного альбома';
            }
        };

        var showvideosCount = function() {
            $('#albums-count').text(makevideosCountText());
        };

        var hideItems = function() {
            var list = getItems();

            _.each(list, function(id) {
                var el = $('.videoalbum[data-item-id={0}]'.format(id));

                el.hide(function() {
                    el.remove();
                    updatePage();
                });
            });
        };

        var showServiceButtons = function() {
            $('#videoalbum-delete-button').show(300, 'linear');
        };

        var hideServiceButtons = function() {
            $('#videoalbum-delete-button').hide(300, 'linear');
        };

        var updatePage = function() {
            if (getItems().length) {
                showServiceButtons();
            } else {
                hideServiceButtons();
            }
            showvideosCount();
        };

        var getDeleteMsg = function() {
            if (getItems().length > 1) {
                return 'Вы действительно хотите удалить выбранные альбомы?';
            } else {
                return 'Вы действительно хотите удалить выбранный альбом?';
            }
        };

        var getCSRF = function() {
            return $('input[name=csrfmiddlewaretoken]').val()
        };

        updatePage();

        this.each(function() {

            $(this).on('click', '.videoalbum input[name=videoalbums]', function(e) {
                var el = $(this);
                var id = el.val();

                if (el.is(':checked')) {
                    addItem(id);
                } else {
                    removeItem(id);
                }
                updatePage();
            });

            $(this).on('click', '#videoalbum-delete-button', function(e) {
                e.preventDefault();
                var decision = confirmModalDialog('#popup-confirm', getDeleteMsg());
                decision.done(function() {
                    $.ajax({
                        url: '/video/albums-delete/',
                        type: 'post',
                        data: {
                            csrfmiddlewaretoken: getCSRF(),
                            ids: JSON.stringify(getItems())
                        }
                    })
                        .success(function(data) {
                            if (getItems().length > 1) {
                                var msg = 'Видео удалены';
                            } else {
                                var msg = 'Видео удалено';
                            }
                            hideItems();
                            deleteItems();
                            updatePage();
                            Notify(NF_SUCCESS, msg);
                        })
                        .error(function() {
                            var msg = 'Произошла ошибка';
                            Notify(NF_ERROR, msg);
                        });
                });
            });

            $(this).on('click', '.videoalbum-menu-delete-link', function(e) {
                e.preventDefault();
                var el = $(this);
                var id = toi(el.attr('data-item-id'));
                addItem(id);

                var decision = confirmModalDialog('#popup-confirm', getDeleteMsg());
                decision.done(function() {
                    $.ajax({
                        url: '/video/albums-delete/',
                        type: 'post',
                        data: {
                            csrfmiddlewaretoken: getCSRF(),
                            ids: JSON.stringify(getItems())
                        }
                    })
                        .success(function(data) {
                            if (getItems().length > 1) {
                                var msg = 'Видео удалены';
                            } else {
                                var msg = 'Видео удалено';
                            }
                            hideItems();
                            deleteItems();
                            updatePage();
                            Notify(NF_SUCCESS, msg);
                        })
                        .error(function() {
                            var msg = 'Произошла ошибка';
                            Notify(NF_ERROR, msg);
                        });
                });
            });
        });
    };
})(jQuery);

$(function() {

    $('#videos-container').videoItemsHandler();

    $('#videoalbums-container').videoAlbumsHandler();

});
