define(['jquery', 'utils'], function($, utils) {
    const PathmapperTimelineVue = {
        props: ['value'],
        template: '#pathmapper-timeline-template',
        data: function() {
            return {
            };
        },
        methods: {
            updateLayers: function() {
                // respect layer visibility
                const value = this.value.filter(layer => layer.visible);

                const ctx = {
                    layers: JSON.stringify(value)
                };

                $.ajax({
                    type: 'POST',
                    url: Footprints.baseUrl + 'pathmapper/timeline/',
                    dataType: 'json',
                    data: ctx
                }).done((data) => {
                    // populate the chart
                    this.chart.data = [{
                        "x": 1293840000000, // year
                        "y": 1, // static
                        "value": 10 // count
                    },
                    {
                        "x": 129380000000, // year
                        "y": 2, // static
                        "value": 30 // count
                    }];
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
                    maxColor: Highcharts.getOptions().colors[1]
                },
                series: [{
                    nullColor: '#EFEFEF',
                    tooltip: {
                        headerFormat: 'Footprints<br/>',
                        pointFormat: '{point.x:%Y}: <b>{point.value}</b>'
                    },
                    turboThreshold: Number.MAX_VALUE // #3404, remove after 4.0.5 release
                }]
            };
        },
        mounted: function() {
            this.myChart = Highcharts.chart('the-timeline', this.options);
        }
    };
    return {
        PathmapperTimelineVue: PathmapperTimelineVue
    };
});