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
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function two_digits(value) {
  if (value < 10) {
    return "0" + value
  } else if (!!value) {
    return value
  }
  return "00";
}

function seconds_to_hms(value) {
  var hours = two_digits(parseInt(value / 3600));
  var minutes = two_digits(parseInt(value / 60) % 60);
  var seconds = two_digits(parseInt(value % 60));
  return hours + ":" + minutes + ":" + seconds
}

function build_formset_data(prefix, array, fields) {
  // this amazing function build formset data to save formsets (create new,
  // edit existing, delete objects)
  var initial = 0,
      total = 0;
  var rows = {};
  var item;
  prefix = prefix + '-';
  var full_prefix;
  var i, j, field;
  for (i = 0; i < array.length; i++) {
    item = array[i];
    full_prefix = prefix + i + '-';
    total++;
    if (item['id']) {
      initial++;
      rows[full_prefix + 'id'] = item['id'];
    }
    if (item['DELETE']) {
      rows[full_prefix + 'DELETE'] = 'on';
    }
    for (j = 0; j < fields.length; j++) {
      field = fields[j];
      rows[full_prefix + field] = item[field];
    }
  }
  rows[prefix + 'TOTAL_FORMS'] = total;
  rows[prefix + 'INITIAL_FORMS'] = initial;
  rows[prefix + 'MAX_NUM_FORMS'] = 1000;
  return rows;
}

function build_playlistblock_formset_data(array) {
  return build_formset_data('playlistblock_set', array, ['title', 'limit', 'sort_order']);
}

function build_playlistitem_formset_data(array) {
  return build_formset_data('playlistitem_set', array, ['video', 'sort_order']);
}

function get_block_data(container) {
  var obj = {};
  obj['id'] = $(container).attr('data-id');
  obj['limit'] = $(container).find('.limit').attr('data-value');
  obj['sort_order'] = $(container).find('.sort_order').attr('data-value');
  obj['title'] = $(container).find('.title').text();
  return obj;
}

function set_block_data() {
  var container;
  var limit = seconds_to_hms(parseInt(this['limit']) * 60);
  if ($(".playlistblock[data-id='" + this['id'] + "']").length) {
    container = $(".playlistblock[data-id='" + this['id'] + "']");
    $(container).find(".limit").attr("data-value", this['limit']);
    $(container).find(".limit").text(limit);
    $(container).find(".title").text(this['title']);
    $(container).find(".sort_order").text(this['sort_order'] + 1 + ".");
    $(container).find(".sort_order").attr("data-value", this['sort_order']);
    if (this['limit'] * 60000 > $(container).find(".duration").attr("data-value")) {
      $(container).find("tfoot tr").addClass("warning").attr("data-original-title", "Блок не заполнен").tooltip();
    } else {
      $(container).find("tfoot tr").removeClass("warning").tooltip("destroy");
    }
  } else {
    var sort_order = parseInt(this['sort_order']) + 1;
    container = $(
      '<div class="playlistblock" data-id="'+this['id'] + '">' +
        '<h3>' +
          '<span class="sort_order" data-value="' + this['sort_order'] + '">' + sort_order  + '.</span>' +
          '<span class="title">' + this['title'] + '</span>' +
          '<span class="glyphicon glyphicon-remove"></span>' +
          '<span class="glyphicon glyphicon-edit"></span>' +
          '<span class="glyphicon glyphicon-plus" data-toggle="modal" data-target="#videoStreamModal"></span>' +
        '</h3>' +
        '<table class="block-items-list">' +
          '<thead>' +
            '<tr>' +
              '<th>Название</th>' +
              '<th>Длительность</th>' +
              '<th>Просмотр</th>' +
              '<th>Действия</th>' +
            '</tr>' +
          '</thead>' +
          '<tbody>' +
            '<tr class="empty"><td colspan="4">Перетащите сюда видео справа</td></tr>' +
          '</tbody>' +
          '<tfoot>' +
            '<tr data-toggle="tooltip" data-placement="top" class="warning" title="Блок не заполнен">' +
              '<td></td>' +
              '<td colspan="3">' +
                '<span class="duration" data-value="0">00:00:00</span> из <span class="limit" data-value="'+ this['limit'] +'">' + limit + '</span>' +
              '</td>' +
            '</tr>' +
          '</tfoot>' +
        '</table>' +
      '</div>');
    container.appendTo(".blocks");
  }
}

