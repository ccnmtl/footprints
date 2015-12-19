(function() {
    window.ImprintView = Backbone.View.extend({
        events: {
            'click .panel-heading': 'onTogglePanel'
        },
        initialize: function(options) {
            _.bindAll(this, 'initializeMap', 'attachInfoWindow',
                      'initializeTooltips', 'onTogglePanel', 'resize');

            var copyId = null;
            var copyTemplate = _.template(jQuery(options.template).html());
            jQuery(this.el).find('.list-group-item').each(function() {
                var id = jQuery(this).data('book-copy');
                if (copyId !== id) {
                    copyId = id;
                    var markup = copyTemplate({'copyId': copyId});
                    jQuery(this).before(markup);
                }
            });

            this.initializeMap();
            jQuery(window).on('resize', this.resize);
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
        getVisibleContentHeight: function() {
            // the more standards compliant browsers
            // (mozilla/netscape/opera/IE7)
            // use window.innerWidth and window.innerHeight
            var viewportheight = window.innerHeight;

            var offset = 50 + jQuery('.header').outerHeight() +
                jQuery('.banner-pl').outerHeight() +
                jQuery('.writtenwork h1').outerHeight();

            return viewportheight - offset;
        },
        resize: function() {
            var height = this.getVisibleContentHeight();

            jQuery(this.el).css('min-height', height);

            var $elt = jQuery(this.el).find('.imprint-map-container').first();
            $elt.css('height', height);
            $elt.css('width', $elt.parent().width());

            $elt = jQuery(this.el).find('.imprint-map').first();
            $elt.css('height', height);
            $elt.css('width', $elt.parent().width());

            height -= jQuery(this.el).find('.writtenwork-detail')
                                     .outerHeight();
        },
        initializeMap: function() {
            var self = this;
            // compile lat/longs
            var markers = jQuery(this.el).find('.map-marker');
            if (markers.length > 0) {
                var infowindow = new google.maps.InfoWindow({
                    content: '',
                    size: new google.maps.Size(50,50)
                });

                this.resize();
                var mapElt = jQuery(this.el).find('.imprint-map')[0];

                var map = new google.maps.Map(mapElt, this.mapOptions);
                var boundsChanged = google.maps.event
                    .addListener(map, 'bounds_changed', function(event) {
                    if (map.getZoom() > 10) {
                        map.setZoom(10);
                    }
                    google.maps.event.removeListener(boundsChanged);
                });

                var bounds = new google.maps.LatLngBounds();

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
                }

                map.fitBounds(bounds);
                jQuery(mapElt).show();

                jQuery('.imprint-map-container').affix({
                    offset: {
                        top: jQuery('.imprint-map-container').offset().top,
                        bottom: jQuery('.foot').outerHeight() + 30
                    }
                });
            }
        },
        initializeTooltips: function() {
            jQuery(this.el).find('[data-toggle="tooltip"]').tooltip();
        },
        onTogglePanel: function(evt) {
            evt.preventDefault();
            jQuery(evt.currentTarget).parent().find(
                '.panel-collapse').collapse('toggle');
        }
    });
})();
