(function() {
    window.LocalLoginView = Backbone.View.extend({
        events: {
            'submit form#login-local': 'onLocalLogin'
        },
        initialize: function(options) {
            _.bindAll(this, 'onLocalLogin');
        },
        onLocalLogin: function(evt) {
            evt.preventDefault();

            var self = this;

            jQuery.ajax({
                type: 'POST',
                url: evt.target.action,
                data: jQuery(evt.target).serialize(),
                success: function(response) {
                    if ('error' in response) {
                        jQuery(self.el).find('div.local-login-errors').show();
                    } else {
                        // redirect to the required url
                        window.location = response.next;
                    }
                },
                error: function(xhr, ajaxOptions, thrownError) {
                    jQuery(self.el).find('div.local-login-errors').show();
                }
            });
            return false;
        }
    });
})();
