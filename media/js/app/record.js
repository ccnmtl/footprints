(function() {
    window.RecordWorkspaceView = Backbone.View.extend({
        events: {
            'click .list-group-item': 'onClickModelList'
        },
        initialize: function(options) {
            _.bindAll(this, 'onClickModelList');
        },
        onClickModelList: function(evt) {
            var self = this;
            
            evt.preventDefault();
            var modelName = evt.currentTarget.hash.split("#")[1];
            
            jQuery.ajax({
                type: "GET",
                url: '/record/form/?model=' + modelName,
                success: function(response) {
                    jQuery('div.model-form').html(response);
                },                                                                                                                              
                error: function(xhr, ajaxOptions, thrownError) {
                    alert('an error occurred');
                }
            });
            return false;
        }
    });
})();