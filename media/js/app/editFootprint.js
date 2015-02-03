(function() {

    EditFootprintView = Backbone.View.extend({
        events: {
            'click a.remove-foreign-key span.glyphicon-remove': 'onConfirmRemove',
            'click .btn-confirm': 'remove'
        },
        initialize: function(options) {
            _.bindAll(this, 'render',
                    'onConfirmRemove', 'remove');
            
            var html = jQuery("#actor-display-template").html();
            this.actor_template = _.template(html);
            
            var html = jQuery("#place-display-template").html();
            this.place_template = _.template(html);
                
            var self = this;

            // Modifying X-Editable default properties
            jQuery.fn.editable.defaults.mode = 'inline';
            jQuery.fn.editable.defaults.ajaxOptions = {
               headers: {'X-HTTP-Method-Override': 'PATCH'}
            };

            // Initializing X-editable fields
            jQuery('.editable').editable({
                namedParams: true
            });

            jQuery('.editable-actor').editable({
                namedParams: true,
                template: '#editable-actor-form',
                validate: function(value) {
                    if (value.indexOf('name=&role') === 0) {
                        return 'Please enter the person\'s name'; 
                    }
                },
                success: function(response, newValue) {
                    var html = self.actor_template(response);
                    jQuery('div.actor-list').append(html);
                }
            });
            
            jQuery('.editable-place').editable({
                namedParams: true,
                template: '#editable-place-form',
                validate: function(values) {
                    if (!values.hasOwnProperty('latitude') ||
                            !values.hasOwnProperty('longitude')) {
                        return "Please select a location on the map";
                    } else  if (values.city.length < 1) {
                        return "Please specify a city";
                    } else if (values.country.length < 1) {
                        return "Please specify a country";
                    }
                },
                success: function(response, newValue) {
                    var html = self.place_template(response);
                    jQuery('.footprint-place').html(html);
                    jQuery('.footprint-place').fadeIn();
                }
            });            

            jQuery('.editable-language').editable({
                namedParams: true,
                source: options.languages,
                select2: {
                    multiple: true,
                    width: 350,
                    placeholder: 'Select language(s)',
                    allowClear: true
                }
            });
            
            jQuery('.editable-medium').editable({
                namedParams: true,
                source: options.mediums,
                select2: {
                    width: 350,
                    placeholder: 'Select evidence type'
                }
            });            

            jQuery('.do-you-know').on('save', function(e, params) {
                var dataName = jQuery(e.currentTarget).data('name');
                var elts = jQuery('[data-attribute-name="' + dataName + '"]');
                jQuery(elts).each(function(index) {
                    if (jQuery(this).is('.editable-date')) {
                        jQuery(this).editable('setValue', params.newValue, true);
                        jQuery(this).attr('data-pk', params.response.associated_date);
                        var url = jQuery(this).attr('data-url');
                        jQuery(this).attr('data-url', url + params.response.associated_date + '/');
                        jQuery(this).editable('option', 'pk', params.response.associated_date);
                    } else if (jQuery(this).is('.editable, .editable-language')) {
                        jQuery(this).editable('setValue', params.newValue, true);
                    }
                    jQuery(this).parents('div.description-list').show();
                });
                if (!jQuery(e.currentTarget).hasClass('editable-actor')) {
                    jQuery(e.currentTarget).parents('li').fadeOut(function() {
                        jQuery(this).remove();
                    });
                }
            });
        },
        onConfirmRemove: function(evt) {
            this.eltToRemove = evt.currentTarget;
            this.eltToRemove = jQuery(evt.currentTarget).prevAll('span')[0];
            var display = jQuery(this.eltToRemove).html();
            var msg = "Are you sure you want to remove " + display + "?";

            jQuery("#confirm-modal").find('.modal-body').html(msg);

            jQuery("#confirm-modal").modal({
                'show': true,
                'backdrop': 'static',
                'keyboard': false
            });
        },
        onCancelRemove: function(evt) {
            delete this.eltToRemove;
        },
        onRemove: function(evt) {
            var params = jQuery(this.eltToRemove).data('params');
            var data = jQuery.fn.editableutils.tryParseJson(params, true);

            jQuery.ajax({
                url: jQuery(this.eltToRemove).data('url'),
                type: "post",
                data: data,
                success: function(response) {
                    var dt = jQuery(this.eltToRemove).prevAll('dt')[0];
                    var dd = jQuery(this.eltToRemove).prevAll('dd')[0];
                    fadeOut(function() {
                        jQuery(this).remove(); 
                    });
                    jQuery("#confirm-modal").modal("hide");
                },
                error: function() {
                    jQuery("#confirm-modal div.error").modal("An error occurred. Please try again.");
                }
            });
        }
    });
})();