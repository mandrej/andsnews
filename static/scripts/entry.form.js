/**
 * Created by milan on 12/14/13.
 */
$('#headline').slugify();
$('#body').markItUp(blogSettings, {nameSpace: 'big'});
$('#images img').click(function(evt) {
    evt.preventDefault();
    src = $(this).attr('src').replace('small', 'normal');
    title = $(this).attr('title');
    tab = '    ';
    $.markItUp(
        {replaceWith:'<figure class="left">\n'+tab+'<img src="' + src +
            '" alt="' + title + '"/>\n'+tab+'<p class="legend">' + title + '</p>\n</figure>\n'}
    );
});
$("#tags").autocomplete("/complete/Entry_tags", autoCompleteOptions);
$('#main button').click(function() {
    $('#overlay, #spinner').show();
});