/*
    Various jQuery plugins

    Copyright (c) 2008 Milan Andrejevic <milan.andrejevic@gmail.com>
    Licensed under the MIT License:
    http://www.opensource.org/licenses/mit-license.php
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
		var opts = $.extend({}, slugifyDefaults, options);
		var output = $(opts.slug);

		$(this).blur(function() {
			$(output).val(URLify($(this).val(), opts.max));
		});
		return this
	};
	slugifyDefaults = {max: 50, slug: '#slug:enabled'};
	/*
	    Highlights paragraph on element focus
	    $Version: 2009.02.08
	    Example: $('input, select, textarea').focusHighlight();
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
	    Style table columns according to colgroup col style
        $Version: 2010.01.25
        Example: $('table').colStyle();
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
    /*
	    Draw copyrighted image on canvas
        $Version: 2014.01.08
    */
    $.fn.copyright = function(src) {
        var width = $(this).parent().width();
        var canvas = this[0];
        var cntx = canvas.getContext('2d');
        var img = new Image();
        img.src = src;
        img.onload = function() {
            var factor = width / img.width;
            if (factor > 1) factor = 1; // don't enlarge
            $(canvas).attr('width', img.width * factor).attr('height', img.height * factor);
            cntx.drawImage(img, 0, 0, img.width, img.height, 0, 0, img.width * factor, img.height * factor);
            cntx.font = '16px "PT Sans"';
            cntx.fillStyle = '#fff';
            cntx.shadowColor = '#000';
            cntx.shadowOffsetX = 0;
            cntx.shadowOffsetY = 0;
            cntx.shadowBlur = 5;
            cntx.fillText('© ands.appspot.com', 20, 30);
        };
        return canvas
    }
    // close
    $('.modal').on('click', '.close', function(evt) {
        evt.preventDefault();
        $(this).parents('.modal').hide();
        $('#overlay').hide();
    });
    // menu close
    $('#wrapper').click(function(evt) {
        var disallow = {"A": 1, "BUTTON": 1, "INPUT": 1};
        var parnetTagName = $(evt.target).parent()[0].tagName;
        if (!(disallow[evt.target.tagName] || disallow[parnetTagName])) {
            evt.preventDefault();
            $("input[data-function*='swipe']").prop('checked',false);
        }
    });
    // search
    $('#searchForm').submit(function() {
        $('#overlay, #spinner').show();
    });
    // confirm TODO NOT WORKING WHEN SWIPING
    $('a.confirm').live('click', function(evt) {
        evt.preventDefault();
        $('#confirm').load(this.href, function() {
            $('#overlay, #confirm').show();
            $('.content button').click(function() {
                $('#overlay, #spinner').show();
            });
        });
    });
    // add comment
    $('a.comment_add').live('click', function(evt) {
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
                            $('#comments').prepend(data);
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
})(jQuery);

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