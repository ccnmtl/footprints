define(['jquery', 'utils'], function($, layer, utils) {
    const PathmapperTableVue = {
        template: '#pathmapper-table-template',
        data: function() {
            return {
                layers: []
            };
        },
        methods: {
        },
        created: function() {
        }
    };
    return {
        PathmapperTableVue: PathmapperTableVue
    };
});
