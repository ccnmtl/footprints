define(['jquery', 'utils'], function($, layer, utils) {
    const PathmapperTableVue = {
        props: ['value'],
        template: '#pathmapper-table-template',
        data: function() {
            return {
                'page': {'number': 1, 'nextPage': null, 'prevPage': null},
                'totalPages': 0,
                'footprints': [],
                'baseUrl': Footprints.baseUrl,
                'pageSize': 15
            };
        },
        methods: {
            hasNext: function() {
                return this.page.nextPage;
            },
            hasPrev: function() {
                return this.page.prevPage;
            },
            changePage: function(pg) {
                this.page.number = pg;
                this.updateLayers();
            },
            url: function(pageNumber) {
                return Footprints.baseUrl +
                    'pathmapper/table/?page=' + pageNumber;
            },
            updateLayers: function() {
                const ctx = {
                    layers: JSON.stringify(this.value)
                };

                $.ajax({
                    type: 'POST',
                    url: this.url(this.page.number),
                    dataType: 'json',
                    data: ctx
                }).done((data) => {
                    this.page.nextPage = utils.parsePageNumber(data.next);
                    this.page.prevPage = utils.parsePageNumber(data.previous);
                    this.totalPages = Math.ceil(data.count / this.pageSize);
                    this.footprints = $.extend(true, [], data.results);
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
