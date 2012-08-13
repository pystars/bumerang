'use strict';

document.__DEBUG = true;

var festivalDetailPageSelector = '.hdr-festival-detail',
    festivalRequestPageSelector = '.hdr-festival-send-request';

$(function() {
    /*
     Festival detail page handler
     */
    if ($(festivalDetailPageSelector)) {
        /* Tabs handler */
        $('div.tabs a.b-button').on('click', function(e) {
//            e.preventDefault();
            window.location.hash = this.hash;
            var el = $(e.target);
            $('div.tabs a.b-button').removeClass('current');
            el.addClass('current').removeClass('hidden');

            $('.tab-block section').addClass('hidden');
            var tab_section = $('.tab-block section[id='+el.attr('href').replace('#', '')+']');

            tab_section.addClass('current')
                .removeClass('hidden')
                .find('.b-form').removeClass('hidden');
        });
        $('.tab-block section:not(.current)').addClass('hidden');
        $('div.tabs a.b-button[href='+location.hash+']').trigger('click');

    } /* end festival page handler */


    if ($(festivalRequestPageSelector)) {
        /*
         * Festival request fill page handler
         */
        var helper = $('#ajax-helper');
        var url = helper.attr('data-ajax-list-url');

    } /* end festival request handler */

    if ($('#event-send-request-form')) {
        var form = $('#event-send-request-form');
        var checked = parseInt(form.find('input[name=type]:checked').val());

        if (checked == 1) {
            form.find('#parent-fest-selector').removeClass('hidden');
        } else if (checked == 2) {
            form.find('#parent-fest-selector').addClass('hidden');
        }

        form.on('click', 'input[name=type]', function(e) {
            var type = parseInt($(this).val(), 10);

            if (type == 1) {
                form.find('#parent-fest-selector').removeClass('hidden');
            } else if (type == 2) {
                form.find('#parent-fest-selector').addClass('hidden');
            }
        });
    }

});

/*
    Star ratings handler
 */
(function($) {
    $.fn.starRating = function() {
        return this.each(function() {
            var $this = $(this);

            function setNewRateStars(count) {
                var count = parseInt(count, 10);
                $this.find('a').each(function(i, e) {
                    (function(el) {
                        console.log('data-rate', el.attr('data-rate'));
                        if (el.attr('data-rate') <= count) {
                            el.addClass('active');
                        } else {
                            el.removeClass('active');
                        }
                    }($(this)));
                });
            }

            var total_num = $this.attr('data-total-rate');
            setNewRateStars(total_num);

            $this.find('a').hover(function(e) {
                    var star_num = parseInt($(this).attr('data-rate'));
                    $this.find('a').each(function(i, e) {
                        var el = $(this);
                        var el_num = el.attr('data-rate');
                        if (el_num < star_num) {
                            el.addClass('active');
                        } else {
                            el.removeClass('active');
                        }
                    });
                }, function(e) {
                    var star_num = parseInt($this.attr('data-total-rate'));
                    $this.find('a').each(function(i, e) {
                        var el = $(e);
                        var el_num = el.attr('data-rate');
                        if (el_num <= star_num) {
                            el.addClass('active');
                        } else {
                            el.removeClass('active');
                        }
                    });
                });

                $this.find('a').on('click', function(e){
                    e.preventDefault();
                    var item_id = $this.attr('data-item-id');
                    var rate = $(this).attr('data-rate');

                    $this.attr('data-total-rate', rate);

                    $.ajax({
                        type: 'POST',
                        url: '/events/participant-video'+item_id+'/'+rate+'/',
                        data: {
                            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                            result: 1
                        },
                        success: function(response) {
                            setNewRateStars(response.current);
                            $('#video-'+response.object_id+'-score').text(
                                response.average
                            );
                            $('#your-'+response.object_id+'-score').text(
                                response.current
                            );
                            Notify(NF_SUCCESS, 'Оценка поставлена')
                        }
                    });
                });
            });

    };
})(jQuery);

$(function() {
    $('.star-rate').starRating();

    $(document).on('click', 'a.make-winner', function(e) {
        e.preventDefault();
        var nomination_id = $(this).attr('data-nomination-id');
        var participant_video_id = $(this).attr('data-participant-video-id')

        $.post('/events/nomination'+nomination_id+'/'+participant_video_id+'/', {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
        }).success(function(response) {
            if (response.success) {
                Notify(NF_SUCCESS, 'Победитель выбран');
            } else {
                Notify(NF_ERROR, 'Произошла ошибка');
            }
        });
    });
});





