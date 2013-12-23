/**
 * Various Common jQuery plugins
 *
 * Copyright (c) 2008 Milan Andrejevic <milan.andrejevic@gmail.com>
 * Licensed under the MIT License:
 * http://www.opensource.org/licenses/mit-license.php
 */
(function($) {
	$.fn.minus = function() {
		$(this).html($(this).html().replace(/[+]/i, "−"));
		return this
	};
	$.fn.plus = function() {
        $(this).html($(this).html().replace(/[−]/i, "+"));
		return this
	};
	/*
	 * collapseGroup - Expand/ Collapse items in a group, 
	 * 				   one at the time, toggle +/− indicator
	 * $Version: 2009.08.04
	 *
	 * Example: $('.ee').collapseGroup();
	 * 			<h4 class="ee collapse">... [+|−]</h4>
	 * 			<div class="hide">...</div>
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
	 * slugify - Slugify field text
	 * $Version: 2008.06.17
	 * Depends on urlify.js
	 *
	 * Example: $('#id_headline').slugify({slug: $('#id_slug')});
	 */
	$.fn.slugify = function(options) {
		var opts = $.extend({}, slugifyDefaults, options);
		var output = $(opts.slug);

		$(this).blur(function() {
			$(output).val(URLify($(this).val(), opts.max));
		})
		return this
	};
	slugifyDefaults = {max: 50, slug: '#slug:enabled'};
	/*
	 * focusHighlight - Highlights paragraph on element focus
	 * $Version: 2009.02.08
	 * 
	 * Example: $('input, select, textarea').focusHighlight();
	 */
	$.fn.focusHighlight = function(options) {
		var opts = $.extend({}, focusHighlightDefaults, options);
		return this.each(function() {
			var para = $(this).parents('p');
			$(this).focus(function() {
				$(para).addClass(opts.highlightClass);
			}).blur(function() {
				$(para).removeClass(opts.highlightClass);
			});
		});
	};
	focusHighlightDefaults = {
		highlightClass: 'focus' 
	};
    /*
	 * Style table columns according to colgroup col style
	 * $Version: 2010.01.25
	 * 
	 * Example: $('table').colStyle();
	 */
	$.fn.colStyle = function() {
        return this.each(function() {
			var table = $(this);
            var styles = $.map($('col', table), function(e) {
            	return $(e).attr('style') || "";
            })
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
    // close
    $('a.close').live('click', function(evt) {
        evt.preventDefault();
        $(this).parents('.modal').hide();
        $('#overlay').hide();
    });
    // tools
    $('#tools').click(function(evt) {
        evt.preventDefault();
        $('.menu').toggle('slow');
    });
    // menu
    $('.menu').click(function(evt) {
        var disallow = {"A": 1, "BUTTON": 1, "INPUT": 1};
        var parnetTagName = $(evt.target).parent()[0].tagName;
        if (!(disallow[evt.target.tagName] || disallow[parnetTagName])) {
            evt.preventDefault();
            $('.menu').toggle('slow');
        }
    });
})(jQuery);
