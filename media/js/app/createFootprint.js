(function() {
    window.CreateFootprintWizard = {
        Models: {},
        Views: {},
        Router: {},
        inst: {},

        initialize: function() {
            this.inst.router = new CreateFootprintWizard.Router();
        }
    };
    
    CreateFootprintWizard.Views.TitleView = Backbone.View.extend({
        initialize: function(options) {
            _.bindAll(this, 'isValid', 'show', 'clearError', 'showError');
            this.elTab = jQuery(this.el).find("#title");
        },
        isValid: function() {
            var elt = jQuery(this.elTab).find('input[name="footprint-title"]')[0];
            return jQuery(elt).val().length > 0;
        },        
        show: function() {
            var elt = jQuery('a[href="#title"]');
            jQuery(elt).parent('li').removeClass('disabled');
            jQuery(elt).tab('show');
        },
        showError: function() {
            jQuery(this.elTab).find('.form-group.required').addClass('has-error');
            jQuery(this.el).find('ul.wizard-tabs').addClass('has-error');
        },
        clearError: function() {
            jQuery(this.elTab).find('.form-group.required').removeClass('has-error');
            jQuery(this.el).find('ul.wizard-tabs').removeClass('has-error');
        }
    });

    CreateFootprintWizard.Views.EvidenceTypeView = Backbone.View.extend({
        events: {
            'click li.disabled a': 'onClickDisabled',
            'change select[name="footprint-medium"]': 'onMediumChange' 
        },
        initialize: function(options) {
            _.bindAll(this, 'isValid', 'show', 'showError', 'clearError',
                'onClickDisabled', 'onMediumChange');
            this.elTab = jQuery(this.el).find("#evidencetype");
        },
        onClickDisabled: function(event) {
            event.preventDefault();
            return false;
        },
        onMediumChange: function(event) {
            var eltInput = jQuery(this.el).find('input[name="footprint-medium-other"]')[0];
            var medium = jQuery(this.el).find('select[name="footprint-medium"] option:selected').val();
            if (medium === "other") {
                jQuery(eltInput).show();
                jQuery(eltInput).addClass("required");
                this.clearError();
            } else {
                jQuery(eltInput).val('');
                jQuery(eltInput).hide();
                jQuery(eltInput).removeClass("required");
                this.clearError();
            }
        },
        isValid: function() {
            var medium = jQuery(this.el).find('select[name="footprint-medium"] option:selected').val();

            if (medium === "") {
                return false;
            } else if (medium === "other"){
                var val = jQuery(this.elTab).find('input[name="footprint-medium-other"]').val();
                return val.length > 0;
            } else {
                return true;
            }
        },
        show: function() {
            jQuery('a[href="#evidencetype"]').tab('show');
        },
        showError: function() {
            jQuery(this.elTab).find('.form-group.required').addClass('has-error');
            jQuery(this.el).find('ul.wizard-tabs').addClass('has-error');
        },
        clearError: function() {
            jQuery(this.elTab).find('.form-group.required').removeClass('has-error');
            jQuery(this.el).find('ul.wizard-tabs').removeClass('has-error');
        }
    });

    CreateFootprintWizard.Views.EvidenceLocationView = Backbone.View.extend({
        events: {
            'click li.disabled a': 'onClickDisabled'
        },
        initialize: function(options) {
            _.bindAll(this, 'isValid', 'show', 'showError', 'clearError',
                'onClickDisabled');
            this.elTab = jQuery(this.el).find("#evidencelocation");
        },
        onClickDisabled: function(event) {
            event.preventDefault();
            return false;
        },
        isValid: function() {
            var self = this;
            var valid = true;
            jQuery("#evidencelocation").find('textarea.required').each(function() {
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
            jQuery('a[href="#evidencelocation"]').tab('show');
        },
        showError: function() {
            jQuery(this.elTab).find('.form-group.required').addClass('has-error');
            jQuery(this.el).find('ul.wizard-tabs').addClass('has-error');
        },
        clearError: function() {
            jQuery(this.elTab).find('.form-group.required').removeClass('has-error');
            jQuery(this.el).find('ul.wizard-tabs').removeClass('has-error');
        }
    });
    
    var titleView = new CreateFootprintWizard.Views.TitleView({
        el: jQuery("#footprint-form")
    });

    var evidenceTypeView = new CreateFootprintWizard.Views.EvidenceTypeView({
        el: jQuery("#footprint-form")
    });    

    var evidenceLocationView = new CreateFootprintWizard.Views.EvidenceLocationView({
        el: jQuery("#footprint-form")
    });

    CreateFootprintWizard.Router = Backbone.Router.extend({
        routes: {
            '': 'title',
            'title': 'title',
            'evidencetype': 'evidencetype',
            'evidencelocation': 'evidencelocation'
        },
        initialize: function () {
            var self = this;
            
            jQuery(".btn-next").click(function(evt) {
                evt.preventDefault();
                if (self.currentView.isValid()) {
                    var route = jQuery(evt.currentTarget).attr('href');
                    self.navigate(route, {trigger: true});
                } else {
                    self.currentView.showError();
                }
                return false;
            });
        },
        title: function() {
            titleView.show();
            this.currentView = titleView;
        },
        evidencetype: function() {
            if (!titleView.isValid()) {
                self.navigate('title', {trigger: true});
            } else {
                evidenceTypeView.show();
                this.currentView = evidenceTypeView;
            }
        },
        evidencelocation: function() {
            if (!titleView.isValid()) {
                this.navigate('title', {trigger: true});
            } else if (!evidenceTypeView.isValid()) {
                this.navigate('evidencetype', {trigger: true});
            } else {
                evidenceLocationView.show();
                this.currentView = evidenceLocationView;
            }
        }
    });
    
    CreateFootprintWizard.initialize();
    Backbone.history.start();
})();