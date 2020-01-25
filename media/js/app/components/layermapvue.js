define(['jquery', 'utils'], function($, utils) {
    const LayerMapVue = {
        props: ['value'],
        data: function() {
            return {
                layer: {},
                lines: [],
                markers: []
            };
        },
        methods: {
            visibilityChanged: function(oldVal, newVal) {
                console.log(oldVal + ' ' + newVal);
            }
        },
        created: function() {
        },
        mounted: function() {
            this.layer = $.extend(true, this.layer, this.value);
            this.$watch('layer.visible', this.visibilityChanged);
        },
        render() {
            // draw the route on the map
        }
    };
    return {
        LayerMapVue: LayerMapVue
    };
});
