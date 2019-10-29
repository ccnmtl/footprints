define(['jquery', 'select2'], function($, select2) {
    const SelectWidget = {
        name: 'select-widget',
        props: ['options', 'value', 'dataUrl', 'id'],
        template: '#select-template',
        mounted: function() {
            var vm = this;

            $(this.$el).select2({
                ajax: {
                    url: Footprints.baseUrl + this.dataUrl,
                    dataType: 'json',
                    delay: 250,
                    processResults: function(data, params) {
                        let results = $.map(data, function(obj) {
                            obj.text = obj.title;
                            return obj;
                        });
                        return {results: results};
                    },
                    cache: true
                },
                minimumInputLength: 1
            });

            $(this.$el)
                .val(this.value)
                .trigger('change')
                .on('change', function() {
                    vm.$emit('input', this.value);
                });
        },
        watch: {
            value: function(value) {
                // update value
                $(this.$el).val(value).trigger('change');
            },
            options: function(options) {
                // update options
                $(this.$el).empty().select2({data: options});
            }
        },
        destroyed: function() {
            $(this.$el).off().select2('destroy');
        }
    };
    return {
        SelectWidget: SelectWidget
    };
});
