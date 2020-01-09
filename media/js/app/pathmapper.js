requirejs(['./common'], function(common) {
    const libs = ['jquery', 'Vue', 'mapVue', 'layerListVue',
        'tableVue', 'utils'];
    requirejs(libs,
        function($, Vue, map, layers, table, utils) {
            new Vue({
                el: '#pathmapper-container',
                data: function() {
                    return {
                        collection: {
                            id: null,
                            layers: []
                        },
                        showMap: true
                    };
                },
                components: {
                    'layer-list': layers.LayerListVue,
                    'google-map': map.GoogleMapVue,
                    'pathmapper-table': table.PathmapperTableVue
                },
                methods: {
                    switchToTable: function() {
                        this.showMap = false;
                    },
                    switchToMap: function() {
                        this.showMap = true;
                    }
                },
                created: function() {
                    // Setup CSRF configuration and busy states
                    utils.ajaxSetup();

                    // eslint-disable-next-line
                    window.addEventListener('beforeunload', this.beforeUnload);

                    // @todo - initialize layers via stored data
                    // if accessing through a saved permalink
                }
            });
        }
    );
});
