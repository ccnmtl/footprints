requirejs(['./common'], function(common) {
    const libs = ['jquery', 'Vue', 'mapVue', 'searchVue', 'utils'];
    requirejs(libs,
        function($, Vue, map, search, utils) {
            new Vue({
                el: '#outer-container',
                data: function() {
                    return {
                    };
                },
                components: {
                    'search-widget': search.SearchVue,
                    'google-map': map.GoogleMapVue
                },
                methods: {
                },
                created: function() {
                },
                mounted: function() {
                },
                updated: function() {
                }
            });
        }
    );
});
