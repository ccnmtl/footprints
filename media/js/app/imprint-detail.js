/* global OverlappingMarkerSpiderfier */
(function() {
    window.ImprintView = Backbone.View.extend({
        events: {
            'click a.book-copy-toggle': 'onClickBookCopy',
            'click .list-group-item': 'onClickFootprint',
            'click .imprint-list-item h4': 'onClickImprint',
            'click .share-link': 'onShareLink'
        },
        initialize: function(options) {
            _.bindAll(this, 'initializeMap', 'attachInfoWindow',
                      'initializeTooltips', 'onClickBookCopy', 'resize',
                      'onClickFootprint', 'onClickImprint',
                      'updateMarkerIcons', 'syncMap',
                      'addHistory', 'popState', 'onShareLink');

            this.urlBase = options.urlBase;

            this.markerIcon = this.iconWithColor('ffa881');
            this.spiderIcon = this.iconWithColor('ff6e2d');

            this.mapLoaded = false;

            this.initializeMap();
            jQuery(window).on('resize', this.resize);
            jQuery(window).on('popstate', this.popState);

            this.setState(options.state.imprint, options.state.copy,
                options.state.footprint);
            this.shareTemplate =
                _.template(jQuery(options.shareTemplate).html());
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
        updateMarkerIcons: function() {
            for (var key in this.markers) {
                if (this.markers.hasOwnProperty(key)) {
                    this.markers[key].marker.setIcon(this.markerIcon);
                }
            }

            var markers = this.oms.markersNearAnyOtherMarker();
            for (var i = 0; i < markers.length; i++) {
                markers[i].setIcon(this.spiderIcon);
            }
        },
        scrollToItem: function($elt) {
            var eltTop = $elt.offset().top - 150;
            var mapTop = jQuery('.foot').offset().top -
                jQuery('.imprint-map-container').height() - 40;

            jQuery('html, body').animate({
                scrollTop: Math.min(eltTop, mapTop) + 'px'
            }, 900);
        },
        attachInfoWindow: function(infowindow, map, marker, content) {
            var self = this;

            this.oms.addListener('click', function(marker, event) {
                infowindow.setContent(marker.desc);
                infowindow.open(map, marker);

                jQuery(self.el).find('.active').removeClass('active');

                var $elt = jQuery('[data-id="' + marker.dataId + '"]').first();
                if (marker.dataId.startsWith('footprint')) {
                    $elt.addClass('active');
                } else {
                    $elt.parent().addClass('active');
                }
            });

            this.oms.addListener('spiderfy', function(markers) {
                for (var i = 0; i < markers.length; i ++) {
                    markers[i].setIcon(self.markerIcon);
                }

                infowindow.close();
            });

            this.oms.addListener('unspiderfy', function(markers) {
                for (var i = 0; i < markers.length; i ++) {
                    markers[i].setIcon(self.spiderIcon);
                }
            });

            google.maps.event.addListener(map, 'click', function() {
                infowindow.close();
            });

            google.maps.event.addListener(map, 'idle', function() {
                if (!self.mapLoaded) {
                    self.updateMarkerIcons();
                    self.mapLoaded = true;
                }
            });

            google.maps.event.addListener(map, 'zoom_changed', function() {
                if (self.mapLoaded) {
                    self.updateMarkerIcons();
                }
            });

            // *
            // http://en.marnoto.com/2014/09/
            //     5-formas-de-personalizar-infowindow.html
            // START INFOWINDOW CUSTOMIZE.
            // The google.maps.event.addListener() event expects
            // the creation of the infowindow HTML structure 'domready'
            // and before the opening of the infowindow,
            // defined styles are applied.
            // *
            google.maps.event.addListener(infowindow, 'domready', function() {
                // Reference to the DIV that wraps the bottom of infowindow
                var $iwOuter = jQuery('.gm-style-iw');

                /* Since this div is in a position prior to .gm-div style-iw.
                 * We use jQuery and create a iwBackground variable,
                 * and took advantage of the existing reference .gm-style-iw
                 * for the previous div with .prev().
                */
                var iwBackground = $iwOuter.prev();

                // Removes background shadow DIV
                iwBackground.children(':nth-child(2)')
                    .css({'display': 'none'});

                // Removes white background DIV
                iwBackground.children(':nth-child(4)')
                    .css({'display': 'none'});

                // Changes the desired tail shadow color.
                iwBackground.children(':nth-child(3)')
                    .find('div').children()
                    .css({'z-index': '1'});

                // Reference to the div that groups the close button elements.
                var iwCloseBtn = $iwOuter.next();
                iwCloseBtn.css({top: '22px', right: '57px'});
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
        iconWithColor: function(color) {
            return 'https://chart.googleapis.com/chart?' +
            'chst=d_map_pin_letter&chld=%E2%80%A2|' + color;
        },
        initializeMap: function() {
            var self = this;

            // compile lat/longs
            var markers = jQuery(this.el).find('.map-marker');
            if (markers.length > 0) {
                this.infowindow = new google.maps.InfoWindow({
                    maxWidth: 350
                });

                this.resize();
                var mapElt = jQuery(this.el).find('.imprint-map')[0];

                this.map = new google.maps.Map(mapElt, this.mapOptions);
                var boundsChanged = google.maps.event
                    .addListener(this.map, 'bounds_changed', function(event) {
                    if (self.map.getZoom() > 10) {
                        self.map.setZoom(10);
                    }
                    google.maps.event.removeListener(boundsChanged);
                });

                this.bounds = new google.maps.LatLngBounds();
                this.oms = new OverlappingMarkerSpiderfier(this.map, {
                    keepSpiderfied: true,
                    markersWontMove: true,
                    markersWontHide: true});

                this.markers = {};
                for (var i = 0; i < markers.length; i++) {
                    var id = jQuery(markers[i]).data('related');
                    var lat = jQuery(markers[i]).data('latitude');
                    var lng = jQuery(markers[i]).data('longitude');
                    var title = jQuery(markers[i]).data('title');
                    var latlng = new google.maps.LatLng(lat, lng);
                    var content = jQuery(markers[i]).html();

                    var marker = new google.maps.Marker({
                        position: latlng,
                        map: this.map,
                        icon: this.markerIcon,
                        desc: content,
                        dataId: id
                    });
                    this.bounds.extend(latlng);
                    this.oms.addMarker(marker);
                    this.markers[id] = {'marker': marker, 'content': content};
                }

                this.attachInfoWindow(this.infowindow, this.map);

                this.map.fitBounds(this.bounds);
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
        onClickImprint: function(evt) {
            this.infowindow.close();
            jQuery(this.el).find('.active').removeClass('active');
            this.syncMap(jQuery(evt.currentTarget).data('map-id'));

            jQuery(evt.currentTarget)
                .parents('.imprint-list-item')
                .addClass('active');
            this.addHistory(jQuery(evt.currentTarget));
        },
        onClickBookCopy: function(evt) {
            jQuery(this.el).find('.active').removeClass('active');
            this.infowindow.close();
            this.map.fitBounds(this.bounds);

            // opening
            jQuery(evt.currentTarget).parent().addClass('active');
            this.addHistory(jQuery(evt.currentTarget));
        },
        onClickFootprint: function(evt) {
            this.infowindow.close();
            jQuery(this.el).find('.active').removeClass('active');
            jQuery(evt.currentTarget).addClass('active');

            var id = jQuery(evt.currentTarget).data('map-id');
            this.syncMap(id);
            this.addHistory(jQuery(evt.currentTarget));
        },
        openBookCopy: function(copyId) {
            var $elt = jQuery('.book-copy-container a[data-copy-id="' +
                    copyId + '"]');
            $elt.removeClass('collapsed');

            var $parent = $elt.parent();
            $elt = $parent.find('.footprint-container');
            $elt.addClass('in');
            $elt.prop('style').removeProperty('height');
            return $parent;
        },
        syncMap: function(id) {
            if (id in this.markers) {
                var marker = this.markers[id].marker;
                this.map.setCenter(marker.getPosition());
                this.map.setZoom(8);

                this.infowindow.close();
                this.infowindow.setContent(this.markers[id].content);
                this.infowindow.open(this.map, marker);
            } else {
                this.map.fitBounds(this.bounds);
            }
        },
        inView: function($elt) {
            var rect = $elt.get(0).getBoundingClientRect();

            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight ||
                                document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth ||
                               document.documentElement.clientWidth)
            );
        },
        addHistory: function($elt) {
            if (window.history.pushState) {
                var state = {
                    imprint: $elt.data('imprint-id'),
                    copy: $elt.data('copy-id'),
                    footprint: $elt.data('footprint-id')
                };

                var url = this.urlBase + state.imprint + '/';
                if (state.copy) {
                    url += state.copy + '/';
                }
                if (state.footprint) {
                    url += state.footprint + '/';
                }
                window.history.pushState(state, '', url);
            }
        },
        popState: function(evt) {
            this.infowindow.close();
            jQuery(this.el).find('.active').removeClass('active');
            if (!evt.originalEvent.state) {
                return;
            }

            var fpId = evt.originalEvent.state.footprint;
            var copyId = evt.originalEvent.state.copy;
            var imprintId = evt.originalEvent.state.imprint;
            this.setState(imprintId, copyId, fpId);
        },
        setState: function(imprintId, copyId, footprintId) {
            var $elt;
            if (footprintId) {
                this.openBookCopy(copyId);

                $elt = jQuery('.list-group-item[data-footprint-id="' +
                    footprintId + '"]');
                $elt.addClass('active');
                this.syncMap($elt.data('map-id'));
            } else if (copyId) {
                $elt = this.openBookCopy(copyId);
                $elt.addClass('active');
                this.map.fitBounds(this.bounds);
            } else if (imprintId) {
                // mark imprint as active
                $elt = jQuery('h4[data-imprint-id="' + imprintId + '"]');
                $elt.parents('.imprint-list-item').addClass('active');
                this.syncMap($elt.data('map-id'));
            }
            if ($elt && !this.inView($elt)) {
                // is $elt in view?
                this.scrollToItem($elt);
            }
        },
        onShareLink: function(evt) {
            var $elt = jQuery(evt.currentTarget);
            var $modal = jQuery('#share-dialog');

            var markup = this.shareTemplate({
                type: $elt.attr('data-type'),
                title: $elt.attr('data-title'),
                link: $elt.attr('href'),
                permalink: encodeURIComponent($elt.attr('href'))
            });
            $modal.find('.modal-content').html(markup);
            $modal.modal('show');
            return false;
        }
    });
})();
