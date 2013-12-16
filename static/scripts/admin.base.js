/**
 * Created by milan on 12/14/13.
 */
$('#main button, #sidebar button').click(function() {
    $('#overlay, #spinner').show();
});
$('.ff, .ss').collapseGroup();
$('.zebra').colStyle();