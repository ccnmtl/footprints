let vuePath = 'lib/vue/vue.min';
let urlArgs = 'bust=' + (new Date()).getTime();
if (Footprints.debug == 'true') {
    vuePath = 'lib/vue/vue';
    urlArgs = '';
}

requirejs.config({
    baseUrl: Footprints.staticUrl + 'js/',
    paths: {
        'domReady': 'lib/require/domReady',
        'jquery': 'lib/jquery-3.3.1.min',
        'mapVue': 'app/components/gmapvue',
        'Vue': vuePath
    },
    urlArgs: urlArgs
});
