(function () {
    window.Footprint = Backbone.Model.extend({
        urlRoot: '/api/footprint/',
        url: function() {
            return this.urlRoot + this.get('id') + '/';
        }
    });

    window.BookCopy = Backbone.Model.extend({
        urlRoot: '/api/book/',
        url: function() {
            return this.urlRoot + this.get('id') + '/';
        }
    });
    
    window.FootprintBaseView = Backbone.View.extend({
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
        },
        validateIdentifier: function(values) {
            if (!values.hasOwnProperty('identifier') ||
                    values.identifer.length < 1) {
                return "Please specify an identifer";
            } else  if (!values.hasOwnProperty('identifier_type') ||
                    values.identifer.length < 1) {
                return "Please select the type of identifier";
            }
        }
    });
    
    window.FootprintDetailView = window.FootprintBaseView.extend({
        events: {
            'click a.remove-related span.glyphicon-remove': 'confirmRemoveRelated'
        },
        initialize: function(options) {
            _.bindAll(this, 'context', 'refresh', 'render',
               'confirmRemoveRelated', 'removeRelated');

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
                tpl: jQuery('#xeditable-place-form').html(),
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
                validate: this.validateActor,
                success: this.refresh,
                tpl: jQuery('#xeditable-actor-form').html() 
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

            var elt = jQuery(this.el).find('.editable-digitalobject');
            jQuery(elt).editable({
                namedParams: true,
                tpl: jQuery('#xeditable-digitalobject-form').html(), 
                source: this.baseContext.all_mediums,
                url: function() { return true; /* plupload submits */},
                success: this.refresh
            });
            
            jQuery('.carousel').carousel({
                interval: false
            });
            
            this.initializeMap();
        }
    });

    window.BookDetailView = window.FootprintBaseView.extend({
        events: {
            'click a.remove-related span.glyphicon-remove': 'confirmRemoveRelated'
        },
        initialize: function(options) {
            _.bindAll(this, 'context', 'refresh', 'render',
                'confirmRemoveRelated', 'removeRelated');
            
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
                tpl: jQuery('#xeditable-author-form').html(),
                validate: this.validateActor,
                success: this.refresh            
            });
            
            jQuery(this.el).find('.editable-publisher').editable({
                namedParams: true,
                tpl: jQuery('#xeditable-publisher-form').html(),
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
                tpl: jQuery('#xeditable-place-form').html(),
                onblur: 'ignore',
                validate: this.validatePlace,
                success: this.refresh
            });

            jQuery(this.el).find('.editable-title').editable({
                namedParams: true,
                tpl: jQuery('#xeditable-title-form').html(),
                onblur: 'ignore',
                validate: this.validate,
                success: this.refresh
            });

            jQuery(this.el).find('.editable-identifier').editable({
                namedParams: true,
                tpl: jQuery('#xeditable-identifier-form').html(),
                onblur: 'ignore',
                validate: this.validateIdentifer,
                success: this.refresh
            });

            this.initializeMap();
        }
    });
    
    window.ConnectModalView = window.FootprintBaseView.extend({
        initialize: function(options) {
            _.bindAll(this, 'initializeSelect2', 'onClear', 'onSelect');
            this.initializeSelect2();
        },
        initializeSelect2: function() {
            var self = this;
            
            // Initialize select2
            jQuery(this.el).find("input.select-object").each(function() {
                var dataUrl = jQuery(this).data('url');
                jQuery(this).select2({
                    allowClear: true,
                    minimumInputLength: 0,
                    ajax: {
                        url: dataUrl,
                        dataType: 'json',
                        delay: 250,
                        data: self.data,
                        results: self.processResults,
                        cache: true
                    },
                    escapeMarkup: function (markup) { return markup; },
                    initSelection: function(elt, callback) {
                        var id = jQuery(elt).val();
                        jQuery.ajax(dataUrl + id, {
                            dataType: "json"
                        }).done(function(data) {
                            var results = {id: data.id, text: data.description};
                            callback(results);
                        });
                    },
                    formatSelection: function(object, container, query, escMarkup) {
                        return object.text;
                    }
                });
                jQuery(this).on('change', self.onSelect);
                jQuery(this).on('select2-clearing', self.onClear);
            });
            
            this.eltWork = jQuery(this.el).find('input.select-object.work')[0];
            this.eltImprint = jQuery(this.el).find('input.select-object.imprint')[0];
            this.eltBook =  jQuery(this.el).find('input.select-object.book')[0];
            this.eltSave = jQuery(this.el).find('input.save-connection')[0];
        },
        onClear: function(evt) {
            if (jQuery(evt.currentTarget).hasClass('work')) {
                jQuery(this.eltImprint).parents('.form-group').fadeOut();
                jQuery(this.eltBook).parents('.form-group').fadeOut();
                jQuery(this.eltImprint).select2('val', '');
                jQuery(this.eltBook).select2('val', '');
            } else if (jQuery(evt.currentTarget).hasClass('imprint')) {
                jQuery(this.eltBook).parents('.form-group').fadeOut();
                jQuery(this.eltBook).select2('val', '');
            }
        },
        onSelect: function(evt, added, removed) {
            if (jQuery(evt.currentTarget).val().length > 0) {
                if (jQuery(evt.currentTarget).hasClass('work')) {
                    jQuery(this.eltImprint).parents('.form-group').fadeIn();
                    jQuery(this.eltImprint).select2('val', '');
                    jQuery(this.eltBook).parents('.form-group').fadeOut();
                    jQuery(this.eltBook).select2('val', '');
                } else if (jQuery(evt.currentTarget).hasClass('imprint')) {
                    jQuery(this.eltBook).select2('val', '');
                    jQuery(this.eltBook).parents('.form-group').fadeIn();
                }
            }
        },
        processResults: function(data, page, query) {
            var results = [];

            for (var i=0; i < data.results.length; i++) {
                if (data.results[i].description &&
                        data.results[i].description.length > 0) {
                    results.push({
                        id: data.results[i].id,
                        text: data.results[i].description
                    });
                }
            }
            return {results: results, more: data.next};
        }
    });
    
    window.ConnectRecordView = window.FootprintBaseView.extend({
        initialize: function(options) {
            _.bindAll(this, 'context', 'onClear', 'onSelect', 'refresh', 'render');
            this.baseContext = options.baseContext;
            this.template = _.template(jQuery(options.template).html());
            this.footprint = options.footprint;
            this.model.on('change', this.render);
            this.model.fetch();
        },
        render: function() {
            var self = this;

            var ctx = this.context();
            ctx.footprint_id = this.footprint.id;
            
            var markup = this.template(ctx);
            jQuery(this.el).html(markup);
            this.delegateEvents();
            
            // Initialize select2
            jQuery(this.el).find("input.select-object").each(function() {
                jQuery(this).select2({
                    allowClear: true,
                    minimumInputLength: 0,
                    ajax: {
                        url: jQuery(this).data('url'),
                        dataType: 'json',
                        delay: 250,
                        data: self.data,
                        results: self.processResults,
                        cache: true
                    },
                    escapeMarkup: function (markup) { return markup; }
                });
                jQuery(this).on('change', self.onSelect);
                jQuery(this).on('select2-clearing', self.onClear);
            });
            
            this.eltWork = jQuery(this.el).find('input.select-object.work')[0];
            this.eltImprint = jQuery(this.el).find('input.select-object.imprint')[0];
            this.eltBook =  jQuery(this.el).find('input.select-object.book')[0];
            this.eltSave = jQuery(this.el).find('input.save-connection')[0];
        },
        onClear: function(evt) {
            if (jQuery(evt.currentTarget).hasClass('work')) {
                jQuery(this.eltImprint).parents('.form-group').fadeOut();
                jQuery(this.eltBook).parents('.form-group').fadeOut();
                jQuery(this.eltImprint).select2('val', '');
                jQuery(this.eltBook).select2('val', '');
            } else if (jQuery(evt.currentTarget).hasClass('imprint')) {
                jQuery(this.eltBook).parents('.form-group').fadeOut();
                jQuery(this.eltBook).select2('val', '');
            }
        },
        onSelect: function(evt, added, removed) {
            if (jQuery(evt.currentTarget).val().length > 0) {
                jQuery(this.eltSave).fadeIn();
                if (jQuery(evt.currentTarget).hasClass('work')) {
                    jQuery(this.eltImprint).parents('.form-group').fadeIn();
                    jQuery(this.eltImprint).select2('val', '');
                    jQuery(this.eltBook).parents('.form-group').fadeOut();
                    jQuery(this.eltBook).select2('val', '');
                } else if (jQuery(evt.currentTarget).hasClass('imprint')) {
                    jQuery(this.eltBook).select2('val', '');
                    jQuery(this.eltBook).parents('.form-group').fadeIn();
                }
            }
        },
        processResults: function(data, page, query) {
            var results = [];

            for (var i=0; i < data.results.length; i++) {
                if (data.results[i].description &&
                        data.results[i].description.length > 0) {
                    results.push({
                        id: data.results[i].id,
                        text: data.results[i].description
                    });
                }
            }
            return {results: results, more: data.next};
        }
    });

    window.FootprintView = Backbone.View.extend({
        events: {
            'click .carousel img': 'maximizeCarousel',
            'click a.show-connect-book-modal': 'connectBook'
        },
        initialize: function(options) {
            _.bindAll(this, 'connectBook', 'context', 'render',
               'maximizeCarousel');

            // Modifying X-Editable default properties
            jQuery.fn.editable.defaults.mode = 'inline';
            jQuery.fn.editable.defaults.ajaxOptions = {
                headers: {'X-HTTP-Method-Override': 'PATCH'}
            };

            this.footprint = new window.Footprint({id: options.footprint.id});
            this.bookCopy = new window.BookCopy({id: options.book_copy.id});

            this.footprint.on('change', this.render);
            this.bookCopy.on('change', this.render);
            
            this.options = options;

            this.baseContext = options.baseContext;
            this.elProgress = jQuery(this.el).find(".progress-detail");
            this.template = _.template(jQuery(options.progressTemplate).html());
            
            this.carouselTemplate = _.template(jQuery(options.carouselTemplate).html());
            
            // create child views for each page area 
            this.detailView = new window.FootprintDetailView({
                el: jQuery(this.el).find(".footprint-detail"),
                model: this.footprint,
                baseContext: options.baseContext,
                template: options.detailTemplate
            });
            this.bookView = new window.BookDetailView({
                el: jQuery(this.el).find(".book-detail"),
                model: this.bookCopy,
                baseContext: options.baseContext,
                template: options.bookTemplate
            });
            this.connectView = new window.ConnectRecordView({
                el: jQuery(this.el).find(".connect-record"),
                model: this.bookCopy,
                footprint: this.footprint,
                baseContext: options.baseContext,
                template: options.connectTemplate
            });
        },
        connectBook: function() {
            var self = this;
            var imprint = this.bookCopy.get('imprint');

            var modal = jQuery(this.el).find("#connect-book-modal");
            this.connectBookView = new window.ConnectModalView({
                el: modal, model: this.bookCopy, selectedWork: imprint.work.id
            });
            var modal = jQuery("#connect-book-modal").modal({
                'backdrop': 'static', 'keyboard': false, 'show': true
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
        },
        maximizeCarousel: function(evt) {
            var self = this;
            
            var ctx = this.footprint.toJSON();
            ctx.active_id = jQuery(evt.currentTarget).data('id');
            var html = this.carouselTemplate(ctx);
            jQuery("#carousel-modal").find('.modal-body').html(html);
            
            var modal = jQuery("#carousel-modal").modal({
                'backdrop': 'static',
                'keyboard': false,
                'show': true
            });
            jQuery('#carousel-fullsize').carousel({
                interval: false
            });
        }
    });
})();