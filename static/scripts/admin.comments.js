/**
 * Created by milan on 12/14/13.
 */
$('#main button').click(function(evt) {
    evt.preventDefault();
    var row = $(this).parents('tr');
    var url = '/admin/comments';
    var params = {'safe_key': row.attr('id'), 'token': token};
    if ($(this).attr('name') == 'save') {
        params['body'] = $('textarea', row).val();
        $.post(url, params, function(data) {
            if (data.success == true) {
                $('#overlay, #spinner').hide();
            }
        }, 'json');
    }
    if ($(this).attr('name') == 'delete') {
        $.post(url, params, function(data) {
            if (data.success == true) {
                row.remove();
                $('#overlay, #spinner').hide();
            }
        }, 'json');
    }
});