(function($) {
    var methods = {
        init: function() {
            return this.each(function() {
                var root = $(this);

                var list_objects = {};
                var items_list = {};
                var current_album, current_video;

                var loadData = function(type) {
                    var url = $('#ajax-helper').attr('data-ajax-list-url');
                    return $.getJSON(url, { type: type });
                };

                var rootType = function(type) {
                    return root.find('dl[id='+type+']');
                };

                var showLoader = function(type, text) {
                    var loader = rootType(type).find('.ldr').show();
                    rootType(type).find('.text').text(text);
                    var dfd = $.Deferred();
                    dfd.done(function() {
                        loader.hide();
                    });
                    return dfd;
                };

                var renderItem = function(data) {
                    var item = $('.item.template').clone()
                        .removeClass('template').show();
                    if (data['img']) {
                        item.find('.preview').attr('src', data['img']);
                    }
                    item.find('.text').text(data['text']);

                    item.attr('data-item_id', data['id']);

                    return item;
                };

                var renderItems = function(type, list) {
                    var context = [];
                    var listEl = $('<ul>').addClass('items-list').show();
                    if (type == 'albums') {
                        context.push({
                            id: 'no-album',
                            text: 'Видеозаписи вне альбомов'
                        });
                    }
                    for (var item_id in list) {
                        (function(a) {
                            context.push({
                                id: a.id,
                                src: a.cover,
                                text: a.title
                            });
                        })(list[item_id]);
                    }
                    for (var key in context) {
                        listEl.append(renderItem(context[key]));
                    }
                    return listEl;
                };

                var replaceItemsList = function(type, list) {
                    rootType(type).find('ul.items-list').replaceWith(list);
                    items_list[type] = rootType(type).find('ul.items-list');
                };

                var showItemsList = function(type, list) {
//                    var items = parseAlbums(list);
                    var rendered = renderItems(type, list);
                    replaceItemsList(type, rendered);
                    items_list[type].show();
                };

                var setMain = function(type, data){
                    rootType(type).parents('li.item').attr('data-item_id', data['id']);
                    rootType(type).find('.preview').attr('src', data['src']);
                    rootType(type).find('.text').text(data['text']);
                };

                var replaceMain = function(type, item) {
                    var id = item.parents('li.item').attr('data-item_id');
                    var src = item.find('.preview').attr('src');
                    var text = item.find('.text').text();

                    rootType(type).parents('li.item').attr('data-item_id', id);
                    rootType(type).find('.preview').attr('src', src);
                    rootType(type).find('.text').text(text);
                };

                root.on('click', 'a.dropdown-link', function(e) {
                    e.preventDefault();
                    var item = $(this);
                    var type = $(e.target).parents('.droplist').attr('id');
                    var id = $(e.target).parents('li.item').attr('data-item_id');
                    console.log('type', type);
                    if (type == 'albums') {
                        if (list_objects[type]) {
                            showItemsList(type, list_objects[type]);
                        } else {
                            var loader_animation = showLoader(type, 'Загружается список альбомов');
                            var req = loadData('albums');
                            req.success(function(res) {
                                list_objects[type] = res['albums_list'];
                                showItemsList(type, list_objects[type]);

                            });
                            req.complete(function() {
                                loader_animation.resolve();
                            });
                        }
                    }
                    if (type == 'videos') {
                        var loader_animation = showLoader(type, 'Загрузка списка видео');
                        var req = loadData('videos');
                        req.success(function(res) {
                            var videos_list = res['videos_list'];
                            var lst = _.filter(videos_list, function(item) {
                                if (current_album == 'no-album') {
                                    if (!item['album']) return item;
                                } else {
                                    if (item['album'] == current_album) return item;
                                }
                            });
                            showItemsList(type, lst);
                        });
                        req.complete(function() {
                            loader_animation.resolve();
                        });
                    }
                });

                root.on('click', 'a.list-item-link', function(e) {
                    e.preventDefault();
                    var item = $(this);
                    var type = $(e.target).parents('.droplist').attr('id');
                    var id = item.parents('li.item').attr('data-item_id');
                    var oldItem = item.clone();

                    if (type == 'albums') {
                        current_album = id;
                        var loader_animation = showLoader(type, 'Загрузка списка видео');
                        var req = loadData('albums');
                        req.success(function(res) {
                            list_objects[type] = res['albums_list'];
                            replaceMain(type, oldItem);
                            showItemsList(type, list_objects[type]);
                            items_list[type].hide();

                            var text;
                            if (current_album == 'no-album') {
                                text = 'Видео вне альбомов';
                            } else {
                                var curr_album = _.filter(list_objects[type], function(item){
                                    if (item.album == current_album) return item;
                                });
                                text = 'Видео из альбома {0}'.format(curr_album.title);
                            }

                            setMain('videos', {
                                text: text
                            });

                            root.find('.droplist[id=videos]').show();
                        });
                        req.complete(function() {
                            loader_animation.resolve();
                        });
                    }
                    if (type == 'videos') {
                        current_video = id;
                        replaceMain(type, item);
                        items_list[type].hide();
                    }
                });

                $(document).on('click', function(e) {
                    var targetEl = $(e.target);
                    if (!targetEl.parents().hasClass('dropdown')) {
                        root.find('ul.items-list').hide();
                    }
                });
            })
        }
    };

    $.fn.dropdownList = function(method) {
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || ! method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' +  method + ' does not exist on jQuery.tooltip');
        }
    };
})(jQuery);

