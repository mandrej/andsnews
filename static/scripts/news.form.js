/**
 * Created by milan on 12/14/13.
 */
$('#headline').slugify();
$("#tags").autocomplete("/complete/Feed_tags", autoCompleteOptions);
$('#main button').click(function() {
    $('#overlay, #spinner').show();
});