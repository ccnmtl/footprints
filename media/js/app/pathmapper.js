requirejs(['./common'], function(common) {
    const libs = ['jquery', 'Vue', 'mapVue', 'layerListVue', 'utils'];
    requirejs(libs,
        function($, Vue, map, layers, utils) {
            new Vue({
                el: '#pathmapper-container',
                data: function() {
                    return {
                        collection: {
                            id: null,
                            layers: []
                        }
                    };
                },
                components: {
                    'layer-list': layers.LayerListVue,
                    'google-map': map.GoogleMapVue
                },
                methods: {
                },
                created: function() {
                    // Setup CSRF configuration and busy states
                    utils.ajaxSetup();

                    // eslint-disable-next-line
                    window.addEventListener('beforeunload', this.beforeUnload);

                    // @todo - initialize layers via template data
                    // if accessing through a saved permalink
                }
            });
        }
    );
});
