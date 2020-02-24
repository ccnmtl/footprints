define(['jquery', 'layerMapVue', 'utils'], function($, layermap, utils) {
    const PathmapperMapVue = {
        props: ['value', 'layers'],
        template: '#pathmapper-map-template',
        data: function() {
            return {
                mapName: 'the-map',
                queue: null,
                map: null,
                places: {}
            };
        },
        components: {
            'layer-map': layermap.LayerMapVue
        },
        methods: {
            addMarker: function(placeId, latlng) {
                let icon = {
                    fillOpacity: .6,
                    anchor: new google.maps.Point(0,0),
                    strokeWeight: 0,
                    scale: 1,
                    fillColor: '#cb8d78',
                    path: 'M-5,0a5,5 0 1,0 10,0a5,5 0 1,0 -10,0'
                };
                let marker = new google.maps.Marker({
                    position: latlng,
                    icon: icon
                });
                marker.addListener('click', () => {
                    this.$emit('input', this.places[placeId]);
                });
                return marker;
            },
            addPoint: function(params) {
                const placeId = params.placeId;
                if (!(placeId in this.places)) {
                    // Initialize a new place
                    this.places[placeId] = {
                        id: placeId,
                        title: params.placeTitle,
                        latlng: params.latlng,
                        points: [],
                        marker: this.addMarker(placeId, params.latlng)
                    };
                }
                this.places[placeId].points.push(params.point);
            },
            updateLayer: function(layer) {
                // eslint-disable-next-line no-unused-vars
                for (let [key, place] of Object.entries(this.places)) {
                    let refs = 0;
                    for (const pt of place.points) {
                        if (layer.id === pt.layer.id) {
                            pt.layer.visible = layer.visible;
                        }
                        if (pt.layer.visible) {
                            refs++;
                        }
                    }
                    if (refs > 0) {
                        place.marker.setMap(this.map);
                    } else {
                        place.marker.setMap(null);
                    }
                }
            },
            deleteLayer: function(layer) {
                // Remove all points that are attached to the specified layer
                // If the place no longer has references, hide it & delete it
                for (let [key, place] of Object.entries(this.places)) {
                    for (let i = place.points.length - 1; i >= 0; i--) {
                        if (place.points[i].layer.id === layer.id) {
                            place.points.splice(i, 1);
                        }
                    }
                    if (place.points.length === 0) {
                        place.marker.setMap(null);
                        delete place.marker;
                        delete this.places[key];
                    }
                }
            }
        },
        created: function() {
            this.queue = new utils.AsyncQueue();
            this.bounds = null;
            this.zoom = 3;
            this.center = new google.maps.LatLng(35.408632, -41.164887);
        },
        mounted: function() {
            let elt = document.getElementById(this.mapName);
            this.map = new google.maps.Map(elt, {
                mapTypeControl: false,
                clickableIcons: false,
                zoom: this.zoom,
                streetViewControl: false,
                center: this.center,
                fullscreenControlOptions: {
                    position: google.maps.ControlPosition.RIGHT_BOTTOM,
                },
                mapTypeControlOptions: {
                    mapTypeIds: ['styled_map']
                }
            });
            this.map.mapTypes.set('styled_map', utils.lightGrayStyle);
            this.map.setMapTypeId('styled_map');
        }
    };
    return {
        PathmapperMapVue: PathmapperMapVue
    };
});