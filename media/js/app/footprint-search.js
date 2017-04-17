(function() {
    window.FootprintListView = Backbone.View.extend({
        events: {
            'click th.sortable': 'clickSortable',
            'click .btn-export': 'clickExport',
            'click .toggle-range': 'clickToggleRange',
            'click a.btn-paginate': 'nextOrPreviousPage',
            'keypress .tools input.page-number': 'specifyPage',
            'click #clear_primary_search': 'clickClear',
            'keypress input[name="q"]': 'enterSearch',
            'click .highlighted input:checkbox': 'applySingleFilter',
            'click .modal input:checkbox': 'matchHighlightedValue',
            'click .btn-apply-filters': 'submitForm',
            'click [type="submit"]': 'submitForm',
            'click [type="reset"]': 'resetForm',
        },
        initialize: function(options) {
            _.bindAll(this, 'clickSortable', 'clickExport', 'clickToggleRange',
                      'nextOrPreviousPage', 'specifyPage', 'enterSearch',
                      'busy', 'matchHighlightedValue',
                      'applySingleFilter', 'submitForm');

            var self = this;
            this.baseUrl = options.baseUrl;
            this.selectedDirection = options.selectedDirection;
            this.selectedSort = options.selectedSort;
            this.query = options.query;

            jQuery('body').css('cursor', 'default');

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
        busy: function(msg) {
            jQuery('body').css('cursor', 'progress');
            jQuery(this.el).find('.loading-overlay h3').html(msg);
            jQuery(this.el).find('.loading-overlay').show();
        },
        clickSortable: function(evt) {
            this.busy('Sorting');
            var direction = 'asc';
            var sortBy = jQuery(evt.currentTarget).data('sort-by');
            if (sortBy === this.selectedSort) {
                direction = this.selectedDirection === 'asc' ? 'desc' : 'asc';
            }
            jQuery(this.el).find('[name="page"]').val(1);
            jQuery(this.el).find('[name="direction"]').val(direction);
            jQuery(this.el).find('[name="sort_by"]').val(sortBy);
            jQuery(this.el).find('form').submit();
        },
        clickClear: function(evt) {
            this.busy('Clearing');
            window.location = this.baseUrl;
        },
        clickExport: function(evt) {
            var query = jQuery(this.el).find('input[name="q"]').val();
            var url = '/export/footprints/?&q=' + query;
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
                this.submitForm();
            }
        },
        nextOrPreviousPage: function(evt) {
            evt.preventDefault();
            this.busy('Loading');
            var pageNo = jQuery(evt.currentTarget).data('page-number');
            jQuery(this.el).find('[name="page"]').val(pageNo);
            jQuery(this.el).find('form').submit();
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
                    this.busy('Loading');
                    jQuery(this.el).find('[name="page"]').val(page);
                    jQuery(this.el).find('form').submit();
                }
                return false;
            }

            return charCode >= 48 && charCode <= 57;
        },
        matchHighlightedValue: function(evt) {
            // match field values
            var checked = jQuery(evt.currentTarget).is(':checked');
            var q = '.highlighted [name="' + evt.currentTarget.name + '"]' +
                '[value="' + evt.currentTarget.value + '"]';
            jQuery(this.el).find(q).prop('checked', checked);
        },
        applySingleFilter: function(evt) {
            evt.preventDefault();

            // uncheck matching fields
            if (!jQuery(evt.currentTarget).is(':checked')) {
                var q = '.modal [name="' + evt.currentTarget.name + '"]' +
                    '[value="' + evt.currentTarget.value + '"]';
                jQuery(this.el).find(q).prop('checked', false);
            }
            this.submitForm();
        },
        submitForm: function(evt) {
            this.busy('Searching');
            jQuery(this.el).find('[name="page"]').val(1);
            jQuery(this.el).find('form').submit();
        }
    });
})();
