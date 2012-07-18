function playlistitem_set_sorting() {
    var i = 0;
    $.each($("#playlistitem_set-group .module.table.dynamic-form div.tbody.dynamic-form"),
        function(index, elem)
    {
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
    $("#playlist_form #playlistitem_set-group .module.table.dynamic-form").sortable({
        items: "div.tbody.dynamic-form",
        placeholder: "ui-state-highlight",
        stop: playlistitem_set_sorting
    });
    $("#playlistitem_set-group .module.table.dynamic-form" ).disableSelection();
    $("#playlist_form #playlistitem_set-group [name$='video']").live("change", playlistitem_set_sorting);
    $("#playlist_form #playlistitem_set-group .remove-handler").live("click", playlistitem_set_sorting);
});
