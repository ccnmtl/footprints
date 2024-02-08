(function() {
    window.FootprintListView = Backbone.View.extend({
        events: {
            'click th.sortable': 'clickSortable',
            'click .btn-search-text': 'clickSearch',
            'click .toggle-range': 'clickToggleRange',
            'keypress input[name="q"]': 'enterSearch',
            'keypress .tools input.page-number': 'specifyPage',
        },
        initialize: function(options) {
            _.bindAll(
                this, 'clickSortable', 'clickSearch',
                'clickToggleRange', 'enterSearch', 'specifyPage');
            var self = this;
            this.baseUrl = options.baseUrl;
            this.selectedDirection = options.selectedDirection;
            this.selectedSort = options.selectedSort;
            this.query = options.query;

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
                direction =
                    this.selectedDirection === 'asc' ? 'desc' : 'asc';
            }

            var url = this.baseUrl + sortBy +
                '/?direction=' + direction + '&q=' + this.query;
            window.location = url;
        },
        clickSearch: function(evt) {
            var query = jQuery(this.el).find('input[name="q"]').val();
            var url = this.baseUrl + this.selectedSort +
                '/?direction=' + this.selectedDirection + '&q=' + query;
            window.location = url;
        },
        clickToggleRange: function(evt) {
            evt.preventDefault();
            if (jQuery(evt.currentTarget).hasClass('range-on')) {
                // turn off range
                jQuery(evt.currentTarget).removeClass('range-on');
                jQuery(evt.currentTarget).prev().val('0');
                jQuery(evt.currentTarget).next().hide().val('');
                jQuery(evt.currentTarget).html('add range');
            } else {
                // turn on range
                jQuery(evt.currentTarget).addClass('range-on');
                jQuery(evt.currentTarget).prev().val('1');
                jQuery(evt.currentTarget).next().show();
                jQuery(evt.currentTarget).html('to');
            }
        },
        enterSearch: function(evt) {
            var charCode = (evt.which) ? evt.which : event.keyCode;
            if (charCode === 13) {
                evt.preventDefault();
                this.clickSearch();
            }
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
