(function() {
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
                    this.map = new google.maps
                        .Map(this.mapElt, this.mapOptions);

                    this.marker = new google.maps.Marker({
                        position: latlng,
                        map: this.map,
                        title: jQuery(this.mapElt).data('title')
                    });
                }
            }
        },
        initializeTooltips: function() {
            jQuery(this.el).find('[data-toggle="tooltip"]').tooltip();
        },
        refresh: function(response, newValue) {
            if (!response.success) {
                return response.msg;
            } else {
                this.model.fetch();
            }
        },
        confirmRemoveRelated: function(evt) {
            var self = this;
            var eltRemove = jQuery(evt.currentTarget).parents('a')[0];
            var eltText = jQuery(evt.currentTarget).closest('div').prev();
            var msg = 'Are you sure you want to remove the connection to ' +
                jQuery(eltText).html() + '?';

            jQuery('#confirm-modal').find('.modal-body').html(msg);

            var modal = jQuery('#confirm-modal').modal({
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
                type: 'post',
                data: data,
                success: self.refresh,
                error: function() {
                    jQuery('#confirm-modal div.error')
                        .modal('An error occurred. Please try again.');
                }
            });
        },
        validate: function(values) {
            if (values.hasOwnProperty('error')) {
                return values.error;
            }
            if (values.length < 1) {
                return 'This field is required';
            }
        }
    });

    window.FootprintDetailView = window.FootprintBaseView.extend({
        events: {
            'click a.remove-related span.glyphicon-trash':
            'confirmRemoveRelated',
            'click .toggle-edit-digital-object': 'toggleEditDigitalObject'
        },
        initialize: function(options) {
            _.bindAll(this, 'context', 'refresh', 'render',
               'confirmRemoveRelated', 'removeRelated',
               'toggleEditDigitalObject');

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
                success: this.refresh
            });

            jQuery(this.el).find('.editable-required').editable({
                namedParams: true,
                success: this.refresh,
                validate: this.validate
            });

            jQuery(this.el).find('.editable-place').editable({
                namedParams: true,
                tpl: jQuery('#xeditable-place-form').html(),
                onblur: 'ignore',
                validate: this.validate,
                success: this.refresh
            });

            jQuery(this.el).find('.editable-edtf').editable({
                namedParams: true,
                tpl: jQuery('#xeditable-edtf-form').html(),
                onblur: 'ignore',
                validate: this.validate,
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
                validate: this.validate,
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

            jQuery(this.el).fadeIn(function() {
                self.initializeMap();
                self.initializeTooltips();
            });
        },
        toggleEditDigitalObject: function(evt) {
            jQuery(this.el).find('.edit-digital-object').toggle();
            return false;
        }
    });

    window.BookDetailView = window.FootprintBaseView.extend({
        events: {
            'click a.remove-related span.glyphicon-trash':
            'confirmRemoveRelated'
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
                success: this.refresh
            });
            jQuery(this.el).find('.editable-required').editable({
                namedParams: true,
                success: this.refresh,
                validate: this.validate
            });
            jQuery(this.el).find('.editable-author').editable({
                namedParams: true,
                tpl: jQuery('#xeditable-author-form').html(),
                validate: this.validate,
                success: this.refresh
            });

            jQuery(this.el).find('.editable-edtf').editable({
                namedParams: true,
                tpl: jQuery('#xeditable-edtf-form').html(),
                onblur: 'ignore',
                validate:  this.validate,
                success: this.refresh
            });

            jQuery(this.el).find('.editable-publisher').editable({
                namedParams: true,
                tpl: jQuery('#xeditable-publisher-form').html(),
                validate: this.validate,
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

            jQuery(this.el).find('.editable-place').editable({
                namedParams: true,
                tpl: jQuery('#xeditable-place-form').html(),
                onblur: 'ignore',
                validate: this.validate,
                success: this.refresh
            });

            jQuery(this.el).find('.editable-work-title').editable({
                namedParams: true,
                tpl: jQuery('#xeditable-work-title-form').html(),
                onblur: 'ignore',
                success: this.refresh
            });
            jQuery(this.el).find('.editable-imprint-title').editable({
                namedParams: true,
                tpl: jQuery('#xeditable-imprint-title-form').html(),
                onblur: 'ignore',
                success: this.refresh
            });
            jQuery(this.el).find('.editable-imprint-identifier').editable({
                namedParams: true,
                tpl: jQuery('#xeditable-imprint-identifier-form').html(),
                onblur: 'ignore',
                validate: this.validate,
                success: this.refresh
            });
            jQuery(this.el).find('.editable-work-identifier').editable({
                namedParams: true,
                tpl: jQuery('#xeditable-work-identifier-form').html(),
                onblur: 'ignore',
                validate: this.validate,
                success: this.refresh
            });

            jQuery(this.el).fadeIn(function() {
                self.initializeMap();
            });
        }
    });

    window.ConnectRecordView = window.FootprintBaseView.extend({
        events: {
            'click button.btn-next': 'next',
            'click button.btn-prev': 'navigate',
            'click button.btn-submit': 'submit'
        },
        createId: '0',
        initialize: function(options) {
            _.bindAll(this, 'context', 'initChoices', 'results',
                'onListSelect',
                'validate', 'navigate', 'reset', 'submit');

            this.baseContext = options.baseContext;
            this.initChoices();
            this.eltWork = jQuery(this.el).find('input.select-object.work')[0];
            this.eltImprint = jQuery(this.el)
                .find('input.select-object.imprint')[0];
            this.eltCopy =  jQuery(this.el).find('input.select-object.copy')[0];

            this.template = _.template(jQuery(options.template).html());

            jQuery(this.el).on('show.bs.modal', this.reset);
        },
        context: function(term, page) {
            return {
                work: jQuery(this.eltWork).val(),
                imprint: jQuery(this.eltImprint).val(),
                page: page,
                q: term
            };
        },
        initChoices: function() {
            var self = this;

            // Initialize select2
            jQuery(this.el).find('input.select-object').each(function() {
                var dataUrl = jQuery(this).data('url');
                var dataId = jQuery(this).val();
                var description = jQuery(this).prev().html();
                jQuery(this).select2({
                    width: '100%',
                    allowClear: true,
                    minimumInputLength: 0,
                    ajax: {
                        url: dataUrl,
                        dataType: 'json',
                        delay: 250,
                        data: self.context,
                        results: self.results,
                        cache: true
                    },
                    escapeMarkup: function(markup) {
                        return markup;
                    },
                    initSelection: function(elt, callback) {
                        callback({id: dataId, text: description});
                    },
                    formatSelection: function(object, container, query,
                            escMarkup) {
                        return object.text;
                    },
                    formatResult: function(object) {
                        return object.text;
                    }
                });
                jQuery(this).on('change', self.onListSelect);
                jQuery(this).on('select2-clearing', self.onListClear);
            });

        },
        onListSelect: function(evt, added, removed) {
            var value = jQuery(evt.currentTarget).val();
            if (value.length > 0) {
                if (jQuery(evt.currentTarget).hasClass('work')) {
                    // Written Work Selection

                    // clear & hide copy
                    jQuery(this.eltCopy).select2('val', '');
                    jQuery(this.eltCopy).parents('.form-group').fadeOut();

                    // clear & maybe hide imprint
                    jQuery(this.eltImprint).select2('val', '');
                    if (value === this.createId) {
                        jQuery(this.eltImprint).parents('.form-group')
                            .fadeOut();
                    } else {
                        jQuery(this.eltImprint).parents('.form-group').fadeIn();
                    }
                } else if (jQuery(evt.currentTarget).hasClass('imprint')) {
                    // Imprint Selection

                    // clear & maybe hide copy
                    jQuery(this.eltCopy).select2('val', '');
                    if (value === this.createId) {
                        jQuery(this.eltCopy).parents('.form-group').fadeOut();
                    } else {
                        jQuery(this.eltCopy).parents('.form-group').fadeIn();
                    }
                }
            }
        },
        results: function(data, page, query) {
            var items = [];

            if (page === 1) {
                items.push({
                    id: this.createId,
                    text: '<div class="separator">Create new ' +
                        query.element[0].name + '</div>'
                });
            }

            for (var i = 0; i < data.length; i++) {
                if (data[i].description &&
                        data[i].description.length > 0) {
                    items.push({
                        id: data[i].id,
                        text: data[i].description
                    });
                }
            }
            return {results: items, more: data.next !== null};
        },
        validateField: function(elt) {
            var parent = jQuery(elt).parents('.form-group');
            if (jQuery(parent).is(':visible') &&
                    jQuery(elt).val().length === 0) {
                jQuery(parent).addClass('has-error');
                return false;
            } else {
                jQuery(parent).removeClass('has-error');
                return true;
            }
        },
        next: function(evt) {
            if (this.validateField(this.eltWork) &&
                this.validateField(this.eltImprint) &&
                    this.validateField(this.eltCopy)) {

                var ctx = this.baseContext;
                ctx.work = jQuery(this.eltWork).select2('data');
                ctx.imprint = jQuery(this.eltImprint).select2('data');
                ctx.copy = jQuery(this.eltCopy).select2('data');
                ctx.createId = this.createId;
                ctx.current_book = this.model.toJSON();

                var markup = this.template(ctx);
                jQuery(this.el).find('.page2 p').html(markup);
                this.navigate();
            }
        },
        navigate: function(evt) {
            jQuery('.page1, .page2').toggle();
        },
        reset: function() {
            jQuery(this.el).find('.page1').show();
            jQuery(this.el).find('.page2').hide();
        },
        submit: function(evt) {
            var form = jQuery(this.el).find('form');
            form.submit();
        }
    });

    window.FootprintView = Backbone.View.extend({
        events: {
            'click .carousel img': 'maximizeCarousel',
            'click a.connect-records': 'connectRecords'
        },
        initialize: function(options) {
            _.bindAll(this, 'connectRecords', 'context', 'render',
                      'maximizeCarousel');

            // Modifying X-Editable default properties
            jQuery.fn.editable.defaults.mode = 'inline';

            this.footprint = new window.Footprint({id: options.footprint.id});
            this.bookCopy = new window.BookCopy({id: options.book_copy.id});

            this.footprint.on('change', this.render);
            this.bookCopy.on('change', this.render);

            this.options = options;

            this.baseContext = options.baseContext;
            this.elProgress = jQuery(this.el).find('.progress-detail');
            this.template = _.template(jQuery(options.progressTemplate).html());

            this.carouselTemplate = _.template(jQuery(options.carouselTemplate)
                                               .html());

            // create child views for each page area
            this.detailView = new window.FootprintDetailView({
                el: jQuery(this.el).find('.footprint-detail'),
                model: this.footprint,
                baseContext: options.baseContext,
                template: options.detailTemplate
            });
            this.bookView = new window.BookDetailView({
                el: jQuery(this.el).find('.book-detail'),
                model: this.bookCopy,
                baseContext: options.baseContext,
                template: options.bookTemplate
            });
            this.connectBookView = new window.ConnectRecordView({
                el: jQuery(this.el).find('#connect-records-modal'),
                model: this.bookCopy,
                baseContext: options.baseContext,
                template: options.connectTemplate
            });
        },
        connectRecords: function() {
            var modal = jQuery(this.connectBookView.el).modal({
                'backdrop': 'static', 'keyboard': false, 'show': true
            });
        },
        context: function() {
            var ctx = this.baseContext;
            ctx.footprint = this.footprint.toJSON();
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
            jQuery('#carousel-modal').find('.modal-body').html(html);

            var modal = jQuery('#carousel-modal').modal({
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
