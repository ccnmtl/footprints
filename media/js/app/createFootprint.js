(function() {
    window.CreateFootprintWizard = {
        Models: {},
        Views: {},
        Router: {},
        Math: {},
        inst: {},

        initialize: function() {
            this.inst.router = new CreateFootprintWizard.Router();
        }
    };

    CreateFootprintWizard.Views.EvidenceView = Backbone.View.extend({
        events: {
            'click li.disabled a': 'onClickDisabled'
        },
        initialize: function(options) {
            _.bindAll(this, 'onClickDisabled');
        },
        onClickDisabled: function(event) {
            event.preventDefault();
            return false;
        },
        validates: function() {
            var self = this;
            var valid = true;
            jQuery("#evidence").find('textarea').each(function() {
                var group = jQuery(this).parents('.form-group');
                if (jQuery(this).val().length < 1) {
                    jQuery(group).addClass('has-error');
                    valid = false;
                } else {
                    jQuery(group).removeClass('has-error');
                }
            });
            
            if (valid) {
                jQuery(this.el).find('ul.wizard-tabs').removeClass('has-error');
            } else {
                jQuery(this.el).find('ul.wizard-tabs').addClass('has-error');
            }
            return valid;
        },
        show: function() {
            jQuery('a[href="#evidence"]').tab('show');
        }
    });
    
    CreateFootprintWizard.Views.TitleView = Backbone.View.extend({
        events: {

        },
        initialize: function(options) {
            
        },
        validates: function() {
            var elt = jQuery('input[name="footprint-title"]')[0];
            var group = jQuery(elt).parents('.form-group');
            var valid = jQuery(elt).val().length > 0;

            if (valid) {
                jQuery(group).removeClass('has-error');
                jQuery(this.el).find('ul.wizard-tabs').removeClass('has-error');
            } else {
                jQuery(group).addClass('has-error');
                jQuery(this.el).find('ul.wizard-tabs').addClass('has-error');
            }
            return valid;
        },        
        show: function() {
            var elt = jQuery('a[href="#title"]');
            jQuery(elt).parent('li').removeClass('disabled');
            jQuery(elt).tab('show');
        }
    });
    
    CreateFootprintWizard.Views.AuthorView = Backbone.View.extend({
        events: {
            'click .author-delete': 'onRemoveAuthor',
            'keypress input[name="footprint-author"]': 'onNewAuthor'
        },
        initialize: function(options) {
            _.bindAll(this, 'dataSource', 'onNewAuthor', 'onRemoveAuthor',
                      'selectAuthor', 'show');

            var html = jQuery('#author-list-template').html()
            this.authorTemplate = _.template(html);

            this.elInput = jQuery(this.el).find("input[name='footprint-author']")[0];
            this.elAuthors = jQuery(this.el).find("ul.selected-authors")[0];
           
            jQuery(this.elInput).autocomplete({
                source: this.dataSource,
                select: this.selectAuthor,
                minLength: 2,
                open: function() {
                    jQuery(this).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
                },
                close: function() {
                    jQuery(this).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
                }
            });
        },
        validates: function() {
            return true;
        },
        show: function() {
            var elt = jQuery('a[href="#author"]');
            jQuery(elt).parent('li').removeClass('disabled');
            jQuery(elt).tab('show');
        },
        dataSource: function(request, response) {
            jQuery.ajax({
                url: "/api/name/",
                dataType: "jsonp",
                data: {
                    q: request.term
                },
                success: function(data) {
                    var names = [];
                    for (var i=0; i < data.length; i++) {
                        names.push({
                            label: data[i].name,
                            object_id: data[i].object_id
                        });
                    }
                    response(names);
                }
            });
        },
        selectAuthor: function(event, ui) {
            event.preventDefault();
            var markup = this.authorTemplate({'ui': ui.item});
            jQuery(this.elAuthors).append(markup);
            jQuery(this.elInput).val('');
            return false;
        },
        onNewAuthor: function(event, ui) {
            if (event.keyCode == 13) {
                event.preventDefault();
                var author = jQuery(event.currentTarget).val().trim();
                if (author.length > 0) {
                    var markup = this.authorTemplate({'ui': {label: author}});
                    jQuery(this.elAuthors).append(markup);
                    jQuery(this.elInput).val('');
                }
                return false;
            }
            return true;
        },
        onRemoveAuthor: function(evt) {
            jQuery(evt.currentTarget).parent('li').remove();
        }
    });
    
    var evidenceView = new CreateFootprintWizard.Views.EvidenceView({
        el: jQuery("#footprint-form")
    });    

    var titleView = new CreateFootprintWizard.Views.TitleView({
        el: jQuery("#footprint-form")
    });

    var authorView = new CreateFootprintWizard.Views.AuthorView({
        el: jQuery("#footprint-form")
    });

    CreateFootprintWizard.Router = Backbone.Router.extend({
        routes: {
            '': 'evidence',
            'evidence': 'evidence',
            'title': 'title',
            'author': 'author',
            'help': 'help'
        },
        initialize: function () {
            var self = this;
            
            jQuery(".btn-next").click(function(evt) {
                evt.preventDefault();
                if (self.currentView.validates()) {
                    var route = jQuery(evt.currentTarget).attr('href');
                    self.navigate(route, {trigger: true});
                }
                return false;
            });
        },
        evidence: function() {
            evidenceView.show();
            this.currentView = evidenceView;
        },
        title: function() {
            titleView.show();
            this.currentView = titleView;
        },
        author: function() {
           authorView.show();
           this.currentView = authorView;
        },
        help: function() {
            alert('help');
        }
    });
    
    CreateFootprintWizard.initialize();
    Backbone.history.start();
})();