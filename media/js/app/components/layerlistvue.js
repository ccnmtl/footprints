define(['jquery', 'layerVue'], function($, layer) {
    const LayerListVue = {
        props: ['value'],
        template: '#layer-list-template',
        data: function() {
            return {
                layers: [],
                selectedLayer: null
            };
        },
        components: {
            'layer-form': layer.LayerVue
        },
        methods: {
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
            if (this.value && this.value.length > 0) {
                this.layers = $.extend(true, [], this.value);
            } else {
                // create a new layer
                this.layers.push({'id': null});
                this.selectedLayer = this.layers[0];
            }
        }
    };
    return {
        LayerListVue: LayerListVue
    };
});
