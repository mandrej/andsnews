$(document).ready(function () {
    var $pinner = $('#overlay, #spinner');
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

    // autocomplete
    var autoCompleteOptions = {
        width: 284,
        selectFirst: false,
        multiple: false,
        matchContains: true
    };

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

    $('#searchForm').submit(function() {
        $pinner.show();
    });

    // search highlight
    var matchFind = location.search.match(/find=([^&]+)/i);
    if (matchFind) {
        $(document).SearchHighlight({exact: "partial", highlight: "#main", keys: decodeURIComponent(matchFind[1])});
    }

    // confirm
    $('a.confirm').click(function(evt) {
        evt.preventDefault();
        $('#confirm').load(this.href, function() {
            $('#overlay, #confirm').show();
            $('.content button').click(function() {
                $('#overlay, #spinner').show();
            });
        });
    });
    // add comment
    $('a.comment_add').click(function(evt) {
        evt.preventDefault();
        $('#addcomment').load(this.href, function() {
            $('#overlay, #addcomment').show();
            $('#body').markItUp(cmntSettings, {nameSpace: 'small'});
            $('.content button').click(function(evt) {
                evt.preventDefault();
                $.ajax({
                    type: 'POST',
                    url: $('#addcommentForm').attr('action'),
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
        });
    });

    // masonry
    var $container = $('#container');
    $container.imagesLoaded(function() {
        $container.masonry({
            itemSelector: '.brick'
        });
        $container.masonry('bindResize');
    });
});