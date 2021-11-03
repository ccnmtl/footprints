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
            /* eslint-disable security/detect-object-injection */
            for (var attrname in this.baseContext) {
                ctx[attrname] = this.baseContext[attrname];
            }
            /* eslint-enable security/detect-object-injection */
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
            streetViewControl: false,
            fullscreenControl: false,
            controlSize: 28
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
            if (Object.prototype.hasOwnProperty.call(response, 'success')
                && !response.success) {
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

            jQuery('#confirm-modal').modal({
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
            if (Object.prototype.hasOwnProperty.call(values, 'error')) {
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
            _.bindAll(
                this, 'context', 'refresh', 'render',
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
                validate: this.validate,
                tpl: jQuery('#xeditable-digitalobject-form').html(),
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
                validate: this.validate,
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
                success: this.refresh,
                error: function(msg) {
                    if (Object.prototype.hasOwnProperty.call(
                        msg, 'responseJSON')) {
                        return msg.responseJSON.title[0];
                    } else {
                        return msg;
                    }
                }
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
                'onListSelect', 'validate', 'navigate', 'reset', 'submit');

            this.baseContext = options.baseContext;
            this.initChoices();
            this.$eltWork = jQuery(this.el)
                .find('select.select-object.work').first();
            this.$eltImprint = jQuery(this.el)
                .find('select.select-object.imprint').first().fadeOut();
            this.$eltCopy = jQuery(this.el)
                .find('select.select-object.copy').first().fadeOut();

            this.template = _.template(jQuery(options.template).html());

            jQuery(this.el).on('show.bs.modal', this.reset);
        },
        context: function(params) {
            return {
                work: this.$eltWork.val(),
                imprint: this.$eltImprint.val(),
                page: params.page || 1,
                q: params.term
            };
        },
        initChoices: function() {
            var self = this;

            // Initialize select2
            jQuery(this.el).find('select.select-object').each(function() {
                const dataUrl = jQuery(this).data('url');
                const placeholder = jQuery(this).data('placeholder');
                jQuery(this).select2({
                    width: '100%',
                    minimumInputLength: 0,
                    placeholder: {
                        id: '-1', // the value of the option
                        text: placeholder
                    },
                    ajax: {
                        url: dataUrl,
                        dataType: 'json',
                        delay: 250,
                        data: self.context,
                        processResults: self.results,
                        cache: true
                    },
                    escapeMarkup: function(markup) {
                        return markup;
                    },
                    templateResult: function(result) {
                        if (result.loading) {
                            return 'Searching...';
                        }
                        return result.html;
                    },
                    templateSelection: function(data) {
                        return data.text;
                    },
                });
                jQuery(this).on('change', self.onListSelect);
                jQuery(this).on('select2-clearing', self.onListClear);
            });
        },
        onListSelect: function(evt, added, removed) {
            this.removeErrors();
            var value = jQuery(evt.currentTarget).val();
            if (value && value.length > 0) {
                if (jQuery(evt.currentTarget).hasClass('work')) {
                    // Written Work Selection

                    // clear & hide copy
                    this.$eltCopy.val(-1).trigger('change');
                    this.$eltCopy.parents('.form-group').fadeOut();

                    // clear & maybe hide imprint
                    this.$eltImprint.val(-1).trigger('change');
                    if (value === this.createId) {
                        this.$eltImprint.parents('.form-group')
                            .fadeOut();
                    } else {
                        this.$eltImprint.parents('.form-group').fadeIn();
                    }
                } else if (jQuery(evt.currentTarget).hasClass('imprint')) {
                    // Imprint Selection

                    // clear & maybe hide copy
                    this.$eltCopy.val(-1).trigger('change');
                    if (value === this.createId) {
                        this.$eltCopy.parents('.form-group').fadeOut();
                    } else {
                        this.$eltCopy.parents('.form-group').fadeIn();
                    }
                }
            }
        },
        results: function(data, params) {
            let items = [];
            let page = params.page || 1;

            if (page === 1) {
                items.push({
                    id: this.createId,
                    text: 'Create New',
                    html: '<div class="separator"><strong>' +
                        'Create New Record</strong></div>'
                });
            }

            for (let item of data.results) {
                if (item.description &&
                        item.description.length > 0) {
                    items.push({
                        id: item.id,
                        text: item.title || item.identifier,
                        html: item.description
                    });
                }
            }
            return {
                results: items,
                pagination: {
                    more: Object.prototype.hasOwnProperty.call(data, 'next') &&
                        data.next !== null
                }
            };
        },
        hasValue: function() {
            if (!jQuery(this).next().is(':visible')) {
                return true;
            }
            var value = jQuery(this).val();
            return value && value.length > 0;
        },
        validateFields: function(parent) {
            this.removeErrors();
            jQuery(parent).find('.required')
                .not(this.hasValue)
                .parents('.form-group')
                .addClass('has-error');
            return jQuery('.form-group.has-error').length === 0;
        },
        next: function(evt) {
            var parent = jQuery(this.el).find('.page1');
            if (this.validateFields(parent)) {
                var ctx = this.baseContext;
                ctx.work = this.$eltWork.select2('data')[0];
                ctx.imprint = this.$eltImprint.select2('data')[0];
                ctx.copy = this.$eltCopy.select2('data')[0];
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
        removeErrors: function(parent) {
            jQuery(this.el).find('.form-group.has-error')
                .removeClass('has-error');
        },
        reset: function() {
            jQuery(this.el).find('.page1').show();
            jQuery(this.el).find('.page2').hide();
        },
        submit: function(evt) {
            var parent = jQuery(this.el).find('.page2');
            if (this.validateFields(parent)) {
                var form = jQuery(this.el).find('form');
                form.submit();
            }
        }
    });

    window.FootprintView = Backbone.View.extend({
        events: {
            'click .carousel img': 'maximizeCarousel',
            'click a.connect-records': 'connectRecords',
            'click .list-group-item': 'clickRelatedFootprint'
        },
        initialize: function(options) {
            _.bindAll(
                this, 'connectRecords', 'context', 'render',
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
            this.progressTemplate =
                _.template(jQuery(options.progressTemplate).html());

            this.elRelated = jQuery(this.el).find('.footprint-evidence');
            this.relatedTemplate =
                _.template(jQuery(options.relatedTemplate).html());

            this.carouselTemplate =
                _.template(jQuery(options.carouselTemplate).html());

            this.elRecordkeeping =
                jQuery(this.el).find('.recordkeeping');
            this.recordkeepingTemplate =
                _.template(jQuery(options.recordkeepingTemplate).html());

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
            this.addRelatedView = new window.ConnectRecordView({
                el: jQuery(this.el).find('#add-related-footprint'),
                model: this.bookCopy,
                baseContext: options.baseContext,
                template: options.connectTemplate
            });
        },
        clickRelatedFootprint: function(evt) {
            location.href =
                jQuery(evt.currentTarget).children('a').first().attr('href');
            return false;
        },
        connectRecords: function(evt) {
            evt.preventDefault();
            jQuery(this.connectBookView.el).modal({
                'backdrop': 'static', 'keyboard': false, 'show': true
            });
            return false;
        },
        context: function() {
            var ctx = this.baseContext;
            ctx.footprint = this.footprint.toJSON();
            return ctx;
        },
        render: function() {
            var ctx = this.context();
            var markup = this.progressTemplate(ctx);
            jQuery(this.elProgress).html(markup);

            markup = this.relatedTemplate(ctx);
            jQuery(this.elRelated).html(markup);

            markup = this.recordkeepingTemplate(ctx);
            jQuery(this.elRecordkeeping).html(markup);
            jQuery(this.elRecordkeeping).show();
        },
        maximizeCarousel: function(evt) {
            if (jQuery('#carousel-modal').is(':visible')) {
                return false;
            }
            var ctx = this.footprint.toJSON();
            ctx.active_id = jQuery(evt.currentTarget).data('id');
            var html = this.carouselTemplate(ctx);
            jQuery('#carousel-modal').find('.modal-body').html(html);

            jQuery('#carousel-modal').modal({
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
