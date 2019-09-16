define(['jquery'], function($) {
    const SearchVue = {
        props: ['total'],
        template: '#search-template',
        data: function() {
            return {
                criteria: {}
            };
        },
        methods: {
            updateCriteria: function() {
                const newValue = $.extend(true, {}, this.criteria);
                this.$emit('input', newValue);
            }
        },
        created: function() {
        },
        mounted: function() {
            // copy the passed criteria values
            this.criteria = $.extend(true, {}, this.value);
            this.$watch('criteria.work', this.updateCriteria);
        },
        updated: function() {
            // @todo - does this need to be done twice?
            // Updates should only happen if a user is loading in a saved value
        }
    };
    return {
        SearchVue: SearchVue
    };
});
