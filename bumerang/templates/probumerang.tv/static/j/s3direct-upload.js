/**
 * Created by goodfellow on 4/1/15.
 */
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
        progressBar($(el).nextAll('.progress-bar'), data, showProgress)
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
    if ($(el).next('.progress-value').size()) {
      $(el).next('.progress-value').html(pcnt + '%');
    }
};
var error = function(el, msg) {
    $(el).value = '';
    alert(msg);
//    $('#popup-upload').hide();
//    $('#tint').hide();
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
    var submitRow = document.querySelector('.submit-row'), buttons;
    if(submitRow) {
      buttons = submitRow.querySelectorAll('input[type=submit]')

    } else {
      buttons = $('#video-upload-form button[type=submit]');
    }

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
