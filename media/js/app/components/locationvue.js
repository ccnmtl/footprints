define(['jquery', 'utils'], function($, utils) {
    const PathmapperLocationVue = {
        props: ['layers', 'value'],
        template: '#pathmapper-location-template',
        data: function() {
            return {
                items: [],
                interim: 0,
                initial: 0,
                terminal: 0,
                copies: {}
            };
        },
        computed: {
            pluralizeTerm: function() {
                if (Object.keys(this.copies).length === 1) {
                    return 'copy';
                } else {
                    return 'copies';
                }
            },
            copyCount: function() {
                return Object.keys(this.copies).length;
            }
        },
        methods: {
            clearLocation: function() {
                this.$emit('clearlocation', null);
            },
            clearStats: function() {
                this.initial = 0;
                this.interim = 0;
                this.final = 0;
                this.items = [];
                this.copies = {};
            },
            updateLocation: function() {
                if (!this.value) {
                    return;
                }
                this.clearStats();
                for (let pt of this.value.points) {
                    if (pt.layer.visible) {
                        this.aggregate(pt);
                    }
                }
                this.items.sort(function(a, b) {return a.sortBy > b.sortBy;});
            },
            aggregate: function(pt) {
                if (!this.copies[pt.bookcopy.identifier]) {
                    this.copies[pt.bookcopy.identifier] = [];
                    if (pt.type === 'initial') {
                        this.initial++;
                    }
                }
                this.copies[pt.bookcopy.identifier].push(pt);

                // keep the array sorted
                this.copies[pt.bookcopy.identifier].sort(
                    function(a, b) {return a.sortBy > b.sortBy;});

                if (pt.type === 'interim') {
                    this.interim++;
                } else if (pt.type === 'terminal') {
                    this.terminal++;
                }
            },
            workUrl: function(pt) {
                return '/writtenwork/' + pt.bookcopy.imprint.work_id + '/';
            },
            imprintUrl: function(pt) {
                return '/writtenwork/' + pt.bookcopy.imprint.work_id + '/' +
                    pt.bookcopy.imprint.id + '/';
            },
            copyUrl: function(name, value) {
                const copy = this.copies[name][0].bookcopy;
                return '/writtenwork/' + copy.imprint.work_id + '/' +
                    copy.imprint.id + '/' +
                    copy.id + '/';
            }
        },
        created: function() {
            this.$watch('value', this.updateLocation);
        },
        updated: function() {
        }
    };
    return {
        PathmapperLocationVue: PathmapperLocationVue
    };
});
