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
            'keyup input[name="pub_end_year"]': 'updateStatus',
            'click a.search-precision': 'changePrecision',
            'click .toggle-view': 'clickToggleView',
            'click .gallery-img-container': 'clickGalleryImage',
            'click .close-overlay': 'clickCloseOverlay',
        },
        initialize: function(options) {
            _.bindAll(
                this, 'clickSortable', 'clickExport', 'clickToggleRange',
                'nextOrPreviousPage', 'specifyPage', 'onKeydown',
                'busy', 'matchHighlightedValue',
                'applySingleFilter', 'submitForm', 'clearErrors',
                'updateStatus', 'changePrecision', 'clickToggleView',
                'clickGalleryImage', 'clickCloseOverlay');

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
            window.location = this.baseUrl;
        },
        clickExport: function(evt) {
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
        clickToggleView: function(evt) {
            evt.preventDefault();
            if (jQuery(evt.currentTarget).hasClass('disabled')) {
                return;
            } else if(jQuery(evt.currentTarget).hasClass('list')) {
                jQuery('input[name="gallery_view"]').removeProp('checked');
                this.submitForm();
            } else {
                jQuery(evt.currentTarget).children('input').first().prop(
                    'checked', true);
                this.submitForm();
            }
        },
        clickGalleryImage: function(evt) {
            evt.preventDefault();
            // Get image
            jQuery('img[class="image-display"]').prop(
                'src', jQuery(evt.currentTarget).find('img')[0].src);
            // Get indices
            let metaData = jQuery(
                evt.currentTarget.nextElementSibling).find('p');
            // Extract metadata
            let dataDisplay = jQuery('ul[title="metadata"]').find('li');
            dataDisplay[0].innerHTML = metaData[0].innerHTML;
            dataDisplay[1].innerHTML = metaData[1].innerHTML;
            dataDisplay[2].innerHTML = metaData[2].innerHTML;
            if (metaData.length > 4) {
                let owners = '<span><strong>---Roles---</strong></span>';
                for (let i=3; i<metaData.length-1; i++) {
                    owners += metaData[i].outerHTML;
                }
                dataDisplay[3].innerHTML = owners;
            } else {
                dataDisplay[3].innerHTML = '';
            }
            // Reveal display
            let display = jQuery('div[class="gallery-display"]');
            display.show();
            display.css('display', 'flex');
            // Store tab location
            this.selected = evt.currentTarget;
            //Set focus
            jQuery('ul[title="metadata"]').focus();
        },
        clickCloseOverlay: function(evt) {
            evt.preventDefault();
            // Set focus to last selected item
            this.selected.focus();
            // Hide view
            let display = jQuery(this.el.getElementsByClassName(
                'gallery-display')[0]);
            display.hide();
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
        changePrecision: function(evt) {
            var $elt = jQuery(evt.currentTarget);
            var $btn = $elt.parents('.dropdown-menu').prev();
            $btn.find('.search-precision-label').html($elt.html());

            jQuery(this.el)
                .find('[name="precision"]')
                .val($elt.data('precision'));
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
