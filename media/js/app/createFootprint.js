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
    
    CreateFootprintWizard.Views.BaseView = Backbone.View.extend({
        showError: function() {
            jQuery(this.elTab).find('.form-group.required').addClass('has-error');
            jQuery(this.el).find('ul.wizard-tabs').addClass('has-error');
        },
        clearError: function() {
            jQuery(this.elTab).find('.form-group.required').removeClass('has-error');
            jQuery(this.el).find('ul.wizard-tabs').removeClass('has-error');
        },
        show: function() {
            var elt = jQuery('a[href="' + this.identifier + '"]');
            jQuery(elt).parent('li').removeClass('disabled');
            jQuery(elt).tab('show');
        }
    });
    
    CreateFootprintWizard.Views.TitleView = CreateFootprintWizard.Views.BaseView.extend({
        initialize: function(options) {
            _.bindAll(this, 'isValid', 'show', 'clearError', 'showError');
            this.identifier = "#title";
            this.elTab = jQuery(this.el).find(this.identifier);
        },
        isValid: function() {
            var elt = jQuery(this.elTab).find('input[name="footprint-title"]')[0];
            return jQuery(elt).val().length > 0;
        }
    });

    CreateFootprintWizard.Views.EvidenceTypeView = CreateFootprintWizard.Views.BaseView.extend({
        events: {
            'click li.disabled a': 'onClickDisabled',
            'change select[name="footprint-medium"]': 'onMediumChange' 
        },
        initialize: function(options) {
            _.bindAll(this, 'isValid', 'show', 'showError', 'clearError',
                'onClickDisabled', 'onMediumChange');
            this.identifier = "#evidencetype";
            this.elTab = jQuery(this.el).find(this.identifier);
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
        }
    });

    CreateFootprintWizard.Views.EvidenceLocationView = CreateFootprintWizard.Views.BaseView.extend({
        events: {
            'click li.disabled a': 'onClickDisabled'
        },
        initialize: function(options) {
            _.bindAll(this, 'isValid', 'show', 'showError', 'clearError',
                'onClickDisabled');
            this.identifier = "#evidencelocation",
            this.elTab = jQuery(this.el).find("#evidencelocation");
        },
        onClickDisabled: function(event) {
            event.preventDefault();
            return false;
        },
        isValid: function() {
            var elt = jQuery(this.elTab).find("textarea[name='footprint-provenance']")[0];
            return jQuery(elt).val().length > 0
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
            'evidencelocation': 'evidencelocation',
            'create': 'create'
        },
        initialize: function () {
            var self = this;

            jQuery(".btn-next").click(function(evt) {
                evt.preventDefault();
                if (self.currentView.isValid()) {
                    self.currentView.clearError();
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
                this.navigate('title', {trigger: true});
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
        },
        create: function() {
            return jQuery(this.currentView.el).submit();
        }
    });
    
    CreateFootprintWizard.initialize();
    Backbone.history.start();
})();