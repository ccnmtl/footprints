define(['jquery', 'utils'], function($, layer, utils) {
    const PathmapperTableVue = {
        props: ['value'],
        template: '#pathmapper-table-template',
        data: function() {
            return {
            };
        },
        methods: {
            updateLayers: function() {
                // @todo - for each layer, query book copy data
                console.log('update table');
            }
        },
        created: function() {
            this.$watch('value', this.updateLayers, {deep: true});
        }
    };
    return {
        PathmapperTableVue: PathmapperTableVue
    };
});
