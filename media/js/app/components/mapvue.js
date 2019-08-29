define(['jquery'], function($) {
    const GoogleMapVue = {
        props: [],
        template: '#google-map-template',
        data: function() {
            return {
                mapName: 'the-map'
            };
        },
        created: function() {
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
        }
    };
    return {
        GoogleMapVue: GoogleMapVue
    };
});