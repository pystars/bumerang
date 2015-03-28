document.__DEBUG = true;

/*
 * Helper functions
 * */
// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
 (function(st) {

    function fl(s, len) {
        var len = Number(len);
        if(isNaN(len)) return s;
        s = ''+s;
        var nl = Math.abs(len)-s.length;
        if (nl<=0) return s;
        while (sp.length<nl) sp += sp;
        return len<0?(s+sp.substring(0, nl)):(sp.substring(0, nl)+s);
    }

    function pp(params, args) {
        var r;
        for(var i=0; i<params.length; i++)
        {
            if( (r = paramph.exec(params[i])) != null )
                params[i] = args[Number(r[1])];
            else
                params[i] = params[i].replace(/\0/g, ',');
        }
        return params;
    }

    st.format = function() {
        if(arguments.length==0) return this;
        var placeholder = /\{(\d+)(?:,([-+]?\d+))?(?:\:([^(^}]+)(?:\(((?:\\\)|[^)])+)\)){0,1}){0,1}\}/g;
        var args = arguments;

        var result = this.replace(placeholder, function(m, num, len) {
            var m = args[Number(num)];
            return fl(m, len);
        });

        return result;
    };

}(String.prototype));

(function(window) {
    var scp = this;
    /*
     * Debug console
     * */
    this._ln = function() {
        if (document.__DEBUG) {
            console.info(arguments);
        } else {
            return function() {};
        }
    };

    this._log = function() {
        if (document.__DEBUG) {
            console.info('| [DEBUG OUTPUT]\t [NUM]\t [TYPE]\t\t\t\t [VALUE]');
            for (var i in arguments) {
                var arg = arguments[i];
                console.info('|\t\t\t', (toi(i)+1), '\t', typeof(arg), '\t\t\t', arg, '\n');
            }
        } else {
            return function() {};
        }
    };

    /*
     * Argument to integer, in decimal number system
     * */
    this.toi = function(value) {
        return parseInt(value, 10);
    };

}(window));

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

/*
 * Notifications
 * */
var NF_SUCCESS = {
        class: 'success'
    },
    NF_ERROR = {
        class: 'error'
    };

function Notify(status, text) {

    var tpl = '<div class="alert-message {0}">'.format(status['class']);
    tpl += '<a class="close msg-close" href="#">×</a>';
    tpl += '<p> {0} </p></div>'.format(text);

    var nfc = $(tpl);

    $('.l-page__i').prepend(nfc);

    nfc.css({
        'width': ($(window).width() - nfc.outerHeight())
    });

    nfc.on('click', '.msg-close', function(e) {
        e.preventDefault();
        $(this).parent().hide();
    });

    $('.alert-message').delay(delay_time).hide(300);

}

/*
 * Constants
 * */
allowed_photos_extensions_regexp = /.+\.(bmp|jpe|jpg|jpeg|tif|gif|tiff|png)$/i;
allowed_videos_extensions_regexp =
    /.+\.(avi|mkv|vob|mp4|ogv|ogg|m4v|m2ts|mts|m2t|wmv|ogm|mov|qt|mpg|mpeg|mp4v)$/i;
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

function invokeConfirmDialog(text, callback, scope) {
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

    var cb = function(scope) {
        return callback(scope);
    }

    okButton.bind('click', {s1: scope}, function(e) {
        //console.log(e.data.s1);
        e.preventDefault();
        cb();
        cancelButton.trigger('click');
    });

    popup.css('margin-left', - popup.width() / 2 + 'px');
    popup.css("top", (($(window).height() - popup.outerHeight()) / 2) + $(window).scrollTop() + "px");
    $('#tint').show();
    popup.show();
};

