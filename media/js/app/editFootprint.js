(function() {

    EditFootprintView = Backbone.View.extend({
        events: {
            'click a.remove-foreign-key span.glyphicon-remove': 'onConfirmRemove',
            'click .btn-cancel': 'onCancelRemove',
            'click .btn-confirm': 'onRemove',
            'mouseover li.list-group-item': 'highlightRelated',
            'mouseout li.list-group-item': 'highlightRelated'
        },
        getIconProperties: function() {
            return {
                url: "http://maps.gstatic.com/mapfiles/place_api/icons/geocode-71.png",
                size: new google.maps.Size(71, 71),
                origin: new google.maps.Point(0, 0),
                anchor: new google.maps.Point(17, 34),
                scaledSize: new google.maps.Size(25, 25)
            };
        },
        initialize: function(options) {
            _.bindAll(this, 'render',
                'onConfirmRemove', 'onCancelRemove', 'onRemove',
                'highlightRelated');
            
            this.mapOptions = {
                zoom: 10,
                mapTypeId: google.maps.MapTypeId.ROADMAP,
                zoomControl: true,
                zoomControlOptions: {
                  style: google.maps.ZoomControlStyle.SMALL,
                  position: google.maps.ControlPosition.RIGHT_BOTTOM
                },
                mapTypeControl: false,
                streetViewControl: false
            }
            this.mapElt = jQuery('.footprint-map')[0];
            if (this.mapElt) {
                var lat = jQuery(this.mapElt).data('latitude');
                var lng = jQuery(this.mapElt).data('longitude');
                if (lat && lng) {
                    var latlng = new google.maps.LatLng(lat, lng);
                    this.mapOptions.center = latlng;
                    this.map = new google.maps.Map(this.mapElt, this.mapOptions);
                    
                    this.marker = new google.maps.Marker({
                        position: latlng,
                        map: this.map,
                        icon: this.getIconProperties(),
                        title: jQuery(this.mapElt).data('title')
                    });
                }
            }

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
                template: '#xeditable-actor-form',
                validate: function(value) {
                    if (value.indexOf('name=&role') === 0) {
                        return 'Please enter the person\'s name'; 
                    }
                },
                success: function(response, newValue) {
                    response.object = {'type': 'footprint',
                                       'id': response.footprint.id}
                    var html = self.actor_template(response);
                    jQuery('div.actor-list').append(html);
                }
            });

            jQuery('.editable-author').editable({
                namedParams: true,
                template: '#xeditable-author-form',
                validate: function(value) {
                    if (value.indexOf('name=&role') === 0) {
                        return 'Please enter an author\'s name'; 
                    }
                },
                success: function(response, newValue) {
                    response.object = {'type': 'footprint',
                                       'id': response.writtenwork.id}

                    var html = self.actor_template(response);
                    jQuery('.writtenwork-author-container').append(html);
                }
            });
            
            jQuery('.editable-place').editable({
                namedParams: true,
                template: '#editable-place-form',
                onblur: 'ignore',
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
            this.eltToRemove = jQuery(evt.currentTarget).parents('a')[0];
            
            var elt = jQuery(evt.currentTarget).closest('div').prev();
            var msg = "Are you sure you want to remove the connection to " + jQuery(elt).html() + "?";

            jQuery("#confirm-modal").find('.modal-body').html(msg);

            jQuery("#confirm-modal").modal({
                'show': true,
                'backdrop': 'static',
                'keyboard': false,
            });
        },
        onCancelRemove: function(evt) {
            delete this.eltToRemove;
        },
        onRemove: function(evt) {
            var self = this;
            var params = jQuery(this.eltToRemove).data('params');
            var data = jQuery.fn.editableutils.tryParseJson(params, true);

            jQuery.ajax({
                url: jQuery(this.eltToRemove).data('url'),
                type: "post",
                data: data,
                success: function(response) {
                    var dd = jQuery(self.eltToRemove).closest('dd')[0];
                    var dt = jQuery(dd).prev();
                    
                    jQuery.each([dd, dt], function(i, elt) {
                        jQuery(elt).fadeOut(function() {
                            jQuery(elt).remove();
                        });
                    });
                    jQuery("#confirm-modal").modal("hide");
                    delete self.eltToRemove;
                },
                error: function() {
                    jQuery("#confirm-modal div.error").modal("An error occurred. Please try again.");
                }
            });
        },
        highlightRelated: function(evt) {
            var selector = jQuery(evt.currentTarget).data('related-fields');
            var elts = jQuery(selector);
            jQuery(elts).toggleClass('highlight');
        },
        unhighlightRelated: function(evt) {
            var selector = jQuery(evt.currentTarget).data('related-fields');
            var elts = jQuery(selector);
            jQuery(elts).css("background-color", "white");
        }
    });
})();