function set_blocks(data) {
  if (data['errors']) {
    $.each(data['errors'], function(key, val) {
      console.log(key, val);
    });
  }
  $.each(data['blocks'], set_block_data);
  $( ".blocks").accordion("refresh");
}

function get_item_data(container) {
  var obj = {};
  if ($(container).attr('data-id')) {
    obj['id'] = $(container).attr('data-id');
  }
  obj['video'] = $(container).attr('data-video-id');
  return obj;
}

function set_item_data() {
  if (!$(".block-items-list [data-id='" + this['id'] + "']").length) {
    $(".block-items-list [data-id='']").attr("data-id", this['id']);
  }
}

function set_items(data) {
  if (data['errors']) {
    $.each(data['errors'], function(key, val) {
      console.log(key, val);
    });
  } else if (data['items']) {
    $.each(data['items'], set_item_data);
    var container = $(".playlistblock[data-id='" + data['block']['id'] + "'] ").get(0);
    var duration = data['block']['duration'];
    $(container).find(".duration").attr("data-value", duration);
    $(container).find(".duration").text(seconds_to_hms(duration / 1000));
    if ($(container).find(".limit").attr("data-value") * 60000 > duration) {
      $(container).find("tfoot tr").addClass("warning").attr("data-original-title", "Блок не заполнен").tooltip();
    } else {
      $(container).find("tfoot tr").removeClass("warning").attr("title", "").tooltip("destroy");
    }
  }
}

function collect_items_data(array) {
  var initial_data = [], added = [];
  array.each(function (i) {
    var obj = get_item_data(this);
    obj['sort_order'] = i;
    if (obj['id']) {
      initial_data.push(obj);
    } else {
      added.push(obj)
    }
  });
  return initial_data.concat(added)
}

