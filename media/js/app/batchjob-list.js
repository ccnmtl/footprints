(function() {
    window.BatchJobListView = Backbone.View.extend({
        events: {
            'fileselect .btn-file :file': 'selectFile',
            'click a.delete-job': 'deleteJob'
        },
        initialize: function(options) {
            _.bindAll(this, 'selectFile', 'deleteJob');

            if (options.errors) {
                jQuery('#upload-file-modal').modal('show');
            }
            this.baseDeleteUrl = options.baseDeleteUrl;

            jQuery(document).on('change', '.btn-file :file', function() {
                var $input = jQuery(this);
                var args = [
                    $input.get(0).files ? $input.get(0).files.length : 1,
                    $input.val().replace(/\\/g, '/').replace(/.*\//, '')
                ];
                $input.trigger('fileselect', args);
            });
        },
        selectFile: function(event, numFiles, label) {
            jQuery(this.el).find('.csv-file-name').html(label);
        },
        deleteJob: function(evt) {
            var jobId = jQuery(evt.currentTarget).data('id');
            var url = this.baseDeleteUrl.replace(/(\d+)/g, jobId);
            jQuery('#confirm-modal').find('form').attr('action', url);

            jQuery('#confirm-modal').modal({
                'show': true,
                'backdrop': 'static',
                'keyboard': false
            });
        },
    });
})();
