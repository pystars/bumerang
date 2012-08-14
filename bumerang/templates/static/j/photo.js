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
    $.fn.photoItemsHandler = function() {
        var $this = $(this);

        var items_list = [];
        var plurals = $this.attr('data-plurals');
        var items_count = $this.attr('data-items-count');
        var items_on_page_count = $('form .photo:visible').length;
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
            return $('form .photo:visible').length;
        };

        var getItemsCount = function() {
            return items_on_other_pages_count + getOnPageItemsCount();
        };

        var makePhotosCountText = function() {
            var count = getItemsCount();

            if (count) {
                var plural_form = ru_pluralize(count, plurals);
                return 'Всего {0} {1}'.format(count, plural_form);
            } else {
                return 'Нет ни одной фотографии';
            }
        };

        var showPhotosCount = function() {
            $('#photos-count').text(makePhotosCountText());
        };

        var hideItems = function() {
            var list = getItems();

            _.each(list, function(id) {
                var el = $('.photo[data-item-id={0}]'.format(id));

                el.hide(function() {
                    el.remove();
                    updatePage();
                });
            });
        };

        var showServiceButtons = function() {
            $('#photo-delete-button').show(300, 'linear');
            $('#photo-move-button').show(300, 'linear');
        };

        var hideServiceButtons = function() {
            $('#photo-delete-button').hide(300, 'linear');
            $('#photo-move-button').hide(300, 'linear');
        };

        var updatePage = function() {
            console.log('items_list', items_list);
            console.log('getItems()', getItems());
            if (getItems().length) {
                showServiceButtons();
            } else {
                hideServiceButtons();
            }
            showPhotosCount();
        };

        var getDeleteMsg = function() {
            if (getItems().length > 1) {
                return 'Вы действительно хотите удалить выбранные фотографии?';
            } else {
                return 'Вы действительно хотите удалить выбранную фотографию?';
            }
        };

        var getCSRF = function() {
            return $('input[name=csrfmiddlewaretoken]').val()
        };

        updatePage();

        this.each(function() {

            $(this).on('click', '.photo input[name=photos]', function(e) {
                var el = $(this);
                var id = el.val();

                if (el.is(':checked')) {
                    addItem(id);
                } else {
                    removeItem(id);
                }
                updatePage();
            });

            $(this).on('click', '#photo-delete-button', function(e) {
                e.preventDefault();
                var decision = confirmModalDialog('#popup-confirm', getDeleteMsg());
                decision.done(function() {
                    $.ajax({
                        url: '/photo/photos-delete/',
                        type: 'post',
                        data: {
                            csrfmiddlewaretoken: getCSRF(),
                            ids: JSON.stringify(getItems())
                        }
                    })
                        .success(function(data) {
                            if (getItems().length > 1) {
                                var msg = 'Фотографии удалены';
                            } else {
                                var msg = 'Фотография удалена';
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

            $(this).on('click', '.photo-menu-delete-link', function(e) {
                e.preventDefault();
                var el = $(this);
                var id = toi(el.attr('data-item-id'));
                addItem(id);

                var decision = confirmModalDialog('#popup-confirm', getDeleteMsg());
                decision.done(function() {
                    $.ajax({
                        url: '/photo/photos-delete/',
                        type: 'post',
                        data: {
                            csrfmiddlewaretoken: getCSRF(),
                            ids: JSON.stringify(getItems())
                        }
                    })
                        .success(function(data) {
                            if (getItems().length > 1) {
                                var msg = 'Фотографии удалены';
                            } else {
                                var msg = 'Фотография удалена';
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

            $(this).on('click', '.photo-menu-move-link', function(e) {
                e.preventDefault();
                var el = $(this);
                var id = toi(el.attr('data-item-id'));
                addItem(id);

                var decision = confirmMoveModalDialog();
                decision.done(function(album) {
                    $.ajax({
                        type: 'post',
                        url: '/photo/photo-move/',
                        data: {
                            csrfmiddlewaretoken: getCSRF(),
                            photo_id: JSON.stringify(getItems()),
                            album_id: album
                        }
                    })
                        .success(function(data) {
                            if (getItems().length > 1) {
                                var msg = 'Фотографии перемещены';
                            } else {
                                var msg = 'Фотография перемещена';
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

            $(this).on('click', '#photo-move-button', function(e) {
                e.preventDefault();
                var count = getItems().length;

                var decision = confirmMoveModalDialog();
                decision.done(function(album) {
                    $.ajax({
                        type: 'post',
                        url: '/photo/photo-move/',
                        data: {
                            csrfmiddlewaretoken: getCSRF(),
                            photo_id: JSON.stringify(getItems()),
                            album_id: album
                        }
                    })
                    .success(function(data) {
                        if (count > 1) {
                            var msg = 'Фотографии перемещены';
                        } else {
                            var msg = 'Фотография перемещена';
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

            $(this).on('click', '.photo-menu-makecover-link', function(e) {
                e.preventDefault();
                var el = $(this);
                var album_id = el.attr('data-album-id');
                var photo_id = el.attr('data-photo-id');

                $.ajax({
                    type: 'POST',
                    url: '/photo/album'+album_id+'/set-cover/',
                    data: {
                        csrfmiddlewaretoken: getCSRF(),
                        cover: photo_id
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
    $.fn.photoAlbumsHandler = function() {
        var $this = $(this);

        var items_list = [];
        var plurals = $this.attr('data-plurals');
        var items_count = $this.attr('data-items-count');
        var items_on_page_count = $('form .photoalbum:visible').length;
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
            return $('form .photoalbum:visible').length;
        };

        var getItemsCount = function() {
            return items_on_other_pages_count + getOnPageItemsCount();
        };

        var makePhotosCountText = function() {
            var count = getItemsCount();

            if (count) {
                var plural_form = ru_pluralize(count, plurals);
                return 'Всего {0} {1}'.format(count, plural_form);
            } else {
                return 'Нет ни одного альбома';
            }
        };

        var showPhotosCount = function() {
            $('#albums-count').text(makePhotosCountText());
        };

        var hideItems = function() {
            var list = getItems();

            _.each(list, function(id) {
                var el = $('.photoalbum[data-item-id={0}]'.format(id));

                el.hide(function() {
                    el.remove();
                    updatePage();
                });
            });
        };

        var showServiceButtons = function() {
            $('#photoalbum-delete-button').show(300, 'linear');
        };

        var hideServiceButtons = function() {
            $('#photoalbum-delete-button').hide(300, 'linear');
        };

        var updatePage = function() {
            if (getItems().length) {
                showServiceButtons();
            } else {
                hideServiceButtons();
            }
            showPhotosCount();
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

            $(this).on('click', '.photoalbum input[name=photoalbums]', function(e) {
                var el = $(this);
                var id = el.val();

                if (el.is(':checked')) {
                    addItem(id);
                } else {
                    removeItem(id);
                }
                updatePage();
            });

            $(this).on('click', '#photoalbum-delete-button', function(e) {
                e.preventDefault();
                var decision = confirmModalDialog('#popup-confirm', getDeleteMsg());
                decision.done(function() {
                    $.ajax({
                        url: '/photo/albums-delete/',
                        type: 'post',
                        data: {
                            csrfmiddlewaretoken: getCSRF(),
                            ids: JSON.stringify(getItems())
                        }
                    })
                        .success(function(data) {
                            if (getItems().length > 1) {
                                var msg = 'Фотографии удалены';
                            } else {
                                var msg = 'Фотография удалена';
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

            $(this).on('click', '.photoalbum-menu-delete-link', function(e) {
                e.preventDefault();
                var el = $(this);
                var id = toi(el.attr('data-item-id'));
                addItem(id);

                var decision = confirmModalDialog('#popup-confirm', getDeleteMsg());
                decision.done(function() {
                    $.ajax({
                        url: '/photo/albums-delete/',
                        type: 'post',
                        data: {
                            csrfmiddlewaretoken: getCSRF(),
                            ids: JSON.stringify(getItems())
                        }
                    })
                        .success(function(data) {
                            if (getItems().length > 1) {
                                var msg = 'Фотографии удалены';
                            } else {
                                var msg = 'Фотография удалена';
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

    $('#photos-container').photoItemsHandler();

    $('#photoalbums-container').photoAlbumsHandler();

});