requirejs(['./common'], function(common) {
    const libs = ['jquery', 'Vue', 'mapVue', 'searchVue', 'utils'];
    requirejs(libs,
        function($, Vue, map, search, utils) {
            new Vue({
                el: '#outer-container',
                data: function() {
                    return {
                        criteria: {},
                        total: null,
                    };
                },
                components: {
                    'search-widget': search.SearchVue,
                    'google-map': map.GoogleMapVue
                },
                methods: {
                    search: function() {
                        if ($('html').hasClass('busy')) {
                            return;
                        }

                        $('html').addClass('busy');
                        this.searching = true;

                        // retrieve book copies
                        $.ajax({
                            url: this.searchUrl,
                            data: this.criteria,
                            type: 'post'
                        }).done((results) => {
                            this.total = results.total;
                            $('html').removeClass('busy');
                            this.searching = false;
                        });
                    }
                },
                created: function() {
                    this.searchUrl = Footprints.baseUrl + 'search/book/';

                    // Setup CSRF configuration and busy states
                    utils.ajaxSetup();

                    // eslint-disable-next-line
                    window.addEventListener('beforeunload', this.beforeUnload);

                    this.$watch('criteria', this.search);
                },
                mounted: function() {
                },
                updated: function() {
                }
            });
        }
    );
});
