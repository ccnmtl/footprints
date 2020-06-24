define(['jquery', 'utils'], function($, utils) {
    const PathmapperTimelineVue = {
        props: ['layers'],
        template: '#pathmapper-timeline-template',
        data: function() {
            return {
            };
        },
        methods: {
            playTimeline: function() {
                if ($('.button-timeline').hasClass('pause')) {
                    $('.button-timeline').removeClass('pause');
                } else {
                    $('.button-timeline').addClass('pause');
                }
            }
        },
        created: function() {
        },
        mounted: function() {
        }
    };
    return {
        PathmapperTimelineVue: PathmapperTimelineVue
    };
});