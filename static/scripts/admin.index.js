/**
 * Created by milan on 12/14/13.
 */
function build() {
    $.getJSON('/admin/memcache/', function(data) {
        $.each(data, function(key, value) {
            var tmpl = '', title = key.split('_').pop() + ' cloud';
            if (value) {
                tmpl += '<button type="submit" name="delete" value="' + key + '">delete</button>';
                tmpl += '<a class="graph" href="/visualize/' + key + '">graph</a>';
                tmpl += '<h4 class="ff">' + title + ' [+]</h4>';
                tmpl += '<div class="hide">';
                $.each(value, function(name, count) {
                    tmpl += '<dl><dt>' + name + '</dt>';
                    tmpl += '<dd>' + count + '</dd></dl>';
                });
                tmpl += '</div>';
            } else {
                tmpl += '<button type="submit" name="put" value="' + key + '">create</button>';
                tmpl += '<h4>' + title + ' [EMPTY]</h4>';
            }
            $('#' + key).html(tmpl);
        });
        $('.ff').collapseGroup();
    });
}
$('button').live('click', function() {
    $('#spinner').show();
    var key = $(this).val(), method = $(this).attr('name');
    $.ajax({
        url: '/admin/memcache/' + key,
        type: method,
        dataType: 'json',
        success: function(data) {
            $('#spinner').hide();
            build();
            $('.ff').unbind().collapseGroup();
        }
    });
});
$('a.graph').live('click', function(evt) {
    evt.preventDefault();
    $('#graph').load(this.href, function() {
        $('#overlay, #graph').show();
    });
});
build();

var drawSpectra = function() {
    var sat = $('#sat').slider('value');
    var lum = $('#lum').slider('value');

    $.getJSON('/admin/spectra?sat=' + sat + '&lum=' + lum, function(data) {
        $('#spectra').empty();
        $.each(data, function(name, colors) {
            var str = '<div style="clear: both"><span class="item" style="width: 50px;">' + name + '</span>';
            $.each(colors, function(i, c) {
                str += '<span class="item" style="background: ' + c + '">&nbsp;</span>';
            });
            str += '</div>';
            $('#spectra').append(str);
        });
    })
};
$('.slider').slider({
    min: 0, max: 100, step: 5,
    change: function(event, ui) {
        $('input[name=' + event.target.id + ']').val(ui.value);
        drawSpectra();
    }
})
$('h2.ss').click(function() {
    drawSpectra();
});
$('#sat').slider('value', 35);
$('#lum').slider('value', 40);