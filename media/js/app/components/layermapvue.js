define(['jquery', 'utils'], function($, utils) {
    const LayerMapVue = {
        props: ['layer', 'map', 'queue'],
        data: function() {
            return {
                lines: [],
                places: []
            };
        },
        methods: {
            url: function(pageNumber) {
                return Footprints.baseUrl +
                    'pathmapper/route/?page=' + pageNumber;
            },
            addLine: function(coords) {
                return new google.maps.Polyline({
                    path: coords,
                    geodesic: true,
                    strokeColor: '#cb8d78',
                    strokeOpacity: .6,
                    strokeWeight: 1
                });
            },
            addPoint: function(placeId, title, type, copy, footprint, latlng) {
                this.$emit('add-point', {
                    placeId: placeId,
                    placeTitle: title,
                    latlng: latlng,
                    point: {
                        layer: {
                            'id': this.layer.id,
                            'visible': false
                        },
                        type: type,
                        bookcopy: copy,
                        footprint: footprint
                    }
                });
                return latlng;
            },
            addImprint: function(bookcopy) {
                const latlng = {
                    lat: bookcopy.imprint.place.latitude,
                    lng: bookcopy.imprint.place.longitude
                };
                return this.addPoint(
                    bookcopy.imprint.place.id,
                    bookcopy.imprint.place.display_title,
                    'initial', bookcopy, null, latlng);
            },
            addFootprint: function(bookcopy, footprint) {
                const latlng = {
                    lat: footprint.place.latitude,
                    lng: footprint.place.longitude
                };
                return this.addPoint(
                    footprint.place.id, footprint.place.display_title,
                    'interim', bookcopy, footprint, latlng);
            },
            clear: function() {
                for (let route of this.lines) {
                    route.setMap(null);
                    route = null;
                }
                this.lines = [];
                this.$emit('delete-layer', {id: this.layer.id});
            },
            refresh: function() {
                this.clear(); // clear the routes
                this.getPage(1); // get the data again
            },
            getPage: function(pageNumber) {
                const ctx = {'layer': this.layer, 'page': pageNumber};
                this.queue.add(this.getData, this.mapData, ctx);
            },
            getData: function(params) {
                return new Promise((resolve, reject) => {
                    $.ajax({
                        type: 'POST',
                        url: this.url(params.page),
                        dataType: 'json',
                        data: {layer: JSON.stringify(params.layer)},
                        success: (data) => {
                            resolve(data);
                        },
                        error: (error) => {
                            reject(error);
                        }
                    });
                });
            },
            mapData: function(data) {
                for (let bookcopy of data.results) {
                    let coords = [];
                    if (bookcopy.imprint && bookcopy.imprint.place) {
                        coords.push(this.addImprint(bookcopy));
                    }
                    for (let fp of bookcopy.footprints) {
                        if (fp.place) {
                            coords.push(this.addFootprint(bookcopy, fp));
                        }
                    }
                    this.lines.push(this.addLine(coords));
                }
                this.visibilityChanged(this.layer.visible, false);

                const nextPage = utils.parsePageNumber(data.next);
                if (nextPage > 1) {
                    this.getPage(nextPage);
                }
            },
            visibilityChanged: function(newVal, oldVal) {
                if (oldVal === newVal) {
                    return;
                }
                const map = newVal ? this.map : null;
                for (let route of this.lines) {
                    route.setMap(map);
                }
                this.$emit('update-layer',
                    {id: this.layer.id, visible: newVal});
            }
        },
        beforeDestroy: function() {
            this.clear();
        },
        mounted: function() {
            this.$watch('layer.visible', this.visibilityChanged);
            this.$watch('layer.work', this.refresh);
            this.$watch('layer.imprint', this.refresh);
            this.$watch('layer.imprintLocation', this.refresh);
            this.$watch('layer.footprintLocation', this.refresh);
            this.$watch('layer.footprintStart', this.refresh);
            this.$watch('layer.footprintEnd', this.refresh);
            this.$watch('layer.pubStart', this.refresh);
            this.$watch('layer.pubEnd', this.refresh);
            this.$watch('layer.actor', this.refresh);
            this.$watch('layer.censored', this.refresh);
            this.$watch('layer.expurgated', this.refresh);

            this.getPage(1);
        },
        render() {
            // don't do anything
        }
    };
    return {
        LayerMapVue: LayerMapVue
    };
});
