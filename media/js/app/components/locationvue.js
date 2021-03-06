define(['jquery', 'utils'], function($, utils) {
    const PathmapperLocationVue = {
        props: ['layers', 'value'],
        template: '#pathmapper-location-template',
        data: function() {
            return {
                items: [],
                interim: 0,
                initial: 0,
                terminal: 0
            };
        },
        computed: {
            pluralizeTerm: function() {
                if (this.items.length === 1) {
                    return 'copy';
                } else {
                    return 'copies';
                }
            },
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
            },
            updateLocation: function() {
                if (!this.value) {
                    return;
                }
                this.clearStats();
                for (let pt of this.value.points) {
                    if (pt.layer.visible) {
                        this.summarize(pt);
                        this.items.push(pt);
                    }
                }
                this.items.sort(function(a, b) {return a.sortBy > b.sortBy;});
            },
            summarize: function(pt) {
                if (pt.type === 'interim') {
                    this.interim++;
                } else if (pt.type === 'terminal') {
                    this.terminal++;
                } else {
                    this.initial++;
                }
            },
            workUrl: function(pt) {
                return '/writtenwork/' + pt.bookcopy.imprint.work_id + '/';
            },
            imprintUrl: function(pt) {
                return '/writtenwork/' + pt.bookcopy.imprint.work_id + '/' +
                    pt.bookcopy.imprint.id + '/';
            },
            copyUrl: function(pt) {
                return '/writtenwork/' + pt.bookcopy.imprint.work_id + '/' +
                    pt.bookcopy.imprint.id + '/' +
                    pt.bookcopy.id + '/';
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
