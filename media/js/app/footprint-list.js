(function() {
    window.FootprintListView = Backbone.View.extend({
        events: {
            'click th.sortable': 'clickSortable',
            'keypress .tools input': 'specifyPage'
        },
        initialize: function(options) {
            _.bindAll(this, 'clickSortable', 'specifyPage');
            var self = this;
            this.baseUrl = options.baseUrl;
            this.selectedDirection = options.selectedDirection;
            this.selectedSort = options.selectedSort;

            jQuery(this.el).find('.progress-circle').each(function() {
                var pct = parseInt(jQuery(this).data('value'), 10) / 100;
                jQuery(this).circleProgress({
                    animation: false,
                    value: pct,
                    size: 50,
                    startAngle: -Math.PI / 2,
                    emptyFill: '#D7D6D6',
                    fill: {
                        color: '#97421b'  //'#2e5367'
                    }
                });
            });

            jQuery('th.sortable').each(function() {
                var sortBy = jQuery(this).data('sort-by');
                if (sortBy === self.selectedSort) {
                    jQuery(this)
                        .addClass('selected')
                        .addClass(self.selectedDirection);
                }
            });
        },
        clickSortable: function(evt) {
            var direction = 'asc';
            var sortBy = jQuery(evt.currentTarget).data('sort-by');
            if (sortBy === this.selectedSort) {
                direction = this.selectedDirection === 'asc' ? 'desc' : 'asc';
            }

            var url = this.baseUrl + sortBy + '/?direction=' + direction;
            window.location = url;
        },
        specifyPage: function(evt) {
            var $elt = jQuery(evt.currentTarget);
            var charCode = (evt.which) ? evt.which : event.keyCode;
            var maxPage = parseInt(jQuery('.max-page').html(), 10);

            if (charCode === 13) {
                evt.preventDefault();
                var page = parseInt($elt.val(), 10);

                if (isNaN(page) || page < 1 || page > maxPage) {
                    $elt.parents('.page-count').addClass('has-error');
                } else {
                    var url = jQuery(evt.currentTarget).data('base-url');
                    window.location = url + page;
                }
                return false;
            }

            return charCode >= 48 && charCode <= 57;
        }
    });
})();
