var delay_time = 4000;

$(function(){
    // Messages
    $('.msg-close').click(function(){
        $(this).parent().hide();
    })
    $('.alert-message').delay(delay_time).hide(300);

    // Avatar
    $('#id_avatar[type=file]').change(function(event){
        $('form[name=avatar_form]').submit();
    });

    jQuery(function($) {
        $('#current_avatar').Jcrop({
            onChange:    function(c){
                $('#id_coords').val(JSON.stringify(c));
            },
            bgColor:     'black',
            bgOpacity:   .5,
            minSize: [100, 100],
            setSelect:   [ 100, 100, 50, 50 ],
            aspectRatio: 1
        });
    });



//    // Avatar
//    jQuery(function($) {
//        $('#cvs').Jcrop({
//            //onSelect:    showCoords,
//            bgColor:     'black',
//            bgOpacity:   .5,
//            minSize: [100, 100],
//            setSelect:   [ 100, 100, 50, 50 ],
//            aspectRatio: 1
//        });
//    });
//
//    $('#id_avatar[type=file]').change(function(event){
//
//        var file = event.target.files[0];
//        var i = $(file);
//
//
//        var reader = new FileReader();
//
//        var oFReader = new FileReader();
//        oFReader.readAsDataURL(event.target.files[0]);
//        oFReader.onload = function (oFREvent) {
//
//            var img = new Image();
//            img.onload = function () {
//                context.drawImage(this, 0, 0);
//            }
//            img.src = oFREvent.target.result;
//
//            console.log(img.width);
//
//            //document.getElementById("uploadPreview").src = oFREvent.target.result;
//            $('.jcrop-holder img').attr('src', oFREvent.target.result);
//
//        };
//
//
//        reader.onload = (function(theFile) {
//            return function(e) {
//                // Render thumbnail.
//                //var imgHTML = '<img class="file-input-thumb" src="' +  + '" title="' + theFile.name + '"/>';
//                //$('#asd').attr('src', e.target.result);
//                var i = new Image();
//                i.src = e.target.result;
//                console.log(i.width);
//
//                var i = $('<img>').attr('src', e.target.result);
//                console.log(i.width());
//
//                //i.src = e.target.result;
//                //console.log(i.fileSize);
//                $('.jcrop-holder img').attr('src', e.target.result);
////                if( typeof params.selector != 'undefined' ){
////                    $(params.selector).html(imgHTML);
////                }else{
////                    fileInput.before(imgHTML);
////                }
//            };
//        })(file);
//
//        // Read in the image file as a data URL.
//        //reader.readAsDataURL(file);
//
//
//    });
//    $('#asd').Jcrop({
//        //onSelect:    showCoords,
//        bgColor:     'black',
//        bgOpacity:   .5,
//        minSize: [100, 100],
//        setSelect:   [ 100, 100, 50, 50 ],
//        aspectRatio: 1
//    });
})
