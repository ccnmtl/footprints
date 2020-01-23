define(['jquery', 'utils'], function($, utils) {
    const GoogleMapVue = {
        props: ['value'],
        template: '#google-map-template',
        data: function() {
            return {
                mapName: 'the-map',
                routes: []
            };
        },
        methods: {
            url: function(pageNumber) {
                return Footprints.baseUrl +
                    'pathmapper/route/?page=' + pageNumber;
            },
            clearRoutes: function() {
                for (let layer of this.routes) {
                    for (let route of layer.lines) {
                        route.setMap(null);
                        route = null;
                    }
                    for (let marker of layer.markers) {
                        marker.setMap(null);
                        marker = null;
                    }
                }
                this.routes = [];
            },
            refreshRoutes: function() {
                this.clearRoutes();
                for (let layer of this.value) {
                    let idx = this.routes.push({'lines': [], 'markers': []});
                    this.q.add(this.getData, this.mapData,
                        {'layer': layer, 'layerIdx': idx - 1, 'page': 1});
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
                    map: this.map,
                    icon: icon
                });
            },
            mapData: function(data) {
                let bounds = new google.maps.LatLngBounds();
                for (let bookcopy of data.results) {
                    let coords = [];
                    if (bookcopy.imprint && bookcopy.imprint.place) {
                        let latlng = {
                            lat: bookcopy.imprint.place.latitude,
                            lng: bookcopy.imprint.place.longitude,
                        };
                        coords.push(latlng);
                        let marker = this.addMarker(latlng, 'Imprint');
                        this.routes[data.layerIdx].markers.push(marker);
                        bounds.extend(marker.position);
                    }
                    for (let fp of bookcopy.footprints) {
                        if (fp.place) {
                            let latlng = {
                                lat: fp.place.latitude,
                                lng: fp.place.longitude,
                            };
                            coords.push(latlng);
                            let marker = this.addMarker(latlng, 'Footprint');
                            this.routes[data.layerIdx].markers.push(marker);
                            bounds.extend(marker.position);
                        }
                    }
                    let path = new google.maps.Polyline({
                        path: coords,
                        geodesic: true,
                        strokeColor: '#cb8d78',
                        strokeOpacity: .6,
                        strokeWeight: 1
                    });
                    path.setMap(this.map);
                    this.routes[data.layerIdx].lines.push(path);
                    this.map.fitBounds(bounds);
                }
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
                            data.layerIdx = params.layerIdx;
                            resolve(data);
                        },
                        error: (error) => {
                            reject(error);
                        }
                    });
                });
            },
        },
        created: function() {
            this.q = new utils.AsyncQueue();
            this.bounds = null;
            this.zoom = 5;
            this.center = new google.maps.LatLng(37.0902, -95.7129);
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
                }
            });
            this.refreshRoutes();
        }
    };
    return {
        GoogleMapVue: GoogleMapVue
    };
});