function invConfDlg(text) {

    var defer = $.Deferred();

    var popup = $('#popup-confirm-video');

    popup.find('*').unbind();

    var cancelButton = $('#' + popup.attr('id') + ' .confirm-popup-cancel');
    var okButton = $('#' + popup.attr('id') + ' .confirm-popup-ok');

    $('#' + popup.attr('id') + ' #dialog-text').text(text);

    var close_n_hide = function() {
        popup.hide();
        $('#tint').hide();
    }

    cancelButton.bind('click', function(e) {
        e.preventDefault();
        close_n_hide();

        defer.reject();
    });

    okButton.bind('click', function(e) {
        e.preventDefault();
        //cancelButton.trigger('click');
        close_n_hide();

        defer.resolve();
    });

    popup.css('margin-left', - popup.width() / 2 + 'px');
    popup.css("top", (($(window).height() - popup.outerHeight()) / 2) + $(window).scrollTop() + "px");
    $('#tint').show();
    popup.show();

    return defer;
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

var request = function(method, url, data, headers, el, showProgress, cb) {
    var req = new XMLHttpRequest();
    req.open(method, url, true);

    Object.keys(headers).forEach(function(key){
        req.setRequestHeader(key, headers[key])
    });

    req.onload = function() {
        cb(req.status, req.responseText)
    };

    req.onerror = req.onabort = function() {
        disableSubmit(false);
        error(el, 'Произошла ошибка во время загрузки  файла.')
    };

    req.upload.onprogress = function(data) {
      if ($(el).find('.progress-bar').size()) {
        progressBar($(el).find('.progress-bar'), data, showProgress)
      } else {
        progressBar($('.progress-bar'), data, showProgress)
      }
    };

    req.send(data)
};
var progressBar = function(el, data, showProgress) {
    if(data.lengthComputable === false || showProgress === false) return;

    var pcnt = Math.round(data.loaded * 100 / data.total);

    $(el).val(pcnt);
    $(el).next('.progress-value').html(pcnt + '%');
};
var error = function(el, msg) {
    $(el).value = '';
    alert(msg);
    $('#popup-upload').hide();
    $('#tint').hide();
};
var update = function(el, xml) {
//    var link = el.querySelector('.file-link'),
//        url  = el.querySelector('.file-url')

//    url.value = parseURL(xml);
//    link.setAttribute('href', url.value)
//    link.innerHTML = url.value.split('/').pop()

//    el.className = 's3direct link-active'
  if ($(el).find('.progress-bar').size()) {
    $(el).find('.progress-bar').val(0);
  } else {
    $('.progress-bar').val(0);
  };
  $(el).value = '';
  $('#popup-upload').hide();
  $('#tint').hide();
  $('<span>Файл успешно загружен</span>').insertAfter(el);
  $(el).prev('button').text('Загрузить другой файл с компьютера');
};

var parseJson = function(json) {
    var data;
    try {data = JSON.parse(json)}
    catch(e){ data = null }
    return data
};

var parseURL = function(text) {
    var xml = new DOMParser().parseFromString(text, 'text/xml'),
        tag = xml.getElementsByTagName('Location')[0];
    return decodeURI(tag.childNodes[0].nodeValue);  // return url
};

var concurrentUploads = 0;
var disableSubmit = function(status) {
//    var submitRow = document.querySelector('.submit-row')
//    if( ! submitRow) return

//    var buttons = submitRow.querySelectorAll('input[type=submit]')
    var buttons = $('#video-upload-form button[type=submit]');

    if (status === true) concurrentUploads++
    else concurrentUploads--;

    $.each(buttons, function(el){
        el.disabled = (concurrentUploads !== 0)
    });
};

var upload = function(file, data, el) {
    var form = new FormData();

    disableSubmit(true);

    if (data === null) return error(el, 'Sorry, could not get upload URL.');

//    el.className = 's3direct progress-active';
    var url  = data['form_action'];
    delete data['form_action'];

    Object.keys(data).forEach(function(key){
        form.append(key, data[key])
    });
    form.append('file', file);

    request('POST', url, form, {}, el, true, function(status, xml){
        disableSubmit(false);
        if(status !== 201) return error(el, 'К сожалению произошла ошибка при загрузке видео на сервер.');
        update(el, xml);
//        console.log(status);
//        console.log(xml);
    })
};

var removeUpload = function(e) {
    e.preventDefault()
    $('#popup-upload').hide();
    $('#tint').hide();

//    var el = e.target.parentElement
//    el.querySelector('.file-url').value = ''
//    el.querySelector('.file-input').value = ''
//    el.className = 's3direct form-active'
};

/*
* Site handlers
* */
$(function() {
    $('.input-file-button').on('click', function(){
      $(this).next('input[type=file]').click();
    });
    $('#video-selector').on('change', function (evt/**Event*/){
        // Retrieve file list
        var file = FileAPI.getFiles(evt)[0];
        if (file.type.startsWith('video')) {
          var el = evt.target;
          var url = $(this).attr('data-policy-url');
          var form = new FormData();
          form.append('content_type', file.type);
          form.append('filename', file.name);
          var headers = {'X-CSRFToken': getCookie('csrftoken')};
          request('post', url, form, headers, el, false, function(status, json) {
            var data = parseJson(json);
            switch(status) {
                case 200:
                    $(el).next('span').remove();
                    invokeUploadMessage();
                    upload(file, data, el);
                    break;
                case 400:
                    error(el, data);
                case 403:
                    error(el, data.error);
                    break;
                default:
                    error(el, 'Sorry, could not get upload URL.')
            }
          });
        } else {
            $('#popup-upload').hide();
            $('#tint').hide();
            show_notification('error',
                'Неверный формат видеофайла'
            );
            return false;
        }

    });

    _.templateSettings = {
        interpolate : /\{=(.+?)\}/g
    };
    /*
    Datetime picker
     */

    if ($.fn.datepicker) {
        $('#datepicker_birthday').datepicker({
            maxDate: new Date(),
            changeMonth: true,
            changeYear: true,
            yearRange: "-100:-16"

        }).datepicker({ showOn: 'both' });

        var dp_ids = '#datepicker_start_date,' +
            '#datepicker_end_date,#datepicker_accept_requests_date,' +
            '#id_start_date,#id_end_date,#id_requesting_till';

        $(dp_ids).datepicker({
            minDate: new Date(),
            changeMonth: true,
            changeYear: true

        }).datepicker({ showOn: 'both' });
    }

    $('a.scroll-to-top').click(function(e) {
        $("html, body").animate({scrollTop:0},"fast");
        e.preventDefault();
    });


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

    // Logo
    $('#id_logo[type=file]').change(function(event){
        $('form[name=logo_form]').submit();
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

    $(window).bind('hashchange', function(e) {
        var hash = location.hash.replace('#','');
        if(hash == '') $(window).scrollTop(window.lastPosition);
    });

    $("a.cal-day").click(function(){
        window.open($(this).attr('href'), 'popUpWindow', 'height=700,width=980,left=10,top=10,resizable=yes,scrollbars=yes,toolbar=no,menubar=no,location=yes,directories=no,status=yes');
        return false;
    });

    $('.clean-modal a.close').click(function(e) {
        e.preventDefault();
        $(this).parents('.clean-modal').hide();
        $('#tint').hide();
        $('body').css('overflow', 'auto');
    });
});
