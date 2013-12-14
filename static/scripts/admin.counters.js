/**
 * Created by milan on 12/14/13.
 */
$('input[type="text"]').change(function() {
    var id = $(this).attr('id');
    $('button[name="action:edit"]')
        .attr({disabled: 'disabled'}).addClass('disabled');
    $('button[value="' + id + '"]')
        .removeAttr('disabled').removeClass('disabled');
});