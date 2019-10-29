let vuePath = 'js/lib/vue/vue.min';
let urlArgs = 'bust=' + (new Date()).getTime();
if (Footprints.debug == 'true') {
    vuePath = 'js/lib/vue/vue';
    urlArgs = '';
}

requirejs.config({
    baseUrl: Footprints.staticUrl,
    paths: {
        'jquery': 'jquery/js/jquery-3.4.1.min',
        'mapVue': 'js/app/components/mapvue',
        'searchVue': 'js/app/components/searchvue',
        'utils': 'js/app/utils',
        'Vue': vuePath
    },
    shim: {
        'utils': {
            'deps': ['jquery']
        }
    },
    urlArgs: urlArgs
});
