define(['jquery', 'select2'], function($, select2) {
    const SelectWidget = {
        name: 'select-widget',
        props: ['id', 'name', 'value', 'dataUrl', 'disabled',
            'minimumInput', 'criteria'],
        template: '#select2-template',
        methods: {
            context: function(params) {
                let ctx = $.extend(true, params, this.criteria);
                ctx.q = params.term;
                ctx.name = this.name;
                ctx.page = params.page || 1;
                return ctx;
            },
            url: function() {
                return Footprints.baseUrl + this.dataUrl;
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
                allowClear: true,
                placeholder: '-----',
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
                    data: this.context,
                    delay: 250,
                    processResults: function(data, params) {
                        let results = $.map(data.results, function(obj) {
                            obj.text = obj.title || obj.search_title ||
                                obj.display_title;
                            obj.html = obj.description || obj.search_title ||
                                obj.display_title;
                            return obj;
                        });

                        const more = Object.prototype.hasOwnProperty.call(
                            data, 'next') && data.next !== null;
                        return {
                            results: results,
                            pagination: {more: more}
                        };
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
