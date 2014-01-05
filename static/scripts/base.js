// search highlight
var matchFind = location.search.match(/find=([^&]+)/i);
if (matchFind) {
    $(document).SearchHighlight({exact: "partial", highlight: "#main", keys: decodeURIComponent(matchFind[1])});
}
// startup
var crumbs = location.pathname.split('/');
crumbs.shift();
crumbs.shift();

if (kind != '') {
    $('.hide').hide();
    $('.collapse').each(function() {
        $(this).plus();
    });

    if (crumbs.length >= 2) {
        var field = crumbs[0];
        var available = ['tags', 'date', 'author', 'color', 'model', 'lens', 'eqv', 'iso', 'forkind'];
        if ($.inArray(field, available) != -1) {
            $.ajax({
                url: '/filter/' + kind + '_' + field + '/' + crumbs[1],
                context: $('#' + field + 'cloud'),
                success: function(snippet) {
                    $(this).html(snippet).slideDown();
                    $('.' + field).minus();
                }
            });
        }
    }
}
$('.collapse').click(function(evt) {
    evt.preventDefault();
    var cntx = $(this);
    var url = cntx.attr('href');
    var key = url.split('/').pop();
    var field = key.split('_').pop();

    $('.hide').slideUp();
    $('.collapse').each(function() {
        $(this).plus();
    });

    $('#overlay, #spinner').show();
    if (crumbs[0] == field && crumbs[1] != undefined) url += '/' + crumbs[1];
    $.ajax({
        url: url,
        context: $('#' + field + 'cloud'),
        success: function(snippet) {
            $(this).html(snippet).slideDown();
            cntx.minus();
            $('#overlay, #spinner').hide();
        }
    });
});