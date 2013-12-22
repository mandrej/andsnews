/**
 * Created by milan on 12/14/13.
 */
$('#main button').click(function(evt) {
    evt.preventDefault();
    $('#overlay, #spinner').show();
    var row = $(this).closest('tr');
    var url = '/admin/images';
    var params = {'safe_key': row.attr('id'), 'action': $(this).attr('name'), 'token': token};

    if (params['action'] == 'delete') {
        var done = function(data) {
            if (data.success == true) {
                $('#overlay, #spinner').hide();
                row.find('._small').html('<img src="/static/images/icon_no.png" alt=""/>');
                row.find('button[name=delete]')
                    .attr('disabled', 'disabled').addClass('disabled');
                row.find('button[name=make]')
                    .removeAttr('disabled').removeClass('disabled');
            }
        }
    } else if (params['action'] == 'make') {
        var done = function(data) {
            if (data.success == true) {
                $('#overlay, #spinner').hide();
                row.find('._small').html(data.small);
                row.find('button[name=make]')
                    .attr('disabled', 'disabled').addClass('disabled');
                row.find('button[name=delete]')
                    .removeAttr('disabled').removeClass('disabled');
            }
        }
    }
    $.post(url, params, done, 'json');
});