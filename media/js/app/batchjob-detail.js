(function() {
    window.BatchJobDetailView = Backbone.View.extend({
        events: {
            'click .batch-job-row-container table td': 'clickRecord',
            'click button.update-record': 'updateRecord'
        },
        initialize: function(options) {
            _.bindAll(this, 'clickRecord', 'updateRecord', 'refreshRecord',
                'showModal', 'showSuccessModal', 'showErrorModal');

            this.baseUpdateUrl = options.baseUpdateUrl;
        },
        clickRecord: function(evt) {
            var $td = jQuery(evt.currentTarget);
            jQuery(this.el).find('td.selected').removeClass('selected');

            var dataId = $td.data('record-id');
            jQuery(this.el)
                .find('td[data-record-id="' + dataId + '"]')
                .addClass('selected');
        },
        refreshRecord: function(json, textStatus, xhr) {
            // remove all status classes
            jQuery(this.el).find('td.selected').attr('class', 'selected');

            // update each record with its new status class(es)
            for (var field in json.errors) {
                var selector = 'td.selected input[type="text"][name="' +
                    field + '"]';
                var $elt = jQuery(this.el).find(selector).parents('td');
                if (json.errors.hasOwnProperty(field)) {
                    $elt.addClass(json.errors[field]);
                }
            }

            if (jQuery(this.el).find('td.selected.has-error').length === 0) {
                this.showSuccessModal();
            } else {
                this.showErrorModal();
            }
        },
        showModal: function(id) {
            jQuery(id).modal({
                'show': true,
                'backdrop': 'static',
                'keyboard': false
            });
        },
        showErrorModal: function() {
            this.showModal('#error-modal');
        },
        showSuccessModal: function() {
            this.showModal('#success-modal');
        },
        updateRecord: function(evt) {
            var self = this;
            var $target = jQuery(evt.currentTarget);

            var recordId = $target.parents('td').data('record-id');
            var url = this.baseUpdateUrl.replace(/(\d+)/g, recordId);

            var data = {};
            jQuery(this.el).find('td.selected input').each(function() {
                data[jQuery(this).attr('name')] = jQuery(this).val();
            });

            jQuery.ajax({
                url: url,
                type: 'post',
                data: data,
                success: self.refreshRecord,
                error: self.showErrorModal
            });
        }
    });
})();
