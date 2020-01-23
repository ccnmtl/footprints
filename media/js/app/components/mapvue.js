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
            mapData: function(data) {
                // @todo - map the data here.
                console.log(data);
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
            updateRoutes: function() {
                for (let layer of this.value) {
                    const ctx = {'layer': layer, 'page': 1};
                    this.q.add(this.getData, this.mapData, ctx);
                }
            }
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
            this.updateRoutes();
        }
    };
    return {
        GoogleMapVue: GoogleMapVue
    };
});