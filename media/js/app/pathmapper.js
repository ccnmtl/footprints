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
                    },
                    readSession: function() {
                        /*eslint-disable scanjs-rules/identifier_localStorage*/
                        /*eslint-disable scanjs-rules/property_localStorage*/
                        if (utils.storageAvailable('localStorage')) {
                            const str =
                                window.localStorage.getItem('pathmapper');
                            if (str && str.length > 0) {
                                this.collection.layers = JSON.parse(str);
                                return true;
                            }
                        }
                        /*eslint-enable scanjs-rules/property_localStorage*/
                        /*eslint-enable scanjs-rules/identifier_localStorage*/
                        return false;
                    },
                    saveSession: function() {
                        /*eslint-disable scanjs-rules/identifier_localStorage*/
                        /*eslint-disable scanjs-rules/property_localStorage*/
                        if (utils.storageAvailable('localStorage')) {
                            const str = JSON.stringify(this.collection.layers);
                            window.localStorage.setItem('pathmapper', str);
                        }
                        /*eslint-enable scanjs-rules/property_localStorage*/
                        /*eslint-enable scanjs-rules/identifier_localStorage*/
                    }
                },
                created: function() {
                    // Setup CSRF configuration and busy states
                    utils.ajaxSetup();

                    // eslint-disable-next-line
                    window.addEventListener('beforeunload', this.beforeUnload);

                    // @todo accessing through a permalink

                    // initialize layers via stored data
                    this.readSession();
                },
                updated: function() {
                    this.saveSession();
                }
            });
        }
    );
});
