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
            createLayer: function() {
                this.selectedLayer = {};
                this.selectedLayerIdx = null;
            },
            editLayer: function(evt) {
                const idx = $(evt.currentTarget).data('idx');
                this.selectedLayer = $.extend(true, {}, this.layers[idx]);
                this.selectedLayerIdx = idx;
            },
            deleteLayer: function(evt) {
                const idx = $(evt.currentTarget).data('idx');
                this.layers.splice(idx, 1);
            },
            cancelLayer: function() {
                this.selectedLayer = null;
            },
            saveLayer: function(layer) {
                if (!this.selectedLayerIdx) {
                    this.layers.push(layer);
                } else {
                    this.layers[this.selectedLayerIdx] =
                        $.extend(true, {}, layer);
                }
                this.selectedLayer = null;
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
            if (this.value && this.value.length > 0) {
                this.layers = $.extend(true, [], this.value);
            } else {
                this.createLayer();
            }
        }
    };
    return {
        LayerListVue: LayerListVue
    };
});
