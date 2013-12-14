/**
 * Created by milan on 12/14/13.
 */
$('#main button, #sidebar button').click(function() {
    $('#overlay, #spinner').show();
});
$('.ff, .ss').collapseGroup();
$('.zebra').colStyle();
$('#tools').click(function(evt) {
    evt.preventDefault();
    $('.menu').toggle('slow');
});
$('.menu').click(function(evt) {
    var disallow = {"A": 1, "BUTTON": 1, "INPUT": 1};
    var parnetTagName = $(evt.target).parent()[0].tagName;
    if (!(disallow[evt.target.tagName] || disallow[parnetTagName])) {
        $('.menu').toggle('slow');
        evt.preventDefault();
    }
});