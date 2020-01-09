define(['jquery'], function($) {
    const GoogleMapVue = {
        props: [],
        template: '#google-map-template',
        data: function() {
            return {
                mapName: 'the-map'
            };
        },
        methods: {
            updateLayers: function() {
                console.log('updateLayers');
            }
        },
        created: function() {
            this.bounds = null;
            this.zoom = 5;
            this.center = new google.maps.LatLng(37.0902, -95.7129);
            this.$watch('value', this.updateLayers);
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
        },
        updated: function() {
            // @todo - map the paths
            console.log('Layers were updated');
        }
    };
    return {
        GoogleMapVue: GoogleMapVue
    };
});