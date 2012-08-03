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

$(function() {
    $('#videoalbums-dropdown').dropdownList();
});


///////////////////////////
(function($) {
    var methods = {
        init: function() {
            return this.each(function() {
                var root = $(this);
                var albums_list, videos_list;
                var albums = {};

                var _classname = root.attr('class');
                var helper = $('#ajax-helper');
                var url = helper.attr('data-ajax-list-url');

                var videosDropDown = $('#videos-dropdown');

                var dropdownLink = root.find('a.dropdown-link');
                var videosDropdownLink = videosDropDown.find('a.dropdown-link');
                var itemsList = root.find('ul.items-list');
                var videositemsList = videosDropDown.find('ul.items-list');
                var ddLinkContent = dropdownLink.find('.content');
                var vddLinkContent = videosDropDown.find('.content');
                var ddLinkLoader = ddLinkContent.find('.ldr');
                var vddLinkLoader = videosDropDown.find('.ldr');

                var parseAlbums = function(list) {
                    var albums_list = {};
                    for (var key in list) {
                        var item = list[key];
                        albums_list[item['id']] = item;
                        delete albums_list[item['id']]['id'];
                    }
                    return albums_list;
                };

                var showLoader = function(text) {
                    ddLinkLoader.show();
                    ddLinkContent.find('text').text(text);

                    var dfd = $.Deferred();

                    dfd.done(function() {
                        ddLinkLoader.hide();
                    });

                    return dfd;
                };

                var loadData = function(type) {
                    return $.getJSON(url, { type: type });
                };

                var renderItem = function(data) {
                    var item = $('.item.template').clone()
                        .removeClass('template').show();
                    if (data['src']) {
                        item.find('.preview').attr('src', data['src']);
                    }
                    item.find('.text').text(data['text']);

                    item.attr('data-item_id', data['id']);

                    return item;
                };

                var renderAlbums = function(list) {
                    var context = [],
                        listEl = $('<ul>').addClass('items-list').show();

                    context.push({
                        id: 'no-album',
                        text: 'Видеозаписи вне альбомов'
                    });
                    for (var album_id in list) {
                        (function(a) {
                            context.push({
                                id: album_id,
                                src: a.cover,
                                text: a.title
                            });
                        })(list[album_id]);
                    }
                    for (var key in context) {
                        listEl.append(renderItem(context[key]));
                    }
                    return listEl;
                };

                var renderVideos = function(list) {
                    var context = [],
                        listEl = $('<ul>').addClass('items-list').show();
                    for (var album_id in list) {
                        (function(a) {
                            context.push({
                                id: album_id,
                                src: a.cover,
                                text: a.title
                            });
                        })(list[album_id]);
                    }
                    for (var key in context) {
                        listEl.append(renderItem(context[key]));
                    }
                    return listEl;
                };

                var replaceList = function(list) {
                    itemsList.replaceWith(list);
                    itemsList = root.find('ul.items-list');
                };

                var videoReplaceList = function(list) {
                    videositemsList.replaceWith(list);
                    videositemsList = videosDropDown.find('ul.items-list');
                };

                var show_albums_list = function(list) {
                    var albums = parseAlbums(list);
                    var rendered = renderAlbums(albums);
                    replaceList(rendered);
                    itemsList.show();
                };

                var show_videos_list = function(list) {
                    var videos = parseAlbums(list);
                    var rendered = renderVideos(videos);
                    videoReplaceList(rendered);
                    videositemsList.show();
                };

                dropdownLink.on('click', function(e) {
                    e.preventDefault();

                    if (albums_list) {
                        show_albums_list(albums_list);
                    } else {
                        var ldr_anim = showLoader('Загружаются альбомы');
                        var req = loadData('albums');
                        req.success(function(res) {
                            albums_list = res['albums_list'];
                            show_albums_list(albums_list);
                        });
                        req.complete(function() {
                            ldr_anim.resolve();
                        });
                    }
                });

                var replaceMain = function(item) {
                    var id = item.parents('li.item').attr('data-item_id');
                    var src = item.find('.preview').attr('src');
                    var text = item.find('.text').text();

                    ddLinkContent.parents('li.item').attr('data-item_id', id);
                    ddLinkContent.find('.preview').attr('src', src);
                    ddLinkContent.find('.text').text(text);
                };

                $(document).on('click', 'a.list-item-link', function(e) {
                    e.preventDefault();
                    var item = $(this);
                    var id = item.parents('li.item').attr('data-item_id');

                    if (id == 'no-album') {
                        var ldr_anim = showLoader('Загрузка списка видео');
                        var req = loadData('videos_with_no_album');
                        req.success(function(res) {
                            videos_list = res['videos_list'];
                            show_videos_list(videos_list);
                        });
                        req.complete(function() {
                            ldr_anim.resolve();
                        });
                    }

                    replaceMain(item);
                    itemsList.hide();

                });

                $(document).on('click', function(e) {
                    var targetEl = $(e.target);
                    if (!targetEl.parents().hasClass(_classname)) {
                        itemsList.hide();
                    }
                });
            });
        }
    };

    $.fn.dropdownList1 = function(method) {
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || ! method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' +  method + ' does not exist on jQuery.tooltip');
        }
    };
})(jQuery);
