(function($) {
    $.fullWall = function(el, options) {
        var options = $.extend($.fullWall.defaultOptions, options);
        el.data('fullWall', this);
        
        var wall_container = "#wall-container";
        var wall_container_w;
        var wall_container_h;

        var wall_loading = "#wall-loading";

        var wall_detail = "#wall-detail";
        var wall_detail_image_container = '.wall-detail-image';
        var wall_detail_controls_container = '.wall-detail-controls';
        var wall_detail_info = '.wall-detail-info';

        var wall = "#wall";
        var wall_rows;

        var wall_items = ".wall-item";
        var wall_items_count = $(wall_items).length;
        var wall_items_for_row = options.itemsForRow;
        
        var x = 0;
        
        this.setWallDimensions = function(resizing) {
            /** get wall width & height **/
            wall_container_w = parseInt( $(window).width() );
            wall_container_h = parseInt( $(window).height() );
            /** set wall dimensions **/
            $(wall).css({ width : wall_container_w, height : wall_container_h });

            /** calculate wall rows **/
            wall_rows = parseInt(wall_items_count/wall_items_for_row)+1;
            if(wall_items_count % wall_items_for_row == 0) { wall_rows = wall_rows-1 }
            
            /** calculate wall items width **/
            wall_items_w = parseInt(wall_container_w/wall_items_for_row);
            
            /** calculate wall items height **/
            wall_items_h = parseInt(wall_container_h/wall_rows);

            /** if window resizing **/
            if (resizing) {
                $(wall_items).css({'width': wall_items_w, 'height' : wall_items_h});
                if($(wall_detail).is(':visible')){
                    this.setBgImage(0);
                }
            };
        };
        
        this.setBgImage = function(img, w, h) {
            if(img != 0){
                img_src = img;
                img_w = w;
                img_h = h;
            }
            
            var w_ratio = wall_container_w / img_w;
            var h_ratio = wall_container_h / img_h;
            
            var w_diff = h_ratio * img_w;
            var h_diff = w_ratio * img_h;
            
            var image;
            if(h_diff>wall_container_h) {
                image = '<img src="'+img_src+'" width="'+wall_container_w+'" height="'+h_diff+'" class="imgZoom" />';
                new_w = wall_container_w;
                new_h = h_diff;
            } 
            else
            {
                image = '<img src="'+img_src+'" width="'+w_diff+'" height="'+wall_container_h+'" class="imgZoom" />';
                new_w = w_diff;
                new_h = wall_container_h;
            }

            if(img!=0)
            {
                return image;
            }
            
            else{
                $('.imgZoom').css('width', new_w);
                $('.imgZoom').css('height', new_h);
            }
            
        }
        
        this.showItem = function(id) {
            $('body').css('overflow', 'hidden');
            
            $(wall_container).css('display', 'block');
            $(wall).css('display', 'block');
            
            link = $(wall_items).find("a").get(id);
            
            var $img_detail = $(link).parent(wall_items).find("span.img_detail").html();
            var $text = $(link).parent(wall_items).find("span.tooltip").html();
            
            //$(wall_loading).fadeIn();
            
            var position = $(wall_items).find("a").index(id);
            
            (position >= wall_items_count) ? next_item = 0 : next_item = position;
            
            position = position-2;
            (position < 0) ? prev_item = (wall_items_count-1) : prev_item = position;
            
            var scope = this;
            $.imgpreload($img_detail, function(){
                var $img = new Image();
                $img.src = $img_detail;
                
                ht = '';
                ht += '<div class="'+wall_detail_controls_container+'">';
                ht += '<a href="#" rel="'+prev_item+'" class="'+options.itemsBtnClose+'"><\/a>';
                ht += '<a href="#" rel="'+prev_item+'" class="'+options.itemsBtnPrev+'"><\/a>';
                ht += '<a href="#" rel="'+next_item+'" class="'+options.itemsBtnNext+'"><\/a>';
                ht += '<span class="'+wall_detail_info.split(".").join('')+'">'+$text+'<\/span>';
                ht += '<\/div>';
                ht += '<div class="'+wall_detail_image_container+'">';
                ht += scope.setBgImage($img.src, $img.width, $img.height);
                ht += '<\/div>';
                
                $(wall_detail).empty().html(ht).fadeIn(options.detailTransitionInSpeed, function() {
                    if(options.imgPanning) {
                        (options.imgPanningCenter) ? $imgOrient = 'center' : $imgOrient = 'top';
                        (options.imgPanningZoom)   ? $imgZoom = 'yes' : $imgZoom = 'no';
                        $pancontainer = $(wall_detail);
                        $this = $pancontainer;
                        $this.css('cursor', 'move');
                        $img = $this.find('img:eq(0)');
                        $options={$pancontainer:$this, pos:$imgOrient, curzoom:1, canzoom:$imgZoom, wrappersize:[$this.width(), $this.height()]};
                        $img.imgmover($options);
                    }
                
                    $(wall_loading).fadeOut(200, function() {
                        if(options.showTooltip)
                        {
                            $(wall_detail).find(wall_detail_info).animate({bottom:20});
                        }
                    });
                });
            });
        };
        
        this.bindItemActions = function() {
            links = $(wall_items).find("a");
            
            links.mouseover(function(){
                $(this).find("span.title").show();
            });

            links.mouseout(function(){
                $(wall_items).find("span.title").hide();
            });
            
            var scope = this;
            links.bind('click', function(){
                var $img_detail = $(this).parent(wall_items).find("span.img_detail").html();
                var $text = $(this).parent(wall_items).find("span.tooltip").html();
                $(wall_loading).fadeIn();
                
                var position = $(wall_items).find("a").index(this)+1;
                
                (position >= wall_items_count) ? next_item = 0 : next_item = position;
                
                position = position-2;
                (position < 0) ? prev_item = (wall_items_count-1) : prev_item = position;
                
                $.imgpreload($img_detail, function(){
                    var $img = new Image();
                    $img.src = $img_detail;
                    
                    ht = '';
                    ht += '<div class="'+wall_detail_controls_container+'">';
                    ht += '<a href="#" rel="'+prev_item+'" class="'+options.itemsBtnClose+'"><\/a>';
                    ht += '<a href="#" rel="'+prev_item+'" class="'+options.itemsBtnPrev+'"><\/a>';
                    ht += '<a href="#" rel="'+next_item+'" class="'+options.itemsBtnNext+'"><\/a>';
                    ht += '<span class="'+wall_detail_info.split(".").join('')+'">'+$text+'<\/span>';
                    ht += '<\/div>';
                    ht += '<div class="'+wall_detail_image_container+'">';
                    ht += scope.setBgImage($img.src, $img.width, $img.height);
                    ht += '<\/div>';
                    
                    $(wall_detail).empty().html(ht).fadeIn(options.detailTransitionInSpeed, function() {
                        if(options.imgPanning) {
                            (options.imgPanningCenter) ? $imgOrient = 'center' : $imgOrient = 'top';
                            (options.imgPanningZoom)   ? $imgZoom = 'yes' : $imgZoom = 'no';
                            $pancontainer = $(wall_detail);
                            $this = $pancontainer;
                            $this.css('cursor', 'move');
                            $img = $this.find('img:eq(0)');
                            $options={$pancontainer:$this, pos:$imgOrient, curzoom:1, canzoom:$imgZoom, wrappersize:[$this.width(), $this.height()]};
                            $img.imgmover($options);
                        }
                    
                        $(wall_loading).fadeOut(200, function() {
                            if(options.showTooltip)
                            {
                                $(wall_detail).find(wall_detail_info).animate({bottom:20});
                            }
                        });
                    });
                });

                return false;
            });
            
            $(document).on("click", '.'+options.itemsBtnPrev, function(e) {
                e.preventDefault();
                prev_items = $(this).attr("rel");
                $(wall_items).find('a').eq(prev_items).trigger('click');
            });
            
            $(document).on("click", '.'+options.itemsBtnNext, function(e) {
                e.preventDefault();
                next_items = $(this).attr("rel");
                $(wall_items).find('a').eq(next_items).trigger('click');
            });
            
            $(document).on("click", '.'+options.itemsBtnClose, function(e) {
                e.preventDefault();
                $(wall_detail).fadeOut(200, function() {
                    $(this).empty();
                    $(wall).hide();
                    $('body').css('overflow', 'visible');
                });
            });
        };
        
        this.setItem = function(pos) {
            x++;
            if(x > wall_items_count){
                $(wall_loading).fadeOut();
                return;
            }
            
            var $item = $(wall_items).eq(pos);
            
            var item_bg = $item.find(".bg").html();

            var scope = this;
            $.imgpreload(item_bg, function(){
                $item.css({'background-image' : 'url('+ item_bg +')'});
                $item.animate(
                    {width : wall_items_w, height : wall_items_h }, 1, function()
                        { 
                            switch (options.itemTransition)
                            {
                                case 'fadeIn' : 
                                    $item.fadeIn(options.itemTransitionSpeed, function(){
                                        scope.setItem(x);
                                    });
                                break;
                                
                                case 'slideDown' : 
                                    $item.slideDown(options.itemTransitionSpeed, function(){
                                        scope.setItem(x)
                                    });
                                break;
                                
                                default : 
                                    $item.toggle(1, function(){
                                        scope.setItem(x)
                                    });
                                break;
                                
                            }
                        }
                );
            });
        };
        
        this.init = function(el, options) {
            
            this.setWallDimensions();
            
            $('.'+options.itemsBtnClose).trigger('click');
            
            this.bindItemActions();
            
            /* Setting resize handler for recalculating dimensions */
            var scope = this;
            $(window).resize(function(){
                 scope.setWallDimensions(true);
            });
            
            $(document).keydown(function(e) {
                if (e.keyCode == 27) {
                    if (el.is(':visible')) {
                        $('.'+options.itemsBtnClose).trigger('click');
                    }
                }
            });
        };
        
        this.init(el, options);
    };

    $.fullWall.defaultOptions = {
        'itemTransition'	       : 'fadeIn',
        'itemTransitionSpeed'      : 200,
        'itemsForRow' 		       : 5,
        'itemsBtnNext'		       : 'jmFullWall-next',
        'itemsBtnPrev'		       : 'jmFullWall-prev',
        'itemsBtnClose'		       : 'jmFullWall-close',
        'detailTransitionIn'  	   : 'fadeIn',
        'detailTransitionInSpeed'  : 500,
        'detailTransitionOut'  	   : 'fadeOut',
        'detailTransitionOutSpeed' : 500,
        'showTooltip'			   : true,
        'imgPanning'			   : true,
        'imgPanningCenter'	       : true,
        'imgPanningZoom'	       : true
    }
    
    $.fn.fullWall = function(options) {
        return this.each(function() {
            (new $.fullWall($(this), options));
        });
    };
}) (jQuery);
