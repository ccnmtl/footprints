(function() {
    window.FootprintListView = Backbone.View.extend({
        events: {
            'click th.sortable': 'clickSortable',
            'click .btn-export': 'clickExport',
            'click .toggle-range': 'clickToggleRange',
            'click a.btn-paginate': 'nextOrPreviousPage',
            'keypress .tools input.page-number': 'specifyPage',
            'click #clear_primary_search': 'clickClear',
            'keydown input[name="q"]': 'onKeydown',
            'keydown input[name="footprint_start_year"]': 'onKeydown',
            'keydown input[name="footprint_end_year"]': 'onKeydown',
            'keydown input[name="pub_start_year"]': 'onKeydown',
            'keydown input[name="pub_end_year"]': 'onKeydown',
            'click .highlighted input:checkbox': 'applySingleFilter',
            'click .modal input:checkbox': 'matchHighlightedValue',
            'click .btn-apply-filters': 'submitForm',
            'click [type="submit"]': 'submitForm',
            'click [type="reset"]': 'resetForm',
            'keyup input[name="footprint_start_year"]': 'updateStatus',
            'keyup input[name="footprint_end_year"]': 'updateStatus',
            'keyup input[name="pub_start_year"]': 'updateStatus',
            'keyup input[name="pub_end_year"]': 'updateStatus'
        },
        initialize: function(options) {
            _.bindAll(
                this, 'clickSortable', 'clickExport', 'clickToggleRange',
                'nextOrPreviousPage', 'specifyPage', 'onKeydown',
                'busy', 'matchHighlightedValue',
                'applySingleFilter', 'submitForm', 'clearErrors',
                'updateStatus');

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

            this.updateStatus();
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
            // eslint-disable-next-line scanjs-rules/assign_to_location
            window.location = this.baseUrl;
        },
        clickExport: function(evt) {
            // eslint-disable-next-line scanjs-rules/assign_to_location
            window.location =
                '/export/footprints/' + window.location.search;
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
            this.updateStatus(evt);
        },
        isCharacter: function(charCode) {
            return charCode === 8 ||
                (charCode >= 46 && charCode <= 90) ||
                (charCode >= 96 && charCode <= 111) ||
                charCode >= 186;
        },
        onKeydown: function(evt) {
            var charCode = (evt.which) ? evt.which : event.keyCode;
            if (charCode === 13) {
                evt.preventDefault();
                this.submitForm();
            } else if (this.isCharacter(charCode)) {
                this.clearErrors();
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
            var $form = jQuery(this.el).find('form');
            if (!$form.get(0).reportValidity()) {
                return;
            }

            this.busy('Searching');
            jQuery(this.el).find('[name="page"]').val(1);
            jQuery(this.el).find('form').submit();
        },
        clearErrors: function() {
            jQuery(this.el).find('*').removeClass('has-error');
            jQuery(this.el).find('.error-message').hide();
        },
        composeStatus: function(lbl) {
            var start = jQuery(this.el).find(
                '[name="' + lbl + '_start_year"]').val();
            var end = jQuery(this.el).find(
                '[name="' + lbl + '_end_year"]').val();
            var range = jQuery(this.el).find(
                '[name="' + lbl + '_range"]').val() === '1';

            if (range) {
                if (start && !end) {
                    return start + ' to present';
                }

                if (start && end) {
                    return start + ' to ' + end;
                }

                if (!start && end) {
                    return 'Up to ' + end;
                }
            } else if (start) {
                return start;
            }

            return 'All years';
        },
        updateStatus: function(evt) {
            var status = this.composeStatus('footprint');
            jQuery('#footprint-year-status').html(status);

            status = this.composeStatus('pub');
            jQuery('#pub-year-status').html(status);
        }
    });
})();
