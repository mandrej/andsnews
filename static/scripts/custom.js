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

    //DRAGGABLE IMAGE BOXES GRID http://tympanus.net/codrops/2011/10/07/draggable-image-boxes-grid/
    var $ibWrapper = $('#ib-main-wrapper'),
        Template = (function() {
            var kinetic_moving = false,                           // true if dragging the container
                current = -1,                                     // current index of the opened item
                isAnimating = false,                              // true if the item is being opened / closed
                $ibItems = $ibWrapper.find('.ib-main > article'), // items on the grid
                $ibImgItems = $ibItems.not('.ib-content'),        // image items on the grid
                imgItemsCount = $ibImgItems.length,               // total image items on the grid
                init = function() {
                    loadKinetic();                                // apply the kinetic plugin to the wrapper
                    initEvents();                                 // load some events
                },
                loadKinetic = function() {
                    setWrapperSize();
                    $ibWrapper.kinetic({
                        moved: function() {
                            kinetic_moving = true;
                        },
                        stopped: function() {
                            kinetic_moving = false;
                        }
                    });

                },
                setWrapperSize = function() {
                    var containerMargins = $('#header').outerHeight(true) + $('#footer').outerHeight(true) + parseFloat($ibItems.css('margin-top'));
                    $ibWrapper.css('height', $(window).height() - containerMargins);
                },
                initEvents = function() {
                    // open the item only if not dragging the container
                    $ibItems.bind('click.ibTemplate', function(event) {
                        if (!kinetic_moving)
                            openItem($(this));
                        return false;
                    });
                    // on window resize, set the wrapper and preview size accordingly
                    $(window).bind('resize.ibTemplate', function(event) {
                        setWrapperSize();
                        $('#ib-img-preview, #ib-content-preview').css({
                            width: $(window).width(),
                            height: $(window).height()
                        })
                    });

                },
                openItem = function($item) {
                    if (isAnimating) return false;
                    // if content item
                    if ($item.hasClass('ib-content')) {
                        isAnimating = true;
                        current = $item.index('.ib-content');
                        loadContentItem($item, function() {
                            isAnimating = false;
                        });
                    }
                    // if image item
                    else {
                        isAnimating = true;
                        current = $item.index('.ib-image');
                        loadImgPreview($item, function() {
                            isAnimating = false;
                        });
                    }
                },
                // opens one image item (fullscreen)
                loadImgPreview = function($item, callback) {
                    var largeSrc = $item.children('img').data('largesrc'),
                        description = $item.children('span').text(),
                        largeImageData = {
                            src: largeSrc,
                            description: description
                        };

                    // preload large image
                    $item.addClass('ib-loading');
                    preloadImage(largeSrc, function() {
                        $item.removeClass('ib-loading');
                        var hasImgPreview = ( $('#ib-img-preview').length > 0 );
                        if (!hasImgPreview)
                            $('#previewTmpl').tmpl(largeImageData).insertAfter($ibWrapper);
                        else
                            $('#ib-img-preview').children('img.ib-preview-img')
                                .attr('src', largeSrc)
                                .end()
                                .find('span.ib-preview-descr')
                                .text(description);

                        //get dimentions for the image, based on the windows size
                        var dim = getImageDim(largeSrc);
                        $item.removeClass('ib-img-loading');

                        //set the returned values and show/animate preview
                        $('#ib-img-preview').css({
                            width: $item.width(),
                            height: $item.height(),
                            left: $item.offset().left,
                            top: $item.offset().top
                        }).children('img.ib-preview-img').hide().css({
                            width: dim.width,
                            height: dim.height,
                            left: dim.left,
                            top: dim.top
                        }).fadeIn(400).end().show().animate({
                            width: $(window).width(),
                            left: 0
                        }, 500, 'easeOutExpo', function() {
                            $(this).animate({
                                height: $(window).height(),
                                top: 0
                            }, 400, function() {
                                var $this = $(this);
                                $this.find('span.ib-preview-descr, span.ib-close').show()
                                if (imgItemsCount > 1)
                                    $this.find('div.ib-nav').show();
                                if (callback) callback.call();
                            });
                        });

                        if (!hasImgPreview)
                            initImgPreviewEvents();
                    });
                },
                // opens one content item (fullscreen)
                loadContentItem = function($item, callback) {
                    var hasContentPreview = ($('#ib-content-preview').length > 0),
                        teaser = $item.children('div.ib-teaser').html(),
                        content = $item.children('div.ib-content-full').html(),
                        contentData = {
                            teaser: teaser,
                            content: content
                        };

                    if (!hasContentPreview)
                        $('#contentTmpl').tmpl(contentData).insertAfter($ibWrapper);

                    // set the returned values and show/animate preview
                    $('#ib-content-preview').css({
                        width: $item.width(),
                        height: $item.height(),
                        left: $item.offset().left,
                        top: $item.offset().top
                    }).show().animate({
                        width: $(window).width(),
                        left: 0
                    }, 500, 'easeOutExpo', function() {
                        $(this).animate({
                            height: $(window).height(),
                            top: 0
                        }, 400, function() {
                            var $this = $(this),
                                $teaser = $this.find('div.ib-teaser'),
                                $content = $this.find('div.ib-content-full'),
                                $close = $this.find('span.ib-close');

                            if (hasContentPreview) {
                                $teaser.html(teaser)
                                $content.html(content)
                            }

                            $teaser.show();
                            $content.show();
                            $close.show();

                            if (callback) callback.call();
                        });

                    });

                    if (!hasContentPreview)
                        initContentPreviewEvents();

                },
                // preloads an image
                preloadImage = function(src, callback) {
                    $('<img/>').load(function() {
                        if (callback) callback.call();
                    }).attr('src', src);
                },
                // load the events for the image preview : navigation ,close button, and window resize
                initImgPreviewEvents = function() {
                    var $preview = $('#ib-img-preview');
                    $preview.find('span.ib-nav-prev').bind('click.ibTemplate', function(event) {
                        navigate('prev');
                    }).end().find('span.ib-nav-next').bind('click.ibTemplate', function(event) {
                        navigate('next');
                    }).end().find('span.ib-close').bind('click.ibTemplate', function(event) {
                        closeImgPreview();
                    });

                    //resizing the window resizes the preview image
                    $(window).bind('resize.ibTemplate', function(event) {
                        var $largeImg = $preview.children('img.ib-preview-img'),
                            dim = getImageDim($largeImg.attr('src'));

                        $largeImg.css({
                            width: dim.width,
                            height: dim.height,
                            left: dim.left,
                            top: dim.top
                        })
                    });

                },
                // load the events for the content preview : close button
                initContentPreviewEvents = function() {
                    $('#ib-content-preview').find('span.ib-close').bind('click.ibTemplate', function(event) {
                        closeContentPreview();
                    });
                },
                // navigate the image items in fullscreen mode
                navigate = function(dir) {
                    if (isAnimating) return false;
                    isAnimating = true;

                    var $preview = $('#ib-img-preview'),
                        $loading = $('#spinner');

                    $loading.show();
                    if (dir === 'next') {
                        (current === imgItemsCount - 1) ? current = 0 : ++current;
                    }
                    else if (dir === 'prev') {
                        (current === 0) ? current = imgItemsCount - 1 : --current;
                    }

                    var $item = $ibImgItems.eq(current),
                        largeSrc = $item.children('img').data('largesrc'),
                        description = $item.children('span').text();

                    preloadImage(largeSrc, function() {
                        $loading.hide();

                        //get dimentions for the image, based on the windows size
                        var dim = getImageDim(largeSrc);

                        $preview.children('img.ib-preview-img')
                            .attr('src', largeSrc)
                            .css({
                                width: dim.width,
                                height: dim.height,
                                left: dim.left,
                                top: dim.top
                            })
                            .end()
                            .find('span.ib-preview-descr')
                            .text(description);

                        $ibWrapper.scrollTop($item.offset().top)
                            .scrollLeft($item.offset().left);

                        isAnimating = false;

                    });

                },
                // closes the fullscreen image item
                closeImgPreview = function() {
                    if (isAnimating) return false;
                    isAnimating = true;
                    var $item = $ibImgItems.eq(current);
                    $('#ib-img-preview').find('span.ib-preview-descr, div.ib-nav, span.ib-close')
                        .hide()
                        .end()
                        .animate({
                            height: $item.height(),
                            top: $item.offset().top
                        }, 500, 'easeOutExpo', function() {
                            $(this).animate({
                                width: $item.width(),
                                left: $item.offset().left
                            }, 400, function() {
                                $(this).fadeOut(function() {
                                    isAnimating = false;
                                });
                            });
                        });
                },
                // closes the fullscreen content item
                closeContentPreview = function() {
                    if (isAnimating) return false;
                    isAnimating = true;

                    var $item = $ibItems.not('.ib-image').eq(current);

                    $('#ib-content-preview').find('div.ib-teaser, div.ib-content-full, span.ib-close')
                        .hide()
                        .end()
                        .animate({
                            height: $item.height(),
                            top: $item.offset().top
                        }, 500, 'easeOutExpo', function() {
                            $(this).animate({
                                width: $item.width(),
                                left: $item.offset().left
                            }, 400, function() {
                                $(this).fadeOut(function() {
                                    isAnimating = false;
                                });
                            });
                        });
                },
                // get the size of one image to make it full size and centered
                getImageDim = function(src) {
                    var img = new Image();
                    img.src = src;

                    var w_w = $(window).width(),
                        w_h = $(window).height(),
                        r_w = w_h / w_w,
                        i_w = img.width,
                        i_h = img.height,
                        r_i = i_h / i_w,
                        new_w, new_h,
                        new_left, new_top;

                    if (r_w > r_i) {
                        new_h = w_h;
                        new_w = w_h / r_i;
                    } else {
                        new_h = w_w * r_i;
                        new_w = w_w;
                    }

                    return {
                        width: new_w,
                        height: new_h,
                        left: (w_w - new_w) / 2,
                        top: (w_h - new_h) / 2
                    };
                };
            return {init: init};
        })();

    Template.init();
});