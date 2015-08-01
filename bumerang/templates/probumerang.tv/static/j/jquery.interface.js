var ie = jQuery.browser.msie,
ieV = jQuery.browser.version,
ie6 = ie&&(ieV == 6),
ltie7 = ie&&(ieV <= 7),
ltie8 = ie&&(ieV <= 8);

function setPie(selectors){
	jQuery(selectors).css("behavior", "url(j/PIE.htc)")
};

function unsetPie(selectors){
	jQuery(selectors).css("behavior", "none")
};

function resetPie(selectors){
	unsetPie(selectors);
	setPie(selectors);
};

var cropText = function(txtElement, container_to_fit, widthLimit){
	var txt = txtElement.get(0).innerHTML;
	var i=0;

	if(container_to_fit.width() > widthLimit){
		while (container_to_fit.width() > widthLimit){
			txt = txt.substr(0,txt.length - 1)
			txtElement.html(txt+'...');
			i++;
			if (i > 100) {
				break;
			}
		}
	}
	
	if(txtElement.width() > 0){
		container_to_fit.get(0).style.width = widthLimit + 'px';
	}
}

function getPopup(link, popId) {
	var pop = $("#" + popId);
	var lnk = $(link);
	var close = pop.find('.b-popup__close');
	
	if (lnk.hasClass("act")) {
		lnk.removeClass("act");
		$('#tint').hide();
		pop.hide();
		removeEvent(document, "click", popClickFunc)
	}
	else {
		if (popBlock != null && popLnk != null) {
			$(popBlock).hide();
			$(popLnk).removeClass("act");
			removeEvent(document, "click", popClickFunc);
		}
		lnk.addClass("act");
		$('#tint').show();
		pop.css('margin-left', - pop.width() / 2 + 'px');
		pop.css("top", (($(window).height() - pop.outerHeight()) / 2) + $(window).scrollTop() + "px");
		pop.show();
		popLnk = link;
		popBlock = pop.get(0);
		popClose = close.get(0);
		addEvent(document, 'click', popClickFunc);
	}

	return false;
}

var popLnk, popBlock, popClose;
function popClickFunc(event) {
	var event = event || window.event;
	var t = event.target || event.srcElement;

	if (t != popLnk && !isChildNode(popLnk, t) && (t == popClose || isChildNode(popClose, t) || !isChildNode(popBlock, t))) {
		$(popBlock).hide();
		$('#tint').hide();
		$('#tint').removeClass('l-tint_popup');
		$(popLnk).removeClass("act");
		removeEvent(document, "click", popClickFunc);
	}

	return false;
}

function addEvent(obj, type, fn) {
	if (obj.addEventListener)
		obj.addEventListener(type, fn, false);
	else if (obj.attachEvent)
		obj.attachEvent( "on"+type, fn );
}

function removeEvent(obj, type, fn) {
	if (obj.removeEventListener)
		obj.removeEventListener(type, fn, false);
	else if (obj.detachEvent)
		obj.detachEvent( "on"+type, fn );
}

function isChildNode(elem, sell) {
	for (var childItem in elem.childNodes) {
		if (elem.childNodes[childItem].nodeType == 1) {
			if (elem.childNodes[childItem] == sell)
				return true;
			else if (isChildNode(elem.childNodes[childItem], sell))
				return true;
		}
	}
	return false;
}

