var get_url = window.location.href.replace(/#$/, "") + ".json";

function fail(jqXHR, textStatus) {
  console.log("failed", jqXHR, textStatus);
}

function trigger(url) {
  return $.ajax({url: url, type: 'PUT'});
}

function refresh(data) {
  return $.ajax({url: get_url, dataType: 'json'});
}

function update(data) {
  // Update current state
  $("#current-state").text(data.state);

  // Update state diagram w/ cache-buster
  var url = data.image_url + "?random=" + Date.now();
  $("#state-diagram").attr("src", url);

  // Update valid events
  $("#valid-events").html('');
  $.each(data.events, function(i, evt) {
    $("#valid-events").append('<a href="#" data-target="' + evt.url + '" class="list-group-item">' + evt.name + '</a>');
  });
}

$(document).on('click', '.list-group-item', function(e) {
  var url = $(this).data('target');
  trigger(url).then(refresh, fail).then(update, fail);
});
