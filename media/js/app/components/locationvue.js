define(['jquery', 'utils'], function($, utils) {
    const PathmapperLocationVue = {
        props: ['layers', 'value'],
        template: '#pathmapper-location-template',
        data: function() {
            return {
            };
        },
        methods: {
            clearLocation: function() {
                this.$emit('clearlocation', null);
            }
        },
        created: function() {
        },
        updated: function() {
        }
    };
    return {
        PathmapperLocationVue: PathmapperLocationVue
    };
});
