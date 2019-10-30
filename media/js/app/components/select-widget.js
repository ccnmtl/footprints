define(['jquery', 'select2'], function($, select2) {
    const SelectWidget = {
        name: 'select-widget',
        props: ['value', 'dataUrl', 'id'],
        template: '#select-template',
        mounted: function() {
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
