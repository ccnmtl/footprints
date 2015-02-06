(function () {
    Footprint = Backbone.Model.extend({
        urlRoot: '/api/footprint/',
        url: function() {
            return this.urlRoot + this.get('id') + '/';
        },
        parse: function(response) {
           return response;
        }
    });

    FootprintDetailView = Backbone.View.extend({
        events: {
            'click a.remove-related span.glyphicon-remove': 'confirmRemoveRelated',
        },
        initialize: function(options) {
            _.bindAll(this, 'context', 'refresh', 'render',
               'confirmRemoveRelated', 'removeRelated',
                'validatePlace');

            this.baseContext = options.baseContext;
            this.template = _.template(jQuery(options.template).html());
            this.model.on('change', this.render);
            
            var html = jQuery("#place-display-template").html();
            this.place_template = _.template(html);
            
            this.mapOptions = {
                zoom: 10,
                draggable: false,
                scrollwheel: false,
                mapTypeId: google.maps.MapTypeId.ROADMAP,
                zoomControl: true,
                zoomControlOptions: {
                  style: google.maps.ZoomControlStyle.SMALL,
                  position: google.maps.ControlPosition.RIGHT_BOTTOM
                },
                mapTypeControl: false,
                streetViewControl: false
            }
        },
        context: function() {
            var ctx = this.model.toJSON();
            for (var attrname in this.baseContext) {
                ctx[attrname] = this.baseContext[attrname];
            }
            return ctx;
        },
        refresh: function(response, newValue) {
            this.model.fetch();
        },
        render: function() {
            var self = this;
            
            var markup = this.template(this.context());
            jQuery(this.el).html(markup);
            this.delegateEvents();
            
            // Initialize X-editable fields
            jQuery(this.el).find('.editable').editable({
                namedParams: true,
                success: this.refresh
            });
            
            jQuery('.editable-place').editable({
                namedParams: true,
                template: '#editable-place-form',
                onblur: 'ignore',
                validate: this.validatePlace,
                success: this.refresh
            });

            jQuery('.editable-language').editable({
                namedParams: true,
                source: this.baseContext.all_languages,
                select2: {
                    multiple: true,
                    width: 350,
                    placeholder: 'Select language(s)',
                    allowClear: true
                }
            });
            
            // Initialize display map
            this.mapElt = jQuery(this.el).find('.footprint-map')[0];
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
                        title: jQuery(this.mapElt).data('title')
                    });
                }
            }
        },
        confirmRemoveRelated: function(evt) {
            var self = this;
            var eltRemove = jQuery(evt.currentTarget).parents('a')[0];
            var eltText = jQuery(evt.currentTarget).closest('div').prev();
            var msg = "Are you sure you want to remove the connection to " + jQuery(eltText).html() + "?";

            jQuery("#confirm-modal").find('.modal-body').html(msg);

            var modal = jQuery("#confirm-modal").modal({
                'show': true,
                'backdrop': 'static',
                'keyboard': false,
            });

            jQuery('#confirm-modal .btn-confirm').one('click', function(evt) {
                self.remove(eltRemove);
            });
        },
        removeRelated: function(elt) {
            var self = this;
            var params = jQuery(elt).data('params');
            var data = jQuery.fn.editableutils.tryParseJson(params, true);

            jQuery.ajax({
                url: jQuery(elt).data('url'),
                type: "post",
                data: data,
                success: self.refresh,
                error: function() {
                    jQuery("#confirm-modal div.error").modal("An error occurred. Please try again.");
                }
            });
        },
        validatePlace: function(values) {
            if (!values.hasOwnProperty('latitude') ||
                    !values.hasOwnProperty('longitude')) {
                return "Please select a location on the map";
            } else  if (values.city.length < 1) {
                return "Please specify a city";
            } else if (values.country.length < 1) {
                return "Please specify a country";
            }
        }
    });
    
    ProgressDetailView = Backbone.View.extend({
        events: {
        },
        initialize: function(options) {
            _.bindAll(this, 'render');
            this.template = _.template(jQuery(options.template).html());
            this.model.on('change', this.render);
        },
        render: function() {
            var ctx = this.model.toJSON();

            var markup = this.template(ctx);
            jQuery(this.el).html(markup);
            this.delegateEvents();
        }
    });
    
    BookDetailView = Backbone.View.extend({
        events: {
        },
        initialize: function(options) {
            _.bindAll(this, 'render');
            this.template = _.template(jQuery(options.template).html());
            this.model.on('change', this.render);
        },
        render: function() {
            var ctx = this.model.toJSON();

            var markup = this.template(ctx);
            jQuery(this.el).html(markup);
            this.delegateEvents();
        }
    });
    
    FootprintView = Backbone.View.extend({
        events: {
        },
        initialize: function(options) {
            //_.bindAll(this, 'initialRender', 'render');
            
            // Modifying X-Editable default properties
            jQuery.fn.editable.defaults.mode = 'inline';
            jQuery.fn.editable.defaults.ajaxOptions = {
               headers: {'X-HTTP-Method-Override': 'PATCH'}
            };
            
            this.model = new window.Footprint({id: options.footprint.id});

            // create child views for each page area 
            this.detailView = new FootprintDetailView({
                el: jQuery(this.el).find(".footprint-detail"),
                model: this.model,
                baseContext: options.baseContext,
                template: options.detailTemplate
            });
            this.bookView = new BookDetailView({
                el: jQuery(this.el).find(".book-detail"),
                model: this.model,
                baseContext: options.baseContext,
                template: options.bookTemplate
            });
            this.progressView = new ProgressDetailView({
                el: jQuery(this.el).find(".progress-detail"),
                model: this.model,
                baseContext: options.baseContext,
                template: options.progressTemplate
            });
            this.model.fetch();
        }
    });
})();