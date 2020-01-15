define(['jquery', 'utils'], function($, layer, utils) {
    const PathmapperTableVue = {
        props: ['value'],
        template: '#pathmapper-table-template',
        data: function() {
            return {
                'page': {'number': 1},
                'totalPages': 0,
                'footprints': [],
                'baseUrl': Footprints.baseUrl
            };
        },
        methods: {
            changePage: function(pg) {
                this.page.number = pg;
                this.updateLayers();
            },
            url: function() {
                return Footprints.baseUrl + 'pathmapper/table/';
            },
            updateLayers: function() {
                const ctx = {
                    layers: JSON.stringify(this.value)
                };

                $.ajax({
                    type: 'POST',
                    url: this.url() + '?page=' + this.page.number,
                    dataType: 'json',
                    data: ctx
                }).done((data) => {
                    this.page = data.page;
                    this.totalPages = data.num_pages;
                    this.footprints = $.extend(true, [], data.footprints);
                    console.log(this.footprints);
                });
            }
        },
        created: function() {
            this.$watch('value', this.updateLayers, {deep: true});
            this.updateLayers();
        }
    };
    return {
        PathmapperTableVue: PathmapperTableVue
    };
});
