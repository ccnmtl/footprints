requirejs(['./common'], function() {
    const a = ['jquery', 'Vue', 'mapVue'];
    requirejs(a, function($, Vue, maps) {
        new Vue({
            el: '#map-container',
            components: {
                'google-map': maps.GoogleMapVue
            }
        });
    });
});
