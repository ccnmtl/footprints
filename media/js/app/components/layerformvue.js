define(['jquery', 'selectWidget'], function($, select) {
    const LayerVue = {
        props: ['value'],
        template: '#layer-template',
        components: {
            'select-widget': select.SelectWidget
        },
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
                    'censored': 'notapp',
                    'expurgated': 'notapp',
                    'visible': true,
                    'narrative': '',
                    'totalCopies': 0
                },
                total: null,
                totalMax: null,
                pubMin: null,
                pubMax: null,
                footprintMin: null,
                footprintMax: null,
                minYear: 1000,
                maxYear: new Date().getFullYear()
            };
        },
        computed: {
            pluralizeTerm: function() {
                if (this.total === 1) {
                    return 'copy';
                } else {
                    return 'copies';
                }
            }
        },
        methods: {
            updateNarrative: function() {
                let s = '';
                if (this.$refs.imprint.selected()) {
                    s += ' from ' + this.$refs.imprint.selected();
                } else if (this.$refs.work.selected()) {
                    s += ' from ' + this.$refs.work.selected();
                }

                // Imprint criteria
                const imprintLoc = this.$refs.imprintLoc.selected();
                let pubDate = this.displayPubRangeStatus().toLowerCase();
                if (imprintLoc && pubDate) {
                    if (!this.validPubRange()) {
                        s += ' published in ' + imprintLoc;
                    } else {
                        s += ' ' + pubDate + ' in ' + imprintLoc;
                    }
                } else if (imprintLoc) {
                    s += ' published in ' + imprintLoc;
                } else if (pubDate) {
                    s += ' ' + pubDate;
                }

                // Footprint criteria
                const ftLoc = this.$refs.footprintLoc.selected();
                const ftDate = this.displayFootprintRangeStatus().toLowerCase();
                if (ftLoc && ftDate) {
                    s += ' with footprints that ' + ftDate + ' in ' + ftLoc;
                } else if (ftLoc) {
                    s += ' with footprints in ' + ftLoc;
                } else if (ftDate) {
                    s += ' with footprints that ' + ftDate;
                }

                if (this.$refs.actor.selected()) {
                    s += ' associated with ' + this.$refs.actor.selected();
                }

                if (this.layer.censored !== 'notapp' ||
                        this.layer.expurgated !== 'notapp') {
                    s += ' that were ';
                }
                if (this.layer.censored !== 'notapp') {
                    if (this.layer.censored === 'yes') {
                        s += ' censored';
                    } else if (this.layer.censored === 'no') {
                        s += ' not censored';
                    }
                    if (this.layer.expurgated !== 'notapp') {
                        s += ' and ';
                    }
                }
                if (this.layer.expurgated === 'yes') {
                    s += ' expurgated';
                }
                if (this.layer.expurgated === 'no') {
                    s += ' not expurgated';
                }
                this.layer.narrative = s;
            },
            displayRangeStatus: function(lbl, prefix) {
                const start = parseInt(this.layer[lbl + 'Start'], 10);
                const end = parseInt(this.layer[lbl + 'End'], 10);
                const range = this.layer[lbl + 'Range'];

                if (start && start < this.minYear || start > this.maxYear) {
                    return 'The start year must be between ' +
                        this.minYear + ' - ' + this.maxYear;
                }

                if (range) {
                    if (start && !end) {
                        return prefix + 'from ' + start + ' to present';
                    }

                    if (end < this.minYear || end > this.maxYear) {
                        return 'The end year must be between ' +
                            this.minYear + ' - ' + this.maxYear;
                    }

                    if (start > end) {
                        return 'The start year must be less than the end year';
                    }

                    if (start && end) {
                        return prefix + 'from ' + start + ' to ' + end;
                    }

                    if (!start && end) {
                        return prefix + 'up to ' + end;
                    }
                } else if (start) {
                    return prefix + 'in the year ' + start;
                }
                return '';
            },
            displayFootprintRangeStatus: function() {
                return this.displayRangeStatus('footprint', 'occurred ');
            },
            displayPubRangeStatus: function() {
                return this.displayRangeStatus('pub', 'published ');
            },
            pubRangeChanged: function() {
                if (this.validPubRange()) {
                    this.search();
                }
            },
            footprintRangeChanged: function() {
                if (this.validFootprintRange()) {
                    this.search();
                }
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
                this.total = null;
            },
            search: function() {
                if (this.isSearching() || !this.isDirty()) {
                    return;
                }
                this.setIsSearching();

                const data = {...this.layer};
                delete data.narrative;

                // retrieve book copies based on criteria
                $.ajax({
                    url: this.searchUrl,
                    data: data,
                    type: 'post'
                }).done((results) => {
                    this.state = JSON.stringify(this.layer);
                    this.totalMax = results.totalMax;
                    this.total = results.total;
                    this.layer.totalCopies = this.total;
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
            validResults: function() {
                return this.total > 0 && this.total < this.totalMax;
            },
            validLayerTitle: function() {
                return this.layer.title.length > 0;
            },
            validDateRange: function(lbl) {
                const start = parseInt(this.layer[lbl + 'Start'], 10);
                const end = parseInt(this.layer[lbl + 'End'], 10);
                const range = this.layer[lbl + 'Range'];

                if (start && (start < this.minYear || start > this.maxYear)) {
                    return false;
                }

                if (range && end &&
                        (end < this.minYear || end > this.maxYear)) {
                    return false;
                }

                if (range && start && end && start > end) {
                    return false;
                }
                return true;
            },
            validPubRange: function() {
                return this.validDateRange('pub');
            },
            validFootprintRange: function() {
                return this.validDateRange('footprint');
            },
            validTitleField: function() {
                if (!this.validLayerTitle()) {
                    $('#layerTitle').addClass('invalid-form-field');
                    $('#layerTitle').removeClass('valid-form-field');
                } else {
                    $('#layerTitle').removeClass('invalid-form-field');
                    $('#layerTitle').addClass('valid-form-field');
                }
            },
            save: function() {
                if (!this.validLayerTitle()) {
                    $('#layerTitle').addClass('invalid-form-field');
                    $('#layerTitle').focus();
                } else if (this.total > 0 && this.validLayerTitle() &&
                        this.validPubRange() && this.validFootprintRange()) {
                    this.$emit('save', $.extend(true, {}, this.layer));
                }
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

            this.layer = $.extend(true, this.layer, this.value);
            this.$watch('layer.work', this.workChanged);
            this.$watch('layer.imprint', this.search);
            this.$watch('layer.imprintLocation', this.search);
            this.$watch('layer.footprintLocation', this.search);
            this.$watch('layer.footprintStart', this.footprintRangeChanged);
            this.$watch('layer.footprintEnd', this.footprintRangeChanged);
            this.$watch('layer.footprintRange', this.footprintRangeChanged);
            this.$watch('layer.pubStart', this.pubRangeChanged);
            this.$watch('layer.pubEnd', this.pubRangeChanged);
            this.$watch('layer.pubRange', this.pubRangeChanged);
            this.$watch('layer.actor', this.search);
            this.$watch('layer.censored', this.search);
            this.$watch('layer.expurgated', this.search);

            this.$watch('layer.work', this.updateNarrative);
            this.$watch('layer.imprint', this.updateNarrative);
            this.$watch('layer.imprintLocation', this.updateNarrative);
            this.$watch('layer.footprintLocation', this.updateNarrative);
            this.$watch('layer.footprintStart', this.updateNarrative);
            this.$watch('layer.footprintEnd', this.updateNarrative);
            this.$watch('layer.footprintRange', this.updateNarrative);
            this.$watch('layer.pubStart', this.updateNarrative);
            this.$watch('layer.pubEnd', this.updateNarrative);
            this.$watch('layer.pubRange', this.updateNarrative);
            this.$watch('layer.actor', this.updateNarrative);
            this.$watch('layer.censored', this.updateNarrative);
            this.$watch('layer.expurgated', this.updateNarrative);
        },
        mounted: function() {
            this.search();
        }
    };
    return {
        LayerVue: LayerVue
    };
});
