var $pinner = $('#overlay, #spinner');
var kind = '{{ kind }}';
var crumbs = location.pathname.split('/');
crumbs.shift();
crumbs.shift();

$('a.confirm').click(function(evt) {
    evt.preventDefault();
    $('#confirm').load(this.href, function() {
        $('#overlay, #confirm').show();
    });
});
$('#searchForm').submit(function() {
    $pinner.show();
});

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

    $pinner.show();
    if (crumbs[0] == field && crumbs[1] != undefined) url += '/' + crumbs[1];
    $.ajax({
        url: url,
        context: $('#' + field + 'cloud'),
        success: function(snippet) {
            $(this).html(snippet).slideDown();
            cntx.minus();
            $pinner.hide();
        }
    });
});

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

// masonry
var $container = $('#container');
$container.imagesLoaded(function() {
    $container.masonry({
        itemSelector: '.brick'
    });
    $container.masonry('bindResize');
});