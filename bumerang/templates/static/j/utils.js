'use strict';

document.__DEBUG = true;

/*
 * String formatting like python format()
 * */
(function(st) {
    function fl(s, len) {
        var len = Number(len);
        if (isNaN(len)) return s;
        s = ''+s;
        var nl = Math.abs(len)-s.length;
        if (nl<=0) return s;
        while (sp.length<nl) sp += sp;
        return len<0?(s+sp.substring(0, nl)):(sp.substring(0, nl)+s);
    }
    st.format = function() {
        if (arguments.length==0) return this;
        var placeholder = /\{(\d+)(?:,([-+]?\d+))?(?:\:([^(^}]+)(?:\(((?:\\\)|[^)])+)\)){0,1}){0,1}\}/g;
        var args = arguments;
        return this.replace(placeholder, function(m, num, len) {
            var m = args[Number(num)];
            return fl(m, len);
        });
    };
}(String.prototype));

/*
 * Global utils
 * */
(function() {
    // Debug console
    window._log = function() {
        if (document.__DEBUG) {
            return console.info(arguments);
        } else {
            return function() {};
        }
    };
    // Argument to integer, in decimal number system
    window.toi = function(value) {
        return parseInt(value, 10);
    };

}());

/*
 * Notifications
 * */
var CONST_NF_DELAY_TIME = 10 * 1000;
var NF_SUCCESS = { class: 'success' };
var NF_ERROR = { class: 'error' };

function showNotify(status, text) {
    var delayTime = CONST_NF_DELAY_TIME || 12 * 1000;
    var tpl = '<div class="alert-message {0}">'.format(status.class);
    tpl += '<a class="close msg-close" href="#">×</a>';
    tpl += '<p> {0} </p></div>'.format(text);

    var nfc = $(tpl);
    $('.l-page__i').prepend(nfc);
    nfc.css({
        'width': ($(window).width() - nfc.outerHeight())
    });
    nfc.on('click', '.msg-close', function() {
        $(this).parent().hide();
    });
    $('.msg-close').click(function(e) {
        e.preventDefault();
        $(this).parent().hide();
    });
    $('.alert-message').delay(delayTime).hide(300);
}
