define(['jquery', 'utils'], function($, utils) {
    const PathmapperTimelineVue = {
        props: ['value'],
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
            },
            updateLayers: function() {
                // respect layer visibility
                const value = this.value.filter(layer => layer.visible);

                const ctx = {
                    layers: JSON.stringify(value)
                };

                $.ajax({
                    type: 'POST',
                    url: Footprints.baseUrl + 'api/events/',
                    dataType: 'json',
                    data: ctx
                }).done((results) => {
                    // populate the chart
                    const data = results.map(function(result) {
                        return {
                            x: Date.parse(result.year),
                            y: 5,
                            value: result.count
                        };
                    });
                    this.chart.series[0].update({data: data});
                });
            }
        },
        created: function() {
            this.$watch('value', this.updateLayers, {deep: true});
            this.updateLayers();

            this.options = {
                chart: {
                    type: 'heatmap',
                    height: '100px'
                },
                title: {
                    text: null
                },
                xAxis: {
                    type: 'datetime',
                    labels: {
                        align: 'left',
                        x: 5,
                        y: 14,
                        format: '{value:%Y}'
                    },
                    tickLength: 16
                },
                yAxis: {
                    visible: false,
                    minPadding: 0,
                    maxPadding: 0,
                    startOnTick: false,
                    endOnTick: false
                },
                legend: {
                    margin: 20,
                    padding: 0
                },
                colorAxis: {
                    min: 0,
                    minColor: '#FFFFFF',
                    maxColor: '#FF0000'
                },
                series: [{
                    nullColor: '#EFEFEF',
                    colsize: 365 * 24 * 36e5, // one day
                    tooltip: {
                        headerFormat: 'Events ',
                        pointFormat: '{point.x:%Y} <b>{point.value}</b>'
                    },
                    data: []
                }]
            };
        },
        mounted: function() {
            this.chart = Highcharts.chart('the-timeline', this.options);
        }
    };
    return {
        PathmapperTimelineVue: PathmapperTimelineVue
    };
});