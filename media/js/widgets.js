(function() {
    /* Sidebar other-terms menu */
    jQuery('.widget-allterms-menu h4').click(function(){
        jQuery('#wrapper').slideToggle(200);
        jQuery(this).toggleClass('open');
        jQuery(this).find('.glyphicon').toggleClass('glyphicon-triangle-right glyphicon-triangle-bottom');
    });
    /* Social-media sharing */
    jQuery('.share-window').click(function(event) {
        var width  = 575,
            height = 400,
            left   = (jQuery(window).width()  - width)  / 2,
            top    = (jQuery(window).height() - height) / 2,
            url    = this.href,
            opts   = 'status=1' +
                     ',width='  + width  +
                     ',height=' + height +
                     ',top='    + top    +
                     ',left='   + left;
        window.open(url, 'sharefp', opts);
        return false;
    });
    /* Page link sharing */
    jQuery('.share-url a').popover({
        placement: 'bottom',
        html: 'true',
        title : '<button type="button" id="close" class="close" onclick="jQuery(&quot;.share-url a&quot;).popover(&quot;hide&quot;)"></button>',
        content: function () {
            return jQuery('#share-url .content').html();
        }
    });
})();
