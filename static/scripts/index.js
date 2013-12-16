$(document).ready(function () {
    $.getJSON('/latest', function(data) {
        $.backstretch(data, {fade: 1000, duration: 4000});
    });
    $('.remove').click(function(evt) {
        evt.preventDefault();
        $('aside').slideUp();
    });
});