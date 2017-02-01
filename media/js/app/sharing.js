(function() {
    /* Social-media sharing */
    jQuery('body').on('click', '.share-window', function(event) {
        var width  = 575;
        var height = 400;
        var left = (jQuery(window).width()  - width)  / 2;
        var top = (jQuery(window).height() - height) / 2;
        var url = this.href;
        var opts = 'status=1,width=' + width + ',height=' + height +
            ',top=' + top + ',left=' + left;
        window.open(url, 'sharecflg', opts);
        return false;
    });
})();
