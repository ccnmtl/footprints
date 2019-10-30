define(['jquery', 'select2'], function($, select2) {
    const SelectWidget = {
        name: 'select-widget',
        props: ['id', 'value', 'dataUrl', 'disabled'],
        template: '#select-template',
        mounted: function() {
            $(this.$el).select2({
                escapeMarkup: function(markup) {
                    return markup;
                },
                templateResult: function(data) {
                    return data.html;
                },
                templateSelection: function(data) {
                    return data.text;
                },
                ajax: {
                    url: Footprints.baseUrl + this.dataUrl,
                    dataType: 'json',
                    delay: 250,
                    processResults: function(data, params) {
                        let results = $.map(data, function(obj) {
                            obj.text = obj.title;
                            obj.html = obj.description;
                            return obj;
                        });
                        return {results: results};
                    },
                    cache: true
                },
                minimumInputLength: 1
            });

            // trigger update if value changes
            $(this.$el).on('change', () => {
                this.$emit('input', $(this.$el).val());
            });

            // set original value if needed
            if (this.value) {
                $(this.$el).val(this.value);
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
