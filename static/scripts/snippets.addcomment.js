/**
 * Created by milan on 12/14/13.
 */
$('#body').markItUp(cmntSettings, {nameSpace: 'small'});
$('.content button').click(function(evt) {
    evt.preventDefault();
    $.ajax({
        type: 'POST',
        url: url,
        data: {'body': $('#body').val(), 'token': token},
        success: function(data) {
            if (typeof(data) == 'string') {
                $('.dummy').hide();
                $('.info').show()
                $('.comments').prepend(data);
                $('a.confirm').click(function(e) {
                    e.preventDefault();
                    $('#confirm').load(this.href, function() {
                        $('#overlay, #confirm').show();
                    });
                });
                setTimeout(function() {
                    $('#overlay, #addcomment').hide();
                }, 1000);
            } else {
                $('.error').text('');
                $.each(data, function(key, arr) {
                    $('.error.C_' + key).text(arr.join(', '));
                });
            }
        }
    });
});