define(['jquery'], function($) {
    const Select2Vue = {
        props: ['options', 'value', 'dataUrl'],
        template: '#select2-template',
        mounted: function () {
            var vm = this;

            // init select2
            $(this.$el)
                .select2({
                    ajax: {
                        url: this.dataUrl,
                        dataType: 'json'
                      }
                 })
                .val(this.value)
                .trigger('change')
                .on('change', function () {
                    vm.$emit('input', this.value)
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
        destroyed: function () {
            $(this.$el).off().select2('destroy')
        }
    });
    return {
        Select2Vue: Select2Vue
    };
});
