$(function() {
  $('a#clear').bind('click', function() {
    $.getJSON('/clear',
        function(data) {
    });
    return false;
  });
});