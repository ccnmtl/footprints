(function() {
    window.ImprintView = Backbone.View.extend({
        events: {},
        initialize: function(options) {
            _.bindAll(this, 'initializeMap', 'attachInfoWindow',
                      'initializeTooltips');

            var self = this;
            jQuery(this.el).find('.imprint-list-item').each(function() {
                self.initializeMap(this);
            });
        },

        mapOptions: {
            zoom: 10,
            draggable: true,
            scrollwheel: false,
            navigationControl: false,
            mapTypeControl: false,
            scaleControl: false,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            zoomControl: true,
            zoomControlOptions: {
                style: google.maps.ZoomControlStyle.SMALL,
                position: google.maps.ControlPosition.RIGHT_BOTTOM
            },
            streetViewControl: false
        },
        attachInfoWindow: function(infowindow, map, marker, content) {
            var self = this;
            google.maps.event.addListener(marker, 'click', function() {
                infowindow.setContent(content);
                infowindow.open(map, marker);
            });
        },
        initializeMap: function(elt) {
            var self = this;
            // compile lat/longs
            var markers = jQuery(elt).find('.map-marker');
            if (markers.length > 0) {
                var infowindow = new google.maps.InfoWindow({
                    content: '',
                    size: new google.maps.Size(50,50)
                });

                var mapElt = jQuery(elt).find('.imprint-map')[0];
                var map = new google.maps.Map(mapElt, this.mapOptions);
                var boundsChanged = google.maps.event
                    .addListener(map, 'bounds_changed', function(event) {
                    if (map.getZoom() > 10) {
                        map.setZoom(10);
                    }
                    google.maps.event.removeListener(boundsChanged);
                });

                var bounds = new google.maps.LatLngBounds();
                var clusterer = new MarkerClusterer(
                    map, [], {gridSize: 10, maxZoom: 15});

                for (var i = 0; i < markers.length; i++) {
                    var lat = jQuery(markers[i]).data('latitude');
                    var lng = jQuery(markers[i]).data('longitude');
                    var title = jQuery(markers[i]).data('title');
                    var latlng = new google.maps.LatLng(lat, lng);
                    var content = jQuery(markers[i]).html();

                    var marker = new google.maps.Marker({
                        position: latlng,
                        map: map,
                        title: title
                    });
                    this.attachInfoWindow(infowindow, map, marker, content);
                    bounds.extend(latlng);
                    clusterer.addMarker(marker);
                }

                map.fitBounds(bounds);
                jQuery(mapElt).show();
            }
        },
        initializeTooltips: function() {
            jQuery(this.el).find('[data-toggle="tooltip"]').tooltip();
        },
    });
})();