$(document).ready(function(){
	$('body').addClass('has-js');

	/* Button prev */
	$('.b-button-prev').bind('mousedown', function () {
		$(this).addClass('active');
	});
	$('.b-button-prev').bind('mouseup', function () {
		$(this).removeClass('active');
	});
	
	
	/* Custom Input */
    /* TODO: this raise error on edit video page */
	//$('input').not('.b-sort__helper').customInput();

	
	/* Popup */
	$('.popup-handle').bind('click', function(){
		getPopup($(this), $(this).attr('rel'))
		
		return false;
	})
	
	
	/* Button */
	// $('.b-button')
	$('.b-button-prev')
	.add('.b-button-file')
	.add('.b-vote__like')
	.add('.b-vote__notlike')
		.not('.disabled')
		.bind('click', function(){
			$(this).blur();
//			return false
		});

    $('.b-button')
        .not('.disabled')
        .bind('click', function(){
            $(this).blur();
//			return false
        });

	
	/* Gradient text */
	$('#now-brief').gradientText({colors: ['#666', '#999', '#ccc']});

	
	/* Tabs */	
//	$('.b-tabs dl > dt').bind('click', function(){
//		$(this)
//			.siblings().removeClass('selected').end()
//			.next('dd').andSelf().addClass('selected');
//	})
	

	/* Cusel */
	var params = {
		changedEl:".b-form__field .f-select select",
		visRows:50,
		scrollArrows:false
	}
	try {
		cuSel(params);
	}
	catch(err){
	}

	$('.cusel').bind('click', function(){
		$('.cuselOpen').not($(this)).removeClass('cuselOpen');
	})

	/* Toggle */
	function Toggle(lnk, block, text, ico, params) {

		var defaultParams = {
			text: ['Скрыть', 'Показать'],
			icoClass: ['b-ico_x','b-ico_text']
		}
		
		var params = params || {};
		
		var text1 = (params.text != null && params.text[0]) ? params.text[0] : defaultParams.text[0];
		var text2 = (params.text != null && params.text[1]) ? params.text[1] : defaultParams.text[1];

		var icoClass1 = (params.icoClass != null && params.icoClass[0]) ? params.icoClass[0] : defaultParams.icoClass[0];
		var icoClass2 = (params.icoClass != null && params.icoClass[1]) ? params.icoClass[1] : defaultParams.icoClass[1];
		
		lnk.bind('click', function(){
			if (block.is(':hidden')) {
				block.slideDown('fast', function(){
					text.empty().text(text1);
					ico.toggleClass(icoClass2).toggleClass(icoClass1);
				});
				return false;
			} else {
				block.slideUp('fast', function(){
					text.empty().text(text2);
					ico.toggleClass(icoClass1).toggleClass(icoClass2);
				});
				return false;
			}
		})
	}

	$('.js-toggle').each(function(){
		var lnk = $(this).find('.b-pseudolink');
		var block = $(this).next('div');
		var text = lnk.find('.js-toggle-text');

		Toggle(lnk, block, text);
	})
	
	$('.js-toggle2-container').each(function(){
		var lnk = $(this).find('.js-toggle2-lnk');
		var block = $(this).find('.js-toggle2-block');
		var text = $(this).find('.js-toggle2-text');
		var ico = $(this).find('.js-toggle2-ico');
		
		if ($(this).hasClass('js-toggle2-container_resume')) {
			Toggle(lnk, block, text, ico, {text:['↑ Скрыть', '↓ Показать']});
		} else if ($(this).hasClass('js-toggle2-container_tv')) {
			Toggle(lnk, block, text, ico, {text:['Скрыть программу передач', 'Программа передач']});
		} else {
			Toggle(lnk, block, text, ico);
		}
	})
	
	/* Change text */
	$('.js-changable').each(function(){
		var ctrl = $(this).find('.js-ctrl');
		var text = $(this).find('.js-text');
		var currentField = $(this).parents('.b-form__field');
		var nextField = currentField.next('.b-form__field');
		var input = nextField.find('.js-input');
		
		ctrl.bind('click', function(){
			currentField.hide();
			nextField.show();
			input.focus().select();
		})
	})
	
	
	/* Advertising */
	$('.b-adv__close').bind('click', function(){
		$(this).parents('.b-adv').hide();
	})
	
	
	/* Dropdown */
	$('.b-dropdown__handle').bind('click', function(){
		$(this).parents('.b-dropdown').toggleClass('b-dropdown_open');
		return false;
	})
	
	$('.b-gallery_ui .b-gallery__item, .b-announs_movie_ui .announ-item').hover(function(){}, function(){
		$(this).find('.b-dropdown_open').removeClass('b-dropdown_open');
	})
	
	$('.b-gallery_ui .b-gallery__item, .b-announs_movie_ui .announ-item').each(function(){
		var item = $(this);
		var checkbox = item.find('.ui-checkbox input[type=checkbox]');
		checkbox.bind('click', function(){
			if ($(this).is(':checked')) {
				item.addClass('checked');
			} else {
				item.removeClass('checked');
			}
		})
	})


	/* Double hover */
	doubleHover = function() {
		$("a.js-double-hover").live("mouseover", function() {
			$("a[href='" + $(this).attr("href") + "']").addClass("pseudo-hover");
		});
		$("a.js-double-hover").live("mouseout", function() {
			$("a").removeClass("pseudo-hover");
		});
	}
	doubleHover();
	
	/* Textarea */
	try {
		$('textarea').css('overflow', 'hidden');
		$('textarea').autogrow();
	} catch(e) {}
	
	$('#dropdown2').each(function(){
		var container = $(this);
		var button = container.find('.b-dropdown2__button');
		var ava = container.find('.b-ava');
		var list = container.find('.b-dropdown2__list');
		var popup = jQuery('<div class="b-dropdown2__popup">');
		var avaClone = ava.clone();
		var listClone = list.clone();
		
		listClone.addClass('b-dropdown2__list_clone');
		avaClone.addClass('b-ava_clone');
		
		button.bind('click', function(){
			if (!popup.parent(container).length) {
				popup.appendTo(container);
			}

			if (!avaClone.parent(container).length) {
				avaClone.appendTo(container);
			}

			if (!listClone.parent(container).length) {
				listClone.appendTo(container);
			}
			
			container.toggleClass('b-dropdown2_open');
			if (container.hasClass('b-dropdown2_open')) {
				ava.appendTo(popup);
				list.appendTo(popup);
				popup.show();
				avaClone.show();
				listClone.show();
			} else {
				list.prependTo(container);
				ava.prependTo(container);
				popup.hide();
				listClone.hide();
				avaClone.hide();
			}
		})
	})
});
