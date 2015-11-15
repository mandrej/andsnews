/**
 * Created by milan on 11/12/15.
 */
$(function() {
    "use strict";
	/*
        Slugify field text
        $Version: 2008.06.17
        Depends on urlify.js
        Example: $('#id_headline').slugify({slug: $('#id_slug')});
	*/
	$.fn.slugify = function(options) {
        var defaults = {max: 50, slug: '#slug:enabled'};
		var opts = $.extend({}, defaults, options);
		var output = $(opts.slug);

		$(this).blur(function() {
			$(output).val(URLify($(this).val(), opts.max));
		});
		return this
	};
    /*
	    Style table columns according to colgroup col style
        $Version: 2010.01.25
        Example: $('table').colStyle();
	*/
	$.fn.colStyle = function() {
        return this.each(function() {
			var table = $(this);
            var styles = $.map($('col', table), function(e) {
            	return $(e).attr('style') || "";
            });
			if (styles.length > 0) {
	            $('thead th', table).each(function(i,eth) {
					var style = $(eth).attr('style') || "";
					style += styles[i];
					if (style != "") $(eth).attr('style', style);
	            });
	            $('tbody tr', table).each(function(i,etr) {
	                $('td',etr).each(function(i,etd) {
						var style = $(etd).attr('style') || "";
						style += styles[i];
	                    if (style != "") $(etd).attr('style', style);
	                })
	            });
			}
        })
	};
    /*
        Reverse array order
        2015.02.16
        Example: $page.find('.main').reverse().each(function(i, slide) {});
        http://stackoverflow.com/questions/1394020/jquery-each-backwards
     */
    $.fn.reverse = function() {
        return this.pushStack(this.get().reverse(), arguments);
    };
    /*
        Get Query Params as Object
        http://css-tricks.com/snippets/jquery/get-query-params-object/
     */
    $.extend({
        getQueryParameters : function(str) {
            if (str) str = str.replace(/^.*(\?)/,'');
            return (str || document.location.search).replace(/(^\?)/,'').split("&").map(function(n){return n = n.split("="),this[n[0]] = n[1],this}.bind({}))[0];
        }
    });
});
