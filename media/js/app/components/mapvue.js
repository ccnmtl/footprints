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
            orderOfMagnitude: function(n) {
                const x = Math.floor(Math.log(n) / Math.LN10);
                // smallest marker is of 3 radius
                return Math.pow(4, x + 1);
            },
            adjustIcon: function(place) {
                const r = this.orderOfMagnitude(place.refs);
                const d = r * 2;
                let icon = L.divIcon({
                    className: 'pathmapper-marker',
                    html: `<div class="pathmapper-marker-circle"></div>`,
                    iconSize: [d, d],
                    iconAnchor: [r, r]
                });
                if (place.marker) {
                    place.marker.setIcon(icon);
                }
            },
            addMarker: function(placeId, latlng, placeTitle) {
                let marker = L.marker(latlng, {title: placeTitle});
                marker.on('click', () => {
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
                    if (place.refs > 0) {
                        place.marker.addTo(this.map);
                    } else {
                        place.marker.remove();
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
                for (let [key, place] of Object.entries(this.places)) {
                    for (let i = place.points.length - 1; i >= 0; i--) {
                        if (place.points[i].layer.id === layer.id) {
                            place.points.splice(i, 1);
                        }
                    }
                    if (place.points.length === 0) {
                        if (this.map.hasLayer(place.marker)) {
                            this.map.removeLayer(place.marker);
                        }
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
            this.center = [35.408632, -41.164887];
            this.activePlace = null;
            this.activeIcon = L.divIcon({
                className: 'pathmapper-active-marker',
                html: '<img src="' + Footprints.staticUrl +
                    'img/pathmapper-selected-location.svg"' +
                    'style="width:26px;height:35px;">',
                iconAnchor: [13, 35]
            });
        },
        mounted: function() {
            let elt = document.getElementById(this.mapName);
            this.map = L.map(elt, {
                zoomControl: false,
                zoom: this.zoom,
                center: this.center,
                attributionControl: false
            });

            // Add the zoom control to the bottom right
            L.control.zoom({
                position: 'bottomright'
            }).addTo(this.map);

            L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png', {
                maxZoom: 20,
                attribution: '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            }).addTo(this.map);

            this.$watch('value', this.valueChanged);
        }
    };
    return {
        PathmapperMapVue: PathmapperMapVue
    };
});