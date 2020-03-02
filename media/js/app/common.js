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
        'layerFormVue': 'js/app/components/layerformvue',
        'layerMapVue': 'js/app/components/layermapvue',
        'locationVue': 'js/app/components/locationvue',
        'mapVue': 'js/app/components/mapvue',
        'markerclusterer': 'js/lib/markerclusterer/markerclustererplus.min',
        'select2': 'js/lib/select2-4.0.10/js/select2.full',
        'selectWidget': 'js/app/components/select-widget',
        'tableVue': 'js/app/components/tableVue',
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
