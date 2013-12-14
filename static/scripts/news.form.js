/**
 * Created by milan on 12/14/13.
 */
$('#headline').slugify();
$("#tags").autocomplete("/complete/Feed_tags", {
    width: 284,
    selectFirst: false,
    multiple: true,
    matchContains: true
});
$('#main button').click(function() {
    $('#overlay, #spinner').show();
});