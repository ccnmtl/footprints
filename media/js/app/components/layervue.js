define(['jquery', 'selectWidget'], function($, select) {
    const LayerVue = {
        props: ['value'],
        template: '#layer-template',
        data: function() {
            return {
                layer: {
                    'id': null,
                    'title': '',
                    'work': null
                },
                total: null
            };
        },
        computed: {
            displayCriteria: function() {
                return '';
            }
        },
        components: {
            'select-widget': select.SelectWidget
        },
        methods: {
            isDirty: function() {
                return this.state !== JSON.stringify(this.layer);
            },
            isSearching: function() {
                return $('html').hasClass('busy');
            },
            setIsSearching: function() {
                $('html').addClass('busy');
                this.total = 0;
            },
            search: function() {
                if (this.isSearching() || !this.isDirty()) {
                    return;
                }

                this.setIsSearching();

                // retrieve book copies based on criteria
                $.ajax({
                    url: this.searchUrl,
                    data: this.layer,
                    type: 'post'
                }).done((results) => {
                    this.state = JSON.stringify(this.layer);
                    this.total = results.total;
                    $('html').removeClass('busy');
                });
            },
            cancel: function() {
                this.$emit('cancel');
            },
            save: function() {
                this.$emit('save', $.extend(true, {}, this.layer));
            },
            togglePane: function() {
                if ($('#container-pane').hasClass('widget-pane-expanded')) {
                    $('#container-pane').removeClass('widget-pane-expanded');
                    $('#container-pane').addClass('widget-pane-collapsed');
                } else {
                    $('#container-pane').addClass('widget-pane-expanded');
                    $('#container-pane').removeClass('widget-pane-collapsed');
                }
            }
        },
        created: function() {
            this.searchUrl = Footprints.baseUrl + 'search/book/';

            // @todo - how is this handled when the list updates the model?
            this.layer = $.extend(true, this.layer, this.value);
            this.$watch('layer', this.search, {deep: true});
        }
    };
    return {
        LayerVue: LayerVue
    };
});
