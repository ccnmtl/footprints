define(['jquery', 'utils'], function($, utils) {
    const LayerMapVue = {
        props: ['layer', 'map', 'queue'],
        data: function() {
            return {
                lines: [],
                markers: []
            };
        },
        methods: {
            url: function(pageNumber) {
                return Footprints.baseUrl +
                    'pathmapper/route/?page=' + pageNumber;
            },
            clear: function() {
                for (let route of this.lines) {
                    route.setMap(null);
                    route = null;
                }
                this.lines = [];
                for (let marker of this.markers) {
                    marker.setMap(null);
                    marker = null;
                }
                this.markers = [];
            },
            refresh: function() {
                console.log('refresh');
                this.clear(); // clear the routes
                this.getPage(1); // get the data again
            },
            getPage: function(pageNumber) {
                const ctx = {'layer': this.layer, 'page': pageNumber};
                this.queue.add(this.getData, this.mapData, ctx);
            },
            getData: function(params) {
                const ctx = {
                    layer: JSON.stringify(params.layer)
                };
                return new Promise((resolve, reject) => {
                    $.ajax({
                        type: 'POST',
                        url: this.url(params.page),
                        dataType: 'json',
                        data: ctx,
                        success: (data) => {
                            resolve(data);
                        },
                        error: (error) => {
                            reject(error);
                        }
                    });
                });
            },
            mapData: function(data) {
                for (let bookcopy of data.results) {
                    let coords = [];
                    if (bookcopy.imprint && bookcopy.imprint.place) {
                        let latlng = {
                            lat: bookcopy.imprint.place.latitude,
                            lng: bookcopy.imprint.place.longitude,
                        };
                        coords.push(latlng);
                        let marker = this.addMarker(latlng, 'Imprint');
                        this.markers.push(marker);
                    }
                    for (let fp of bookcopy.footprints) {
                        if (fp.place) {
                            let latlng = {
                                lat: fp.place.latitude,
                                lng: fp.place.longitude,
                            };
                            coords.push(latlng);
                            let marker = this.addMarker(latlng, 'Footprint');
                            this.markers.push(marker);
                        }
                    }
                    let line = new google.maps.Polyline({
                        path: coords,
                        geodesic: true,
                        strokeColor: '#cb8d78',
                        strokeOpacity: .6,
                        strokeWeight: 1
                    });
                    this.lines.push(line);
                }
                this.visibilityChanged(this.layer.visible, false);

                const nextPage = utils.parsePageNumber(data.next);
                if (nextPage > 1) {
                    this.getPage(nextPage);
                }
            },
            addMarker: function(latlng, iconType) {
                let icon = {
                    fillOpacity: .6,
                    anchor: new google.maps.Point(0,0),
                    strokeWeight: 0,
                    scale: 1
                };
                if (iconType === 'Imprint') {
                    icon.path = 'M-5,0a5,5 0 1,0 10,0a5,5 0 1,0 -10,0';
                    icon.fillColor = '#628395';
                } else if (iconType === 'Footprint') {
                    icon.fillColor = '#cb8d78';
                    icon.path = 'M-5,0a5,5 0 1,0 10,0a5,5 0 1,0 -10,0';
                }
                return new google.maps.Marker({
                    position: latlng,
                    icon: icon
                });
            },
            visibilityChanged: function(newVal, oldVal) {
                if (oldVal === newVal) {
                    return;
                }

                console.log('visibilityChanged');
                const map = newVal ? this.map : null;
                for (let route of this.lines) {
                    route.setMap(map);
                }
                for (let marker of this.markers) {
                    marker.setMap(map);
                }
            }
        },
        beforeDestroy: function() {
            this.clear();
        },
        mounted: function() {
            this.$watch('layer.visible', this.visibilityChanged);
            this.$watch('layer.work', this.refresh);
            this.$watch('layer.imprint', this.refresh);
            this.$watch('layer.imprintLocation', this.refresh);
            this.$watch('layer.footprintLocation', this.refresh);
            this.$watch('layer.footprintStart', this.refresh);
            this.$watch('layer.footprintEnd', this.refresh);
            this.$watch('layer.pubStart', this.refresh);
            this.$watch('layer.pubEnd', this.refresh);
            this.$watch('layer.actor', this.refresh);

            this.getPage(1);
        },
        render() {
            // don't do anything
        }
    };
    return {
        LayerMapVue: LayerMapVue
    };
});
