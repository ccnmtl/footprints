define(['jquery', 'selectWidget'], function($, select) {
    const LayerVue = {
        props: ['value'],
        template: '#layer-template',
        data: function() {
            return {
                layer: {
                    'id': null,
                    'title': '',
                    'work': null,
                    'imprint': null,
                    'imprintLocation': null,
                    'footprintLocation': null,
                    'footprintLocationFinal': null,
                    'actor': null,
                    'pubStart': null,
                    'pubEnd': null,
                    'pubRange': false,
                    'footprintStart': null,
                    'footprintEnd': null,
                    'footprintRange': false,
                    'censored': null,
                    'expurgated': null,
                    'visible': true
                },
                total: null,
                pubMin: null,
                pubMax: null,
                footprintMin: null,
                footprintMax: null
            };
        },
        computed: {
            displayCriteria: function() {
                return '';
            },
        },
        components: {
            'select-widget': select.SelectWidget
        },
        methods: {
            displayMinMax: function(start, end) {
                start = start > this.dateMin ? start : null;
                end = end < this.dateMax ? end : null;
                if (start && !end) {
                    return start + ' to present';
                } else if (!start && end) {
                    return 'Up to ' + end;
                } else if (start && end) {
                    return start + ' to ' + end;
                } else {
                    return '';
                }
            },
            displayFootprintMinMax: function() {
                return this.displayMinMax(this.footprintMin, this.footprintMax);
            },
            displayPubMinMax: function() {
                return this.displayMinMax(this.pubMin, this.pubMax);
            },
            displayYearStatus: function(lbl) {
                var start = this.layer[lbl + 'Start'];
                var end = this.layer[lbl + 'End'];
                var range = this.layer[lbl + 'Range'];

                if (range) {
                    if (start && !end) {
                        return start + ' to present';
                    }

                    if (start && end) {
                        return start + ' to ' + end;
                    }

                    if (!start && end) {
                        return 'Up to ' + end;
                    }
                } else if (start) {
                    return start;
                }
                return 'All years';
            },
            displayFootprintYearStatus: function() {
                return this.displayYearStatus('footprint');
            },
            displayPubYearStatus: function() {
                return this.displayYearStatus('pub');
            },
            workChanged: function() {
                // the imprint is always cleared when the work changes
                this.layer.imprint = null;
                this.search();
            },
            isDirty: function() {
                return this.state !== JSON.stringify(this.layer);
            },
            isSearching: function() {
                return $('html').hasClass('busy');
            },
            setIsSearching: function() {
                $('html').addClass('busy');
                this.total = 0;
            },
            search: function() {
                if (this.isSearching() || !this.isDirty()) {
                    return;
                }

                this.setIsSearching();

                // retrieve book copies based on criteria
                $.ajax({
                    url: this.searchUrl,
                    data: this.layer,
                    type: 'post'
                }).done((results) => {
                    this.state = JSON.stringify(this.layer);
                    this.total = results.total;
                    this.pubMin = results.pubMin;
                    this.pubMax = results.pubMax;
                    this.footprintMin = results.footprintMin;
                    this.footprintMax = results.footprintMax;
                    $('html').removeClass('busy');
                });
            },
            cancel: function() {
                this.$emit('cancel');
            },
            save: function() {
                this.$emit('save', $.extend(true, {}, this.layer));
            },
            togglePane: function() {
                if ($('#container-pane').hasClass('widget-pane-expanded')) {
                    $('#container-pane').removeClass('widget-pane-expanded');
                    $('#container-pane').addClass('widget-pane-collapsed');
                } else {
                    $('#container-pane').addClass('widget-pane-expanded');
                    $('#container-pane').removeClass('widget-pane-collapsed');
                }
            },
            togglePubRange: function() {
                this.layer.pubRange = !this.layer.pubRange;
                if (!this.layer.pubRange) {
                    this.layer.pubEnd = null;
                }
            },
            toggleFootprintRange: function() {
                this.layer.footprintRange = !this.layer.footprintRange;
                if (!this.layer.footprintRange) {
                    this.layer.footprintEnd = null;
                }
            }
        },
        created: function() {
            this.searchUrl = Footprints.baseUrl + 'search/book/';
            this.dateMin = 1000;
            this.dateMax = 9999;

            // @todo - how is this handled when the list updates the model?

            this.layer = $.extend(true, this.layer, this.value);
            this.$watch('layer.work', this.workChanged);
            this.$watch('layer.imprint', this.search);
            this.$watch('layer.imprintLocation', this.search);
            this.$watch('layer.footprintLocation', this.search);
            this.$watch('layer.footprintStart', this.search);
            this.$watch('layer.footprintEnd', this.search);
            this.$watch('layer.pubStart', this.search);
            this.$watch('layer.pubEnd', this.search);
            this.$watch('layer.actor', this.search);
        },
        mounted: function() {
            this.search();
        }
    };
    return {
        LayerVue: LayerVue
    };
});