$(function() {
  $('[data-toggle="tooltip"]').tooltip();

  var playlist_items_edit_url_rule = $('.blocks').attr("data-playlist-items-edit-url");
  var items_sortable_options = {
    axis: "y",
    cursor: "move",
    update: function(event, ui) {
      var el;
      if (ui.item) {
        el = $(ui.item);
      } else {
        el = $(ui.helper[0]);
      }
      el.siblings(".empty").remove();
      $.post(
          playlist_items_edit_url_rule.replace("0", el.parents(".playlistblock").attr('data-id')),
          build_playlistitem_formset_data(collect_items_data(el.parent().children())),
          set_items)
    }
  };

  // we can sort items in block
  $(".block-items-list tbody").sortable(items_sortable_options);

  // we can collapse and uncollapse blocks as well as reorder blocks

  $(".blocks").accordion({
      header: "> div > h3",
      collapsible: true,
      heightStyle: "content",
      beforeActivate: function(e, ui) {
        if ($(e.toElement).hasClass("glyphicon")) {
          e.preventDefault()
        }
      }
    })
    .sortable({
      axis: "y",
      handle: "h3",
      cursor: "move",
      stop: function( event, ui ) {
        // IE doesn't register the blur when sorting
        // so trigger focusout handlers to remove .ui-state-focus
        ui.item.children( "h3" ).triggerHandler( "focusout" );
        // Refresh accordion to handle new order
        var initial_data = [];
        $('.blocks .playlistblock').each(function(i){
          var obj = get_block_data(this);
          obj['sort_order'] = i;
          initial_data.push(obj);
        });
        var data = build_playlistblock_formset_data(initial_data);
        $.post(
          $("#block-form").attr("data-playlistblocks-edit-url"),
          data,
          set_blocks
        );
      }
    });

  // reset block form after hiding
  $("#playListBlockModal").on('hidden.bs.modal', function(e) {
    $(this).find('form').get(0).reset();
  });

  //save block (create or update)
  $("#block-form").on("submit", function(e){
    e.preventDefault();
    var form = $(this).get(0);
    var initial_data = {id: form.id.value, title: form.title.value, limit: form.limit.value};
    if (!!form.sort_order.value) {
      initial_data['sort_order'] = form.sort_order.value;
    } else {
      initial_data['sort_order'] = $(".blocks .playlistblock").size();
    }
    var data = build_playlistblock_formset_data([initial_data]);
    $.post(
        $(form).attr("data-playlistblocks-edit-url"),
        data,
        function(response) {
          set_blocks(response);
          form.reset();
          $("#id_id").add("#id_sort_order").val("");
          $("#playListBlockModal").modal('hide');
          $(".block-items-list tbody").sortable(items_sortable_options);
        }
    );
  });
  $(".blocks").on("click", ".playlistblock>h3>span.glyphicon-edit", function(e){
    var obj = get_block_data($(this).parents(".playlistblock"));
    $('#id_title').val(obj['title']);
    $('#id_limit').val(obj['limit']);
    $('#id_id').val(obj['id']);
    $('#id_sort_order').val(obj['sort_order']);
    $("#playListBlockModal").modal("show");
  });
  $(".blocks").on("click", ".playlistblock>h3>span.glyphicon-remove", function(e){
    if (confirm("Уверены, что хотите удалить блок?")) {
      var initial_data = [];
      var block = $(this).parents(".playlistblock");
      var obj = get_block_data(block);
      obj['DELETE'] = true;
      initial_data.push(obj);
      block.nextAll('.playlistblock').each(function(i){
        var obj = get_block_data(this);
        obj['sort_order']--;
        initial_data.push(obj);
      });
      var data = build_playlistblock_formset_data(initial_data);
      $.post($("#block-form").attr("data-playlistblocks-edit-url"),
          data,
          function(response){
            set_blocks(response);
            $(block).remove();
          }
      );
    }
  });

  $("#video-search-form #id_category").on("change", function(){
    var action = $("#video-search-form").attr("data-action");
    var category_id = $(this).val();
    if (category_id) {
      $.get(
        action.replace("0", category_id),
        function(data) {
          var videos = [];
          $.each(data['object_list'], function(){
            videos.push($(
              '<tr data-video-id="' + this['id'] + '" data-id="">' +
                '<td>' + this['title'] + '</td>' +
                '<td>' + seconds_to_hms(parseInt(this['duration'] / 1000)) + '</td>' +
                '<td><a target="_blank" href="http://probumerang.tv/video/' + this['id'] + '/">посмотреть</a></td>' +
                '<td><span class="glyphicon glyphicon-remove"></span></td>' +
              '</tr>'
            ))
          });
          $("#video-list tbody").html(videos);
          $("#video-list tbody tr").draggable({
            connectToSortable: ".block-items-list tbody",
            helper: "clone",
            revert: "invalid",
            cursor: "move"
            })
          });
          $("#video-list").disableSelection();
    } else {
      $("#video-list tbody").text("");
    }
  });

  $(".blocks").on("click", ".playlistblock .block-items-list .glyphicon-remove", function(e){
    if (confirm("Уверены, что хотите удалить блок?")) {
      var item = $(this).parents("tr");
      var container = $(item).parent();
      var obj = get_item_data(item);
      obj['DELETE'] = true;
      obj['sort_order'] = 0;
      item.remove();
      if (!$(container).children().size()) {
        container.append('<tr class="empty"><td colspan="4">Перетащите сюда видео справа</td></tr>');
      }
      $.post(
          playlist_items_edit_url_rule.replace("0", container.parents(".playlistblock").attr('data-id')),
          build_playlistitem_formset_data([obj].concat(collect_items_data($(container).children()))),
          set_items
      );
    }
  });
  $("#video-stream-form").submit(function(e) {
    e.preventDefault();
  });
  $("#videoStreamModal").on('shown.bs.modal', function(e){
    var block = $(e.relatedTarget).parents(".playlistblock").get(0);
    $("#video-stream-form").submit(function(e) {
      e.preventDefault();
      $.post(
          $(this).attr("action"),
          $(this).serialize(),
          function(data) {
            var row = $(
                '<tr data-id="" data-video-id="' + data['object']['pk'] + '">' +
                  '<td>' + data['object']['title'] + '</td>' +
                  '<td>' + seconds_to_hms(parseInt(data['object']['duration'] / 1000)) + '</td>' +
                  '<td></td>' +
                  '<td><span class="glyphicon glyphicon-remove"></span></td>' +
                '</tr>');
            $(block).find('.block-items-list tbody').append(row)
            $(block).find(".empty").remove();
            $.post(
                playlist_items_edit_url_rule.replace("0", $(block).attr('data-id')),
                build_playlistitem_formset_data(collect_items_data($(block).find('tbody').children())),
                set_items);
            $("#videoStreamModal").modal('hide');
          }
      );
    });
  });
  $("#videoStreamModal").on('hide.bs.modal', function(){
    $(this).find('form').get(0).reset()
  });
});
