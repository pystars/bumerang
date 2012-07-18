"use strict";
/*
Photos handler
 */
function photosHandler() {
    /*
    Private object's data
     */
    var selected_items = new Array();



    this.init = function() {
        makePhotosCountText();
    };

    /*
    Private object's methods
     */
    var getPhotosCount = function() {
        return toi($('form .photo:visible').length);
    };

    var makePhotosCountText = function() {
        var text = new String();
        var plurals = $('#photos-plurals').text();
        var count = getPhotosCount();

        if (count) {
            //text = 'Всего ' + count + ' ' + ru_pluralize(count, plurals);
            _log('Всего {0} {1}'.format(count, ru_pluralize(count, plurals)));
        } else {
            text = 'Нет ни одной фотографии';
        }

        return text;
    };

    this.showPhotosCount = function() {
        var count = getPhotosCount();
        _log(count);
        if (count != 0) {
            $('#photos-count').text('Всего ' + count + ' ' + ru_pluralize(count, $('#photos-plurals').text()));
        } else {
            $('#photos-count').text('Нет ни одной фотографии');
        };


    };

    this.init();

}


$(function() {

    if ($('#photoalbums-container')) {

        var handler = new photosHandler();



    };

});