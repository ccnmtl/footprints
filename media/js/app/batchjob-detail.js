(function() {
    window.BatchJobDetailView = Backbone.View.extend({
        events: {
            'click .batch-job-row-container table td': 'clickRecord',
            'click button.update-record': 'updateRecord',
            'click button.delete-record': 'confirmDeleteRecord',
            'click #confirm-delete-modal .btn-primary': 'deleteRecord',
            'click #process-job': 'confirmProcessJob',
            'click #confirm-process-modal .btn-primary': 'processJob'
        },
        initialize: function(options) {
            _.bindAll(this, 'clickRecord', 'updateRecord',
                      'deleteRecord', 'confirmDeleteRecord', 'checkErrorState',
                      'onKeydown', 'openRecord', 'closeRecord',
                      'confirmProcessJob', 'processJob');

            this.baseUpdateUrl = options.baseUpdateUrl;

            this.checkErrorState();

            var rowId = window.location.search.split('selected=')[1];
            this.openRecord(rowId);

            jQuery('body').click(this.closeRecord);
            jQuery('body').keydown(this.onKeydown);
        },
        checkErrorState: function() {
            if (jQuery(this.el).find('.has-error').length > 0) {
                jQuery(this.el).find('#process-job')
                    .attr('disabled', 'disabled');
                jQuery(this.el).find('.alert-danger').show();
            } else {
                jQuery(this.el).find('#process-job').removeAttr('disabled');
                jQuery(this.el).find('.alert-danger').hide();
            }
        },
        openRecord: function(dataId) {
            jQuery(this.el)
                .find('td[data-record-id="' + dataId + '"]')
                .addClass('selected');
            return false;
        },
        closeRecord: function(evt) {
            jQuery(this.el).find('td.selected').removeClass('selected');
            jQuery(this.el).find('.error-message, .success-message').hide();
        },
        onKeydown: function(evt) {
            var dataId;
            switch (evt.which) {
            case 37: // left
                dataId = jQuery(this.el).find('td.selected').first()
                    .prev().data('record-id');
                break;

            case 39: // right
                dataId = jQuery(this.el).find('td.selected').first()
                    .next().data('record-id');
                break;
            default:
                return; // exit this handler for other keys
            }
            evt.preventDefault();
            if (dataId) {
                this.closeRecord();
                this.openRecord(dataId);
            }
            return false;
        },
        clickRecord: function(evt) {
            evt.preventDefault();
            var $td = jQuery(evt.currentTarget);
            jQuery(this.el).find('td.selected').removeClass('selected');

            var dataId = $td.data('record-id');
            this.openRecord(dataId);
            return false;
        },
        updateRecord: function(evt) {
            evt.preventDefault();
            var self = this;
            var $form = jQuery(evt.currentTarget).parents('form');

            jQuery(this.el).find('td.selected input').each(function() {
                jQuery('<input />').attr('type', 'hidden')
                    .attr('name', jQuery(this).attr('name'))
                    .attr('value', jQuery(this).val())
                    .appendTo($form);
            });

            $form.submit();
            return false;
        },
        confirmDeleteRecord: function(evt) {
            evt.preventDefault();
            this.$form = jQuery(evt.currentTarget).parents('form');
            jQuery('#confirm-delete-modal').modal({
                'show': true, 'backdrop': 'static'
            });
            return false;
        },
        deleteRecord: function(evt) {
            this.$form.submit();
        },
        confirmProcessJob: function(evt) {
            evt.preventDefault();
            this.$process = jQuery(evt.currentTarget).parents('form');
            jQuery('#confirm-process-modal').modal({
                'show': true, 'backdrop': 'static'
            });
            return false;
        },
        processJob: function(evt) {
            this.$process.submit();
        }
    });
})();
