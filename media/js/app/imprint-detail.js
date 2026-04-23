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
            _.bindAll(this, 'initializeMap', 'resize',
                'onClickBookCopy', 'onClickFootprint', 'onClickImprint',
                'onClickMarker', 'onClickWork', 'syncMap',
                'onShareLink', 'clearState', 'setState',
                'addHistory', 'popHistory');

            this.urlBase = options.urlBase;

            this.footprintIcon = this.iconWithColor('#ffa881');
            this.imprintIcon = this.iconWithColor('#5e98b7');

            this.shareTemplate =
                _.template(jQuery(options.shareTemplate).html());

            this.mapLoaded = false;

            jQuery(window).on('resize', this.resize);
            jQuery(window).on('popstate', this.popHistory);

            this.initializeMap(options);
            jQuery(this.el).find('[data-toggle="tooltip"]').tooltip();
        },
        scrollToItem: function($elt) {
            var eltTop = $elt.offset().top - 150;
            var mapTop = jQuery('.foot').offset().top -
                jQuery('.imprint-map-container').height() - 40;

            jQuery('html, body').animate({
                scrollTop: Math.min(eltTop, mapTop) + 'px'
            }, 900);
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
            return L.divIcon({
                className: 'custom-marker',
                html: `
                            <div style="
                                background-color: ${color};
                                width: 16px;
                                height: 16px;
                                border-radius: 50%;
                                border: 2px solid white;
                                box-shadow: 0 0 2px rgba(0,0,0,0.5);
                            "></div>
                        `,
                iconSize: [16, 16],
                iconAnchor: [8, 8],
            });
        },
        initializeMap: function(options) {
            var self = this;
            var markers = jQuery(this.el).find('.map-marker');
            if (markers.length > 0) {

                this.resize();

                var mapElt = jQuery(this.el).find('.imprint-map')[0];

                this.map = L.map(mapElt);

                L.tileLayer(
                    Footprints.tileServer.url,
                    {
                        maxZoom: 20,
                        detectRetina: true,
                        attribution: Footprints.tileServer.attribution
                    }
                ).addTo(this.map);

                this.bounds = L.latLngBounds();
                this.clusterGroup = L.markerClusterGroup({
                    spiderfyOnMaxZoom: true
                });
                this.map.addLayer(this.clusterGroup);

                this.markers = {};

                for (var i = 0; i < markers.length; i++) {
                    var m = markers[i];
                    var id = jQuery(m).data('related');
                    var lat = jQuery(m).data('latitude');
                    var lng = jQuery(m).data('longitude');
                    var latlng = [lat, lng];

                    var content = jQuery(m).html();

                    var marker = L.marker(latlng, {
                        icon: this.getIcon(id),
                        dataId: id
                    });

                    marker.bindPopup(content);

                    marker.on('click', this.onClickMarker);

                    this.bounds.extend(latlng);

                    this.markers[id] = {
                        marker: marker,
                        content: content
                    };
                    this.clusterGroup.addLayer(marker);
                }

                this.map.fitBounds(this.bounds);

                this.map.whenReady(function() {
                    if (!self.mapLoaded) {
                        self.mapLoaded = true;

                        self.setState(
                            options.state.imprint,
                            options.state.copy,
                            options.state.footprint,
                            true
                        );
                    }
                });
                jQuery('.imprint-map-container').affix({
                    offset: {
                        top: jQuery('.imprint-map-container').offset().top,
                        bottom: jQuery('.foot').outerHeight() + 30
                    }
                });
            }
        },
        onClickMarker: function(evt) {
            var m = evt.target;

            // find corresponding list item
            var q = '[data-map-id="' + m.options.dataId + '"]';
            var $elt = this.$el.find(q).first();

            jQuery(this.el).find('.infocus').removeClass('infocus');

            this.setState(
                $elt.data('imprint-id'),
                $elt.data('copy-id'),
                $elt.data('footprint-id'),
                false // sync map
            );
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

            var bounds = L.latLngBounds();
            for (var key in this.markers) {
                if (Object.prototype.hasOwnProperty.call(this.markers, key)) {
                    var mk = this.markers[key].marker;
                    if (subset.indexOf(key) > -1) {
                        bounds.extend(mk.getLatLng());
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
                this.popup = L.popup()
                    .setLatLng(this.markers[highlight].marker.getLatLng())
                    .setContent(this.markers[highlight].content)
                    .openOn(this.map);
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
            if (this.popup) {
                this.map.closePopup(this.popup);
            }
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
