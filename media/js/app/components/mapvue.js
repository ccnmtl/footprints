const maplibs = ['jquery', 'layerMapVue', 'utils'];
define(maplibs, function($, layermap, utils) {
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
            adjustIcon: function(place) {
                const pct = (place.refs / this.events) * 75;
                const r = Math.max(3, pct);
                const d = r * 2;
                let path =
                    `M-${r},0a${r},${r} 0 1,0 ${r*2},0a${r},${r} 0 1,0 -${d},0`;
                let icon = {
                    strokeColor: '#cb8d78',
                    strokeOpacity: 1,
                    strokeWeight: 1,
                    fillColor: '#cb8d78',
                    fillOpacity: .4,
                    anchor: new google.maps.Point(0,0),
                    scale: 1,
                    path: path
                };
                if (place.marker) {
                    place.marker.setIcon(icon);
                }
            },
            addMarker: function(placeId, latlng, placeTitle) {
                let marker = new google.maps.Marker({
                    position: latlng,
                    title: placeTitle,
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
                        marker: this.addMarker(
                            placeId, params.latlng, params.placeTitle)
                    };
                }
                this.places[placeId].points.push(params.point);
            },
            updateLayer: function(layer) {
                this.events = 0;
                // eslint-disable-next-line no-unused-vars
                for (let [key, place] of Object.entries(this.places)) {
                    place.refs = 0;
                    for (const pt of place.points) {
                        if (layer.id === pt.layer.id) {
                            pt.layer.visible = layer.visible;
                        }
                        if (pt.layer.visible) {
                            place.refs++;
                        }
                    }
                    this.events += place.refs;
                    if (place.refs > 0) {
                        place.marker.setMap(this.map);
                    } else {
                        place.marker.setMap(null);
                    }
                }

                // eslint-disable-next-line no-unused-vars
                for (let [key, place] of Object.entries(this.places)) {
                    this.adjustIcon(place);
                }
            },
            deleteLayer: function(layer) {
                // Remove all points that are attached to the specified layer
                // If the place no longer has references, hide it & delete it
                // eslint-disable-next-line no-unused-vars
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
            },
            valueChanged: function() {
                if (this.activePlace) {
                    // reset icon back to the variable circle
                    this.adjustIcon(this.activePlace);
                }
                if (this.value) {
                    this.value.marker.setIcon(this.activeIcon);
                }
                this.activePlace = this.value;
            }
        },
        created: function() {
            this.queue = new utils.AsyncQueue();
            this.bounds = null;
            this.zoom = 3;
            this.center = new google.maps.LatLng(35.408632, -41.164887);
            this.activePlace = null;
            this.activeIcon = {
                url: Footprints.staticUrl +
                    'img/pathmapper-selected-location.svg',
                scaledSize: new google.maps.Size(26, 35)
            };
            this.events = 0;
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
                    mapTypeIds: ['styled_map'],
                    ignoreHidden: true
                }
            });
            this.map.mapTypes.set('styled_map', utils.lightGrayStyle);
            this.map.setMapTypeId('styled_map');

            this.$watch('value', this.valueChanged);
        }
    };
    return {
        PathmapperMapVue: PathmapperMapVue
    };
});