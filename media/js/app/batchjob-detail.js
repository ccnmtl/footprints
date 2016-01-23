(function() {
    window.BatchJobDetailView = Backbone.View.extend({
        events: {
            'click .batch-job-row-container table td': 'clickRecord'
        },
        initialize: function(options) {
            _.bindAll(this, 'clickRecord');
        },
        clickRecord: function(evt) {
            var $td = jQuery(evt.currentTarget);
            jQuery(this.el).find('td.selected').removeClass('selected');

            var dataId = $td.data('record-id');
            jQuery(this.el)
                .find('td[data-record-id="' + dataId + '"]')
                .addClass('selected');
        }
    });
})();

