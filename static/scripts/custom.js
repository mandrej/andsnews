/**
 * Created by milan on 1/4/15.
 */
$(function() {
    "use strict";

	$.fn.minus = function() {
		$(this).html($(this).html().replace(/[+]/i, "−"));
		return this
	};
	$.fn.plus = function() {
        $(this).html($(this).html().replace(/[−]/i, "+"));
		return this
	};
	/*
        Expand/ Collapse items in a group,
        one at the time, toggle +/− indicator
	    $Version: 2009.08.04
        Example: $('.ee').collapseGroup();
                <h4 class="ee collapse">... [+|−]</h4>
                <div class="hide">...</div>
    */
	$.fn.collapseGroup = function() {
		var thisContexts = $(this);

		return this.each(function() {
			var $this = $(this);
			var $next = $this.next();
			$this.click(function() {
				if ($next.is(':hidden')) {
					$this.minus();
					$next.slideDown();
				} else {
					$this.plus();
					$next.slideUp();
				}
				thisContexts.not($this).each(function() {
					$(this).plus();
					$(this).next().slideUp();
				});
			})
		})
	};
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

$(document).ready(function() {
    // close
    $('.modal').on('click', '.close', function (evt) {
        evt.preventDefault();
        $(this).parents('.modal').hide();
        $('#overlay').hide();
    });
    // confirm
    $(document).on('click', 'a.confirm', function (evt) {
        evt.preventDefault();
        $('#confirm').load(this.href, function () {
            $('#overlay, #confirm').show();
            $('.content button').click(function () {
                $('#overlay, #spinner').show();
            });
        });
    });
});