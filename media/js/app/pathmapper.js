requirejs(['./common'], function(common) {
    const libs = ['jquery', 'Vue', 'mapVue', 'layerListVue',
        'tableVue', 'utils', 'timelineVue'];
    requirejs(libs,
        function($, Vue, map, layers, table, utils, timeline) {
            new Vue({
                el: '#pathmapper-container',
                data: function() {
                    return {
                        collection: {
                            id: null,
                            layers: []
                        },
                        selectedLocation: null,
                        showMap: true,
                        shareUrl: Footprints.baseUrl + 'pathmapper/'
                    };
                },
                components: {
                    'layer-list': layers.LayerListVue,
                    'pathmapper-map': map.PathmapperMapVue,
                    'pathmapper-table': table.PathmapperTableVue,
                    'pathmapper-timeline': timeline.PathmapperTimelineVue
                },
                methods: {
                    clearLocation: function() {
                        this.selectedLocation = null;
                    },
                    switchToTable: function() {
                        this.showMap = false;
                    },
                    switchToMap: function() {
                        this.showMap = true;
                    },
                    readSession: function() {
                        if (utils.storageAvailable('localStorage')) {
                            const str =
                                window.localStorage.getItem('pathmapper');
                            if (str && str.length > 0) {
                                this.collection.layers = JSON.parse(str);
                                return true;
                            }
                        }
                        return false;
                    },
                    saveSession: function() {
                        if (utils.storageAvailable('localStorage')) {
                            const str = JSON.stringify(this.collection.layers);
                            window.localStorage.setItem('pathmapper', str);
                        }
                    },
                    shareResults: function() {
                        if ($('#share-panel-focus')
                            .hasClass('share-panel-collapsed')) {
                            $('#share-panel-focus')
                                .removeClass('share-panel-collapsed');
                            $('#share-panel-focus')
                                .addClass('share-panel-expanded');
                        } else {
                            $('#share-panel-focus')
                                .removeClass('share-panel-expanded');
                            $('#share-panel-focus')
                                .addClass('share-panel-collapsed');
                        }
                        $('#shareCopyLink').focus().select();
                    },
                    closeShareResults: function() {
                        $('#share-panel-focus')
                            .removeClass('share-panel-expanded');
                        $('#share-panel-focus')
                            .addClass('share-panel-collapsed');
                    },
                    readShareData: function() {
                        const j = document.getElementById('layers').textContent;
                        const layers = JSON.parse(j);
                        if (layers.length < 1) {
                            return false;
                        }
                        // clear out the query parameters
                        window.history.replaceState(
                            {}, [], Footprints.baseUrl + 'pathmapper/');
                        this.collection.layers = layers;
                        return true;
                    },
                    updateShareUrl: function() {
                        let url = Footprints.baseUrl + 'pathmapper/?';
                        let visibleLayers =
                            this.collection.layers.filter(l => l.visible);

                        url += 'n=' + visibleLayers.length + '&';
                        visibleLayers.forEach((layer, idx) => {
                            url += 'l' + idx + '=';
                            for (let [key, value] of Object.entries(layer)) {
                                if (key === 'narrative') {
                                    continue;
                                }
                                if (key !== 'id') {
                                    key = utils.abbreviate(key);
                                }
                                url += key + ':' + (value || '') + ',';
                            }
                            url += '&';
                        });
                        this.shareUrl = url;
                    }
                },
                created: function() {
                    // Setup CSRF configuration and busy states
                    utils.ajaxSetup();

                    // eslint-disable-next-line
                    window.addEventListener('beforeunload', this.beforeUnload);

                    // Accessing through a permalink?
                    if (!this.readShareData()) {
                        // otherwise, check to see if there is a saved
                        // session. initialize layers via stored data
                        this.readSession();
                    }
                },
                updated: function() {
                    this.saveSession();
                    this.updateShareUrl();
                }
            });
        }
    );
});
