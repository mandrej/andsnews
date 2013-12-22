/**
 * Created by milan on 12/14/13.
 */
$('#headline').slugify();
$("#tags").autocomplete("/complete/Photo_tags", $.extend({}, autoCompleteOptions, {multiple: true}));
$("#lens").autocomplete("/complete/Photo_lens", autoCompleteOptions);
$("#crop_factor").autocomplete("/complete/Photo_crop_factor", autoCompleteOptions);
$('button[type=submit]').click(function() {
    $('#overlay, #spinner').show();
});

var write_palette = function() {
    $.getJSON(palette_url, function(data) {
        var cntx = $('table.palette');
        cntx.empty().append('<tr><th>active</th>' +
            '<td><span class="dot" data-color="[' + data.active.color + ']" style="border-color: ' + data.active.hex + '"></span></td>' +
            '<th>' + data.active['class'] + '</th></tr>');
        $.each(data.palette, function(i, pal) {
            cntx.append('<tr><th>' + pal.prominence + '</th>' +
                '<td><span class="dot" data-color="[' + pal.color + ']" style="border-color: ' + pal.hex + '"></span></td>' +
                '<td>' + pal['class'] + '</td></tr>');
        });
        if (data.bgcolor) {
            cntx.append('<tr><th>' + data.bgcolor.prominence + '</th>' +
                '<td><span class="dot" data-color="[' + data.bgcolor.color + ']" style="border-color: ' + data.bgcolor.hex + '"></span></td>' +
                '<td>' + data.bgcolor['class'] + '</td></tr>');
        }
//        cntx.after('<p>' + explain + '</p>');
    });
};
$('button[type=button]').click(function(evt) {
    evt.preventDefault();
    write_palette();
});
$('.dot').live('click', function() {
    var rgb = $(this).attr('data-color');
    $.post(palette_url, {'rgb': rgb}, function(data) {
        if (data.success == true) {
            write_palette();
        }
    })
});