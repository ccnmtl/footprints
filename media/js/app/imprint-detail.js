/* global OverlappingMarkerSpiderfier */

(function() {
    window.ImprintView = Backbone.View.extend({
        events: {
            'click a.book-copy-toggle': 'onClickBookCopy',
            'click .list-group-item': 'onClickFootprint',
            'click .imprint-list-item h4': 'onClickImprint',
            'click .writtenwork-title': 'onClickWork',
            'click .share-link': 'onShareLink'
        },
        initialize: function(options) {
            _.bindAll(this, 'initializeMap', 'attachInfoWindow', 'resize',
                'onClickBookCopy', 'onClickFootprint', 'onClickImprint',
                'onClickWork', 'updateMarkerIcons', 'syncMap',
                'onShareLink', 'clearState', 'setState',
                'addHistory', 'popHistory');

            this.urlBase = options.urlBase;

            this.footprintIcon = this.iconWithColor('ffa881');
            this.imprintIcon = this.iconWithColor('5e98b7');
            this.spiderIcon = this.iconWithColor('ff6e2d', true);

            this.shareTemplate =
                _.template(jQuery(options.shareTemplate).html());

            this.mapLoaded = false;

            jQuery(window).on('resize', this.resize);
            jQuery(window).on('popstate', this.popHistory);

            this.initializeMap(options);
            jQuery(this.el).find('[data-toggle="tooltip"]').tooltip();
        },
        mapOptions: {
            zoom: 10,
            maxZoom: 10,
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
                if (Object.prototype.hasOwnProperty.call(this.markers, key)) {
                    var icon = this.getIcon(this.markers[key].marker.dataId);
                    this.markers[key].marker.setIcon(icon);
                }
            }

            var markers = this.spiderfier.markersNearAnyOtherMarker();
            markers.forEach((m) => {
                m.setIcon(this.spiderIcon);
            });
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

            this.spiderfier.addListener('click', function(marker, event) {
                infowindow.setContent(marker.desc);
                infowindow.open(map, marker);

                var q = '[data-map-id="' + marker.dataId + '"]';
                var $elt = self.$el.find(q).first();
                jQuery(self.el).find('.infocus').removeClass('infocus');
                self.setState(
                    $elt.data('imprint-id'),
                    $elt.data('copy-id'),
                    $elt.data('footprint-id'),
                    false /* sync map */);
            });

            this.spiderfier.addListener('spiderfy', function(markers) {
                markers.forEach(function(m) {
                    m.setIcon(self.getIcon(m.dataId));
                });

                infowindow.close();
            });

            this.spiderfier.addListener('unspiderfy', function(markers) {
                markers.forEach(function(m) {
                    m.setIcon(self.spiderIcon);
                });
            });

            google.maps.event.addListener(map, 'click', function() {
                infowindow.close();
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
            var $elt = jQuery(this.el).find('.imprint-map-container').first();
            $elt.css('height', height);
            $elt.css('width', $elt.parent().width());

            $elt = jQuery(this.el).find('.imprint-map').first();
            $elt.css('height', height - 10);
        },
        getIcon: function(dataId) {
            return dataId.indexOf('footprint') > -1 ?
                this.footprintIcon : this.imprintIcon;
        },
        iconWithColor: function(color, multiple) {
            var c = multiple ? '%2B' : '%E2%80%A2';
            return 'https://chart.googleapis.com/chart?' +
            'chst=d_map_pin_letter&chld=' + c + '|' + color;
        },
        initializeMap: function(options) {
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

                this.bounds = new google.maps.LatLngBounds();
                this.spiderfier = new OverlappingMarkerSpiderfier(this.map, {
                    keepSpiderfied: true,
                    markersWontMove: true,
                    markersWontHide: false});

                this.markers = {};
                for (var i=0; i < markers.length; i++) {
                    var m = markers[i];
                    var id = jQuery(m).data('related');
                    var lat = jQuery(m).data('latitude');
                    var lng = jQuery(m).data('longitude');
                    var latlng = new google.maps.LatLng(lat, lng);

                    var content = jQuery(m).html();

                    var marker = new google.maps.Marker({
                        position: latlng,
                        map: this.map,
                        icon: this.getIcon(id),
                        desc: content,
                        dataId: id
                    });
                    this.bounds.extend(latlng);

                    this.markers[id] = {'marker': marker, 'content': content};
                }

                this.map.fitBounds(this.bounds);
                this.attachInfoWindow(this.infowindow, this.map);

                google.maps.event.addListener(this.map, 'idle', function() {
                    if (!self.mapLoaded) {
                        self.mapLoaded = true;
                        self.projection = self.map.getProjection();
                        self.setState(
                            options.state.imprint,
                            options.state.copy,
                            options.state.footprint,
                            true);
                        self.updateMarkerIcons();
                    }
                });

                google.maps.event.addListener(this.map, 'zoom_changed',
                    function() {
                        if (self.mapLoaded) {
                            self.updateMarkerIcons();
                        }
                    }
                );

                google.maps.event.addListener(
                    this.map,
                    'bounds_changed',
                    function() {
                        // An infowindow opening throws off the fitBounds
                        // logic. Call fitBounds again when necessary
                        if (self.mapLoaded && self.activeBounds) {
                            self.map.fitBounds(self.activeBounds);
                            delete self.activeBounds;

                            self.map.setZoom(self.map.getZoom() - 1);
                        }
                    }
                );

                jQuery('.imprint-map-container').affix({
                    offset: {
                        top: jQuery('.imprint-map-container').offset().top,
                        bottom: jQuery('.foot').outerHeight() + 30
                    }
                });
            }
        },
        onClickWork: function(evt) {
            this.clearState();
            jQuery(evt.currentTarget).addClass('infocus');
            this.syncMap(this.$el);
            this.addHistory(this.$el);
        },
        onClickImprint: function(evt) {
            this.clearState();

            var $elt = jQuery(evt.currentTarget);
            var $parent = $elt.parents('.imprint-list-item');

            $parent.addClass('infocus');
            this.syncMap($parent, $elt.data('map-id'));
            this.addHistory($elt);
        },
        onClickBookCopy: function(evt) {
            this.clearState();
            var $elt = jQuery(evt.currentTarget);
            var $parent = $elt.parent();

            $parent.addClass('infocus');
            this.syncMap($parent);
            this.addHistory($elt);
        },
        onClickFootprint: function(evt) {
            this.clearState();

            var $elt = jQuery(evt.currentTarget);
            $elt.addClass('infocus');
            this.syncMap($elt, $elt.data('map-id'));
            this.addHistory($elt);
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
        syncMap: function($parent, activeId) {
            var subset = [];
            var highlight;

            $parent.find('.map-marker').each(function() {
                subset.push(jQuery(this).data('related'));
            });

            if (activeId && Object.prototype.hasOwnProperty.call(
                this.markers, activeId)) {
                // the active element has an associated place
                highlight = activeId;
                if (subset.indexOf(highlight) === -1) {
                    subset.push(highlight);
                }
            }

            var bounds = new google.maps.LatLngBounds();
            for (var key in this.markers) {
                if (Object.prototype.hasOwnProperty.call(this.markers, key)) {
                    var mk = this.markers[key].marker;
                    if (subset.indexOf(key) > -1) {
                        mk.setVisible(true);
                        bounds.extend(mk.getPosition());
                        this.spiderfier.addMarker(mk);
                    } else {
                        mk.setVisible(false);
                        this.spiderfier.removeMarker(mk);
                    }
                }
            }

            if (subset.length < 1) {
                this.$el.find('.empty-map-message').show();
                this.map.fitBounds(this.bounds);
            } else if (!highlight) {
                this.$el.find('.empty-map-message').hide();
                this.map.fitBounds(bounds);
            } else {
                this.$el.find('.empty-map-message').hide();
                this.activeBounds = bounds;
                this.infowindow.setContent(this.markers[highlight].content);
                this.infowindow.open(
                    this.map, this.markers[highlight].marker);
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

                var url = this.urlBase;
                if (state.imprint) {
                    url += state.imprint + '/';
                }
                if (state.copy) {
                    url += state.copy + '/';
                }
                if (state.footprint) {
                    url += state.footprint + '/';
                }
                window.history.pushState(state, '', url);
            }
        },
        clearState: function() {
            this.infowindow.close();
            this.spiderfier.clearMarkers();
            jQuery(this.el).find('.infocus').removeClass('infocus');
        },
        popHistory: function(evt) {
            this.clearState();
            var fpId;
            var copyId;
            var imprintId;

            if (evt.originalEvent.state) {
                fpId = evt.originalEvent.state.footprint;
                copyId = evt.originalEvent.state.copy;
                imprintId = evt.originalEvent.state.imprint;
            }
            this.setState(imprintId, copyId, fpId, true);
        },
        setState: function(imprintId, copyId, footprintId, syncMap) {
            var $elt = this.$el;
            var activeId;
            if (footprintId) {
                this.openBookCopy(copyId);

                $elt = jQuery('.list-group-item[data-footprint-id="' +
                    footprintId + '"]');
                $elt.addClass('infocus');
                activeId = $elt.data('map-id');
            } else if (copyId) {
                $elt = this.openBookCopy(copyId);
                $elt.addClass('infocus');
            } else if (imprintId) {
                $elt = jQuery('h4[data-imprint-id="' + imprintId + '"]');
                activeId = $elt.data('map-id');

                $elt = $elt.parents('.imprint-list-item');
                $elt.addClass('infocus');
            } else {
                this.$el.find('.writtenwork-title').addClass('infocus');
            }

            if (syncMap) {
                this.syncMap($elt, activeId);
            }

            if (!this.inView($elt)) {
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
