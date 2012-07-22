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
var PhotosPageHandler = function() {
    /*
     * Private object's data
     * */
    var root = this;

    var _delegateEventSplitter = /^(\S+)\s*(.*)$/;
    var events_handlers = {};
    var confirm_dialog_selector = '#popup-confirm';
    var items_list = [];

    var events = {
        'click a[id*=photo-del-]': 'clickSinglePhotoDelete',
        'click article[id*=photo-item-]': 'clickPhotoCheckbox'
    };

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

    var cleanItems = function() {
        items_list = [];
    };


    var init = function() {

//        delegateEvents(events);

        _log(this);

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
        var list = items_list.getList();

        _.each(list, function(id) {
            var el = $('#photo-item-{0}'.format(id));

            el.hide(function() {
                el.remove();
                updatePage();
            });
        });
    };

    var updatePage = function() {
        var list = getItems();

        if (list.length) {
            showDeleteButton();
        } else {
            hideDeleteButton();
        }

        showPhotosCount();
    };

//    var sendItemsDeleteRequest = function() {
//        $.post('/photo/photos-delete1/', {
//            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
//            ids: JSON.stringify(selected_items.getList())
//        })
//        .success(function(response) {
//            Notify(NF_SUCCESS, response['message']);
//            hideItems();
//            showPhotosCount();
//            selected_items = [];
//            updatePage();
//        })
//        .error(function() {
//            var msg = 'Произошла ошибка';
//            Notify(NF_ERROR, msg);
//        });
//    };

    /*
     * Events handlers functions
     */

    events_handlers = {

        clickPhotoCheckbox: function(e) {
            var el = $(e.target || e.srcElement);
            var id = toi(el.attr('data-photo-id'));

            if (el.is(':checked')) {
                addItem(id);
            } else {
                removeItem(id);
            }

            updatePage();
        },

        clickSinglePhotoDelete: function(e) {
            e.preventDefault();
            var el = $(e.target || e.srcElement);
            var id = el.attr('data-photo-id');

            var msg = 'Вы действительно хотите удалить выбранную фотографию?';
            var decision = confirmModalDialog(confirm_dialog_selector, msg);

            addItem(id);
            _ln('b', getItems());

            decision.done(function() {
                _ln('dcs', getItems());
//                sendItemsDeleteRequest();
            });

//            decision.fail(function() {
//                Notify(NF_ERROR, 'cancelled');
//            });
        }

    };

    /*
     * Init Handler object
     * */
    init();

};


(function($) {
    $.fn.lol = function(options) {

        var settings = $.extend( {
            'delete': ''
        }, options);

        this.each(function() {
            _log(settings.delete);
        });
    };
})(jQuery);


$(function() {

    if ($('#photoalbums-container')) {

        $('#photos-container').lol({ delete: 'photo' });

//        var handler = new PhotosPageHandler();

    }

});