function playlistitem_set_sorting() {
    var i = 0;
    $.each($("#playlistitem_set-group .module>table .dynamic-playlistitem_set"),
        function(index, elem)
    {
        if (index % 2) {
            $(elem).addClass("row2").removeClass("row1")
        } else {
            $(elem).addClass("row1").removeClass("row2")
        }
        if ($(elem).find("[name$='video']").attr('value')) {
            $(elem).find("[name$='sort_order']").attr('value', index);
        } else {
            $(elem).find("[name$='sort_order']").attr('value', '');
        }
        $.each($(elem).find("[name^='playlistitem_set']"), function(j, obj){
            $(obj).attr("id", $(obj).attr("id").replace(/[0-9]+/g, i))
            $(obj).attr("name", $(obj).attr("name").replace(/[0-9]+/g, i))
        });
        i++;
    });
}

$(function() {
    $("#playlist_form #playlistitem_set-group .module>table").sortable({
        items: "tr.form-row",
        placeholder: "ui-state-highlight",
        stop: playlistitem_set_sorting
    });
    $("#playlistitem_set-group .module.table.dynamic-form" ).disableSelection();
    $("#playlist_form #playlistitem_set-group [name$='video']").live("change", playlistitem_set_sorting);
    $("#playlist_form #playlistitem_set-group .remove-handler").live("click", playlistitem_set_sorting);

    $( ".accordion" )
      .accordion({
        header: "> div > h3"
      })
      .sortable({
        axis: "y",
        handle: "h3",
        stop: function( event, ui ) {
          // IE doesn't register the blur when sorting
          // so trigger focusout handlers to remove .ui-state-focus
          ui.item.children( "h3" ).triggerHandler( "focusout" );

          // Refresh accordion to handle new order
          $( this ).accordion( "refresh" );
        }
      });
});
