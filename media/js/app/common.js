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
        'layerListVue': 'js/app/components/layerlistvue',
        'layerVue': 'js/app/components/layervue',
        'mapVue': 'js/app/components/mapvue',
        'select2': 'js/lib/select2-4.0.10/js/select2.min',
        'selectWidget': 'js/app/components/select-widget',
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
