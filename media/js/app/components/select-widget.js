define(['jquery', 'select2'], function($, select2) {
    const SelectWidget = {
        name: 'select-widget',
        props: ['id', 'name', 'value', 'dataUrl', 'disabled',
            'minimumInput', 'criteria', 'searchFor'],
        template: '#select2-template',
        methods: {
            context: function(params) {
                let ctx = $.extend(true, params, this.criteria);
                ctx.q = params.term;
                ctx.page = params.page || 1;
                ctx.searchFor = this.searchFor;
                return ctx;
            },
            selected: function() {
                return $(this.$el).select2('data')[0].title;
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
                    // delay: 250,
                    processResults: function(data, params) {
                        let results = $.map(data.results, function(obj) {
                            obj.text = obj.title || obj.search_title ||
                                obj.display_title || obj.display_name ||
                                obj.canonical_name;
                            obj.html = obj.description || obj.search_title ||
                                obj.display_title || obj.canonical_name;
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
            }).on('change', () => {
                this.$emit('input', $(this.$el).val());
            });

            if (this.value) {
                const ctx = {searchFor: this.searchFor};
                ctx['selected'] = this.value;
                $.ajax({
                    type: 'GET',
                    url: this.url(),
                    dataType: 'json',
                    data: ctx
                }).done((data) => {
                    if (data.results.length > 0) {
                        const item = data.results[0];
                        const title = item.title || item.display_title ||
                            item.canonical_name;
                        const value = item.id;
                        const option = new Option(title, value, true, true);
                        $(this.$el).append(option).trigger('change');
                        $(this.$el).val(value);
                    }
                });
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
