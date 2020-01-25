define(['jquery', 'layerMapVue', 'utils'], function($, layermap, utils) {
    const PathmapperMapVue = {
        props: ['layers'],
        template: '#pathmapper-map-template',
        data: function() {
            return {
                mapName: 'the-map',
                queue: null,
                map: null
            };
        },
        components: {
            'layer-map': layermap.LayerMapVue
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