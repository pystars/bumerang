$(function() {
    $("#playlistitem_set-group .module.table.dynamic-form").sortable({
        items: "div.tbody",
        placeholder: "ui-state-highlight",
        stop: function(event, ui) {
            $("#playlistitem_set-group .module.table.dynamic-form div.tbody [name$='sort_order']").each(
                function(index) {
                    $(this).attr('value', index + 1);
                }
            )
        }
    });
    $( "#playlistitem_set-group .module.table.dynamic-form" ).disableSelection();
});