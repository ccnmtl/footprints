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
                if ($('.btn-play-timeline').hasClass('pause')) {
                    $('.btn-play-timeline').removeClass('pause');
                } else {
                    $('.btn-play-timeline').addClass('pause');
                }
            },
            closeTimeline: function() {
                $('#widget-timeline').removeClass('timeline-expanded');
                $('#widget-timeline').addClass('timeline-collapsed');
                $('#timeline-launch').html('View Timeline');
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
                    if (this.value.length < 1) {
                        this.closeTimeline();
                    }
                });
            }
        },
        created: function() {
            this.$watch('value', this.updateLayers, {deep: true});
            this.updateLayers();

            this.options = {
                chart: {
                    type: 'heatmap',
                    height: '40px',
                    spacing: [0, 0, 0, 0],
                    plotBackgroundColor: '#fafafa',
                    plotBorderColor: '#dddddd',
                    plotBorderWidth: 2,
                    style: {
                        fontFamily: '"Asap", Helvetica, Arial, sans-serif'
                    }
                },
                credits: {
                    enabled: false
                },
                title: {
                    text: null
                },
                xAxis: {
                    type: 'datetime',
                    labels: {
                        align: 'left',
                        x: 2,
                        y: 14,
                        format: '{value:%Y}',
                        style: {
                            color: '#212529',
                            fontSize: '0.6875rem'
                        }
                    },
                    tickLength: 15,
                    tickColor: '#999999'
                },
                yAxis: {
                    visible: false,
                    minPadding: 0,
                    maxPadding: 0,
                    startOnTick: false,
                    endOnTick: false
                },
                legend: {
                    enabled: false
                },
                colorAxis: {
                    min: 0,
                    minColor: '#edb69c',
                    maxColor: '#56260f',
                    visible: false
                },
                series: [{
                    nullColor: '#EFEFEF',
                    colsize: 365 * 24 * 36e5, // one day
                    tooltip: {
                        headerFormat: '<b>Events in ',
                        pointFormat: '{point.x:%Y}:</b> {point.value}'
                    },
                    data: []
                }]
            };
        },
        mounted: function() {
            this.chart = Highcharts.chart('heatmap', this.options);
        }
    };
    return {
        PathmapperTimelineVue: PathmapperTimelineVue
    };
});