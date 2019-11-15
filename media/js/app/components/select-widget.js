define(['jquery', 'select2'], function($, select2) {
    const SelectWidget = {
        name: 'select-widget',
        props: ['id', 'value', 'dataUrl', 'disabled',
            'minimumInput', 'criteria'],
        template: '#select2-template',
        methods: {
            url: function() {
                return Footprints.baseUrl + this.dataUrl +
                    '?' + $.param(this.criteria);
            }
        },
        watch: {
            value: function(newVal, oldVal) {
                const val = $(this.$el).val();
                if (val !== this.value) {
                    $(this.$el).val(this.value).trigger('change');
                }
            }
        },
        mounted: function() {
            $(this.$el).select2({
                escapeMarkup: function(markup) {
                    return markup;
                },
                templateResult: function(data) {
                    if (data.loading) {
                        return 'Searching...';
                    }
                    return data.html;
                },
                templateSelection: function(data) {
                    return data.text;
                },
                ajax: {
                    url: this.url,
                    dataType: 'json',
                    delay: 250,
                    processResults: function(data, params) {
                        let results = $.map(data.results, function(obj) {
                            obj.text = obj.title;
                            obj.html = obj.description;
                            return obj;
                        });
                        return {results: results};
                    }
                },
                minimumInputLength:
                    (this.minimumInput === undefined ? 1 : this.minimumInput)
            })
                .val(this.value)
                .trigger('change')
                .on('change', () => {
                    this.$emit('input', $(this.$el).val());
                });
        },
        destroyed: function() {
            $(this.$el).off().select2('destroy');
        }
    };
    return {
        SelectWidget: SelectWidget
    };
});
