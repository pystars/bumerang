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

/*
 * Photos handler
 * */
function PhotosPageHandler() {
    /*
     * Private object's data
     * */
    var scp = this;
    var _delegateEventSplitter = /^(\S+)\s*(.*)$/;
    var events_handlers = {};
    var selected_items = [];

    var confirm_dialog_selector = '#popup-confirm';

    var events = {
        'click a[id*=photo-del-]': 'clickSinglePhotoDelete',
        'click article[id*=photo-item-]': 'clickPhotoCheckbox'
    };


    this.init = function() {

        delegateEvents(events);

    };

    /*
     * Private object's methods
     * */
    var getEventsHandlers = function() {
        return events_handlers;
    };

    var delegateEvents = function(events) {
        var events_handlers = getEventsHandlers();

        for (var key in events) {
            var method = events[key];

            if (!_.isFunction(method)) {
                method = events_handlers[method];
            }

            var match = key.match(_delegateEventSplitter);
            var eventName = match[1], selector = match[2];

            $(document).on(eventName, selector, method);
        }
    };

    var pushItem = function(id) {
        selected_items.push(toi(id));
        selected_items = _.uniq(selected_items);
    };

    var removeItem = function(id) {
        selected_items = _.without(selected_items, toi(id));
    };

    var getItems = function() {
        return selected_items;
    };

    var getPhotosCount = function() {
        return toi($('form .photo:visible').length);
    };

    var makePhotosCountText = function() {
        var plurals = $('#photos-plurals').text();
        var count = getPhotosCount();

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

    var showDeleteButton = function() {
        $('#photo-delete-button').show(300, 'linear');
    };

    var hideDeleteButton = function() {
        $('#photo-delete-button').hide(300, 'linear');
    };

    var hideItems = function() {
        var selected_items = getItems();

        _.each(selected_items, function(id) {
            var el = $('#photo-item-{0}'.format(id));

            el.hide(function() {
                el.remove();
                updatePage();
            });
        });
    };

    var updatePage = function() {
        if (selected_items.length) {
            showDeleteButton();
        } else {
            hideDeleteButton();
        }

        showPhotosCount();
    };

//    updatePage: function() {
//        var view = this;
//        view.albums = [];
//        $('figure[id*=photoalbum-item-]:visible').each(function() {
//            view.albums.push(this.getAttribute('data-photoalbum-id'));
//        });
//
//        if (this.selected_albums.length) {
//            this.showAlbumDeleteButton();
//        } else {
//            this.hideAlbumDeleteButton();
//        }
//
//        if (this.selected_photos.length) {
//            this.showPhotoDeleteButton();
//            this.showPhotoMoveButton();
//        } else {
//            this.hidePhotoDeleteButton();
//            this.hidePhotoMoveButton();
//        }
//
//        this.showAlbumsCount();
//        this.showPhotosCount();
//
//        if (!this.getAlbumsCount() && !$('#photoalbum-empty-block').is(':visible')) {
//            var empty_block_tpl = $('#photoalbum-empty-block-tpl');
//            $('#photoalbums-container').append(empty_block_tpl);
//            empty_block_tpl.show(300, 'linear')
//        }
//
//        if (!this.getPhotosCount() && !$('#photo-empty-block').is(':visible')) {
//            var empty_block_tpl = $('#photo-empty-block-tpl');
//            $('#photos-container').append(empty_block_tpl);
//            empty_block_tpl.show(300, 'linear')
//        }
//    }

    /*
     * Events handlers functions
     */
    events_handlers = {

//        clickPhotoCheckbox: function(e) {
//            var el = $(e.target || e.srcElement);
//            var photoId = parseInt(el.attr('data-photo-id'));
//
//            if (el.is(':checked')) {
//                this.selected_photos.push(photoId);
//            } else {
//                // Delete ID from array if checkbox unchecked
//                this.selected_photos = _.without(this.selected_photos, photoId);
//            }
//
//            this.updatePage();
//        },
//
        clickPhotoCheckbox: function(e) {
            var el = $(e.target || e.srcElement);
            var photoId = toi(el.attr('data-photo-id'));

            if (el.is(':checked')) {
                pushItem(photoId);
            } else {
                removeItem(photoId);
            }

            updatePage();
        },

        clickSinglePhotoDelete: function(e) {
            e.preventDefault();
            var el = $(e.target || e.srcElement);
            var photoId = toi(el.attr('data-photo-id'));

            pushItem(photoId);

            var msg = 'Вы действительно хотите удалить выбранную фотографию?';
            var decision = confirmModalDialog(confirm_dialog_selector, msg);

            decision.done(function() {
                Notify(NF_SUCCESS, 'ok');
                hideItems();
                updatePage();
            });

            decision.fail(function() {
                Notify(NF_ERROR, 'cancelled');
            });
        }

    };

    /*
     * Init Handler object
     * */
    this.init();

};


$(function() {

    if ($('#photoalbums-container')) {

        var handler = new PhotosPageHandler();

    };

});