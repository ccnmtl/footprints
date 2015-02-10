(function () {
    Footprint = Backbone.Model.extend({
        urlRoot: '/api/footprint/',
        url: function() {
            return this.urlRoot + this.get('id') + '/';
        }
    });

    BookCopy = Backbone.Model.extend({
        urlRoot: '/api/book/',
        url: function() {
            return this.urlRoot + this.get('id') + '/';
        }
    });
    
    FootprintBaseView = Backbone.View.extend({
        context: function() {
            var ctx = this.model.toJSON();
            for (var attrname in this.baseContext) {
                ctx[attrname] = this.baseContext[attrname];
            }
            return ctx;
        },
        mapOptions: {
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
        },
        initializeMap: function() {
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
        refresh: function(response, newValue) {
            this.model.fetch();
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
                self.removeRelated(eltRemove);
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
        validate: function(values) {
            if (values.length < 1) {
                return 'This field is required';
            }
        },
        validateActor: function(values) {
            if (!values.hasOwnProperty('person_name') ||
                    values.person_name.length < 1) {
                return 'Please enter the person\'s name';
            } else if (!values.hasOwnProperty('role') ||
                           values.role.length < 1) {
                return 'Please select a role';
            }
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
    
    FootprintDetailView = FootprintBaseView.extend({
        events: {
            'click a.remove-related span.glyphicon-remove': 'confirmRemoveRelated'
        },
        initialize: function(options) {
            _.bindAll(this, 'context', 'refresh', 'render',
               'confirmRemoveRelated', 'removeRelated',
               'validate', 'validatePlace', 'validateActor');

            this.baseContext = options.baseContext;
            this.template = _.template(jQuery(options.template).html());
            this.model.on('change', this.render);
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
                success: this.refresh,
                validate: this.validate
            });

            jQuery(this.el).find('.editable-place').editable({
                namedParams: true,
                template: '#editable-place-form',
                onblur: 'ignore',
                validate: this.validatePlace,
                success: this.refresh
            });

            jQuery(this.el).find('.editable-language').editable({
                namedParams: true,
                source: this.baseContext.all_languages,
                select2: {
                    multiple: true,
                    width: 350,
                    placeholder: 'Select language(s)',
                    allowClear: true
                },
                success: this.refresh
            });
            
            jQuery(this.el).find('.editable-actor').editable({
                namedParams: true,
                template: '#xeditable-actor-form',
                validate: this.validateActor,
                success: this.refresh
            });
            
            jQuery(this.el).find('.editable-medium').editable({
                namedParams: true,
                source: this.baseContext.all_mediums,
                select2: {
                    width: 350,
                    placeholder: 'Select evidence type'
                },
                validate: this.validate,
                success: this.refresh
            });
            
            this.initializeMap();
        }
    });

    BookDetailView = FootprintBaseView.extend({
        events: {
            'click a.remove-related span.glyphicon-remove': 'confirmRemoveRelated',
        },
        initialize: function(options) {
            _.bindAll(this, 'context', 'refresh', 'render',
                      'confirmRemoveRelated', 'removeRelated',
                      'validate', 'validatePlace', 'validateActor');
            
            this.baseContext = options.baseContext;
            this.template = _.template(jQuery(options.template).html());
            this.model.on('change', this.render);
            this.model.fetch();
        },
        render: function() {
            var markup = this.template(this.context());
            jQuery(this.el).html(markup);
            this.delegateEvents();

            // Initialize X-editable fields
            jQuery(this.el).find('.editable').editable({
                namedParams: true,
                success: this.refresh,
                validate: this.validate
            });

            jQuery(this.el).find('.editable-author').editable({
                namedParams: true,
                template: '#xeditable-author-form',
                validate: this.validateActor,
                success: this.refresh            
            });
            
            jQuery(this.el).find('.editable-publisher').editable({
                namedParams: true,
                template: '#xeditable-publisher-form',
                validate: this.validateActor,
                success: this.refresh
            });
            
            jQuery(this.el).find('.editable-language').editable({
                namedParams: true,
                source: this.baseContext.all_languages,
                select2: {
                    multiple: true,
                    width: 350,
                    placeholder: 'Select language(s)',
                    allowClear: true
                },
                success: this.refresh,
                validate: this.validate
            });
            
            jQuery(this.el).find('.editable-place').editable({
                namedParams: true,
                template: '#editable-place-form',
                onblur: 'ignore',
                validate: this.validatePlace,
                success: this.refresh
            });
            
            
            jQuery(this.el).find('.editable-title').editable({
                namedParams: true,
                template: '#editable-title',
                onblur: 'ignore',
                validate: this.validate,
                success: this.refresh
            });

            
            this.initializeMap();

        }
    });
    
    FootprintView = Backbone.View.extend({
        initialize: function(options) {
            _.bindAll(this, 'context', 'render');
            
            // Modifying X-Editable default properties
            jQuery.fn.editable.defaults.mode = 'inline';
            jQuery.fn.editable.defaults.ajaxOptions = {
                headers: {'X-HTTP-Method-Override': 'PATCH'}
            };
            
            this.footprint = new Footprint({id: options.footprint.id});
            this.bookCopy = new BookCopy({id: options.book_copy.id});
            
            this.footprint.on('change', this.render);
            this.bookCopy.on('change', this.render);
            
            this.baseContext = options.baseContext;
            this.elProgress = jQuery(this.el).find(".progress-detail");
            this.template = _.template(jQuery(options.progressTemplate).html());
            
            // create child views for each page area 
            this.detailView = new FootprintDetailView({
                el: jQuery(this.el).find(".footprint-detail"),
                model: this.footprint,
                baseContext: options.baseContext,
                template: options.detailTemplate
            });
            this.bookView = new BookDetailView({
                el: jQuery(this.el).find(".book-detail"),
                model: this.bookCopy,
                baseContext: options.baseContext,
                template: options.bookTemplate
            });
        },
        context: function() {
            var ctx = this.baseContext;
            ctx.footprint = this.footprint.toJSON();
            ctx.book = this.bookCopy.toJSON();
            return ctx;
        },
        render: function() {
            var ctx = this.context();
            var markup = this.template(ctx);
            jQuery(this.elProgress).html(markup);
        }
    });
})();