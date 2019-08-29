let vuePath = 'lib/vue/vue.min';
let urlArgs = 'bust=' + (new Date()).getTime();
if (Footprints.debug == 'true') {
    vuePath = 'lib/vue/vue';
    urlArgs = '';
}

requirejs.config({
    baseUrl: Footprints.staticUrl + 'js/',
    paths: {
        'jquery': 'lib/jquery-3.3.1.min',
        'mapVue': 'app/components/mapvue',
        'multiselect': 'lib/vue-multiselect/vue-multiselect.min',
        'searchVue': 'app/components/searchvue',
        'utils': 'app/utils',
        'Vue': vuePath
    },
    shim: {
        'utils': {
            'deps': ['jquery']
        }
    },
    urlArgs: urlArgs
});
