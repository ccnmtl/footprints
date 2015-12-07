(function($) {
    'use strict';

    var ExtendedDateTimeFormat = function(options) {
        this.init('ExtendedDateTimeFormat', options,
                ExtendedDateTimeFormat.defaults);
    };

    //inherit from Abstract input
    $.fn.editableutils.inherit(ExtendedDateTimeFormat,
            $.fn.editabletypes.abstractinput);

    $.extend(ExtendedDateTimeFormat.prototype, {
        /**
        Renders input from tpl

        @method render()
        **/
        render: function() {
            var self = this;

            this.$tpl.parents('.editable-input').addClass('wide');

            this.$millenium1 = this.$tpl.find('input[name="millenium1"]');
            this.$century1 = this.$tpl.find('input[name="century1"]');
            this.$decade1 = this.$tpl.find('input[name="decade1"]');
            this.$year1 = this.$tpl.find('input[name="year1"]');
            this.$month1 = this.$tpl.find('select[name="month1"]');
            this.$day1 = this.$tpl.find('input[name="day1"]');
            this.$approximate1 = this.$tpl.find('input[name="approximate1"]');
            this.$uncertain1 = this.$tpl.find('input[name="uncertain1"]');

            this.$millenium2 = this.$tpl.find('input[name="millenium2"]');
            this.$century2 = this.$tpl.find('input[name="century2"]');
            this.$decade2 = this.$tpl.find('input[name="decade2"]');
            this.$year2 = this.$tpl.find('input[name="year2"]');
            this.$month2 = this.$tpl.find('select[name="month2"]');
            this.$day2 = this.$tpl.find('input[name="day2"]');
            this.$approximate2 = this.$tpl.find('input[name="approximate2"]');
            this.$uncertain2 = this.$tpl.find('input[name="uncertain2"]');

            this.$tpl.find('[data-toggle="popover"]').popover({
                'html': true,
                'trigger': 'focus',
                'placement': 'bottom'
            });

            this.$tpl.find('[data-toggle="tooltip"]').tooltip();

            this.$tpl.find('.toggle-next-row').click(function(evt) {
                evt.preventDefault();
                jQuery(this).parents('tr').next().toggle('fast');
                jQuery(this).toggleClass('minus');
                return false;
            });

            jQuery('.edtf-entry').keypress(function() {
                var maxlength = parseInt(jQuery(this).attr('maxlength'), 10);
                if (this.value.length >= maxlength) {
                    return false;
                }
            });
        },

        /**
           Default method to show value in element.
           Can be overwritten by display option.

           @method value2html(value, element)
        **/
        value2html: function(value, element) {
        },

        /**
           Gets value from element's html

           @method html2value(html)
        **/
        html2value: function(html) {
            return null;
        },

        /**
           Converts value to string.
           It is used in internal comparing (not for sending to server).

           @method value2str(value)
        **/
        value2str: function(value) {
            var str = '';
            if (value) {
                for (var k in value) {
                    str = str + k + ':' + value[k] + ';';
                }
            }
            return str;
        },

        /*
          Converts string to value. Used for reading value
          from 'data-value' attribute.

          @method str2value(str)
        */
        str2value: function(str) {
            /*
              this is mainly for parsing value defined in data-value attribute.
              If you will always set value by javascript,
              no need to overwrite it
            */
            return str;
        },

        /**
           Sets value of input.

           @method value2input(value)
           @param {mixed} value
        **/
        value2input: function(value) {
            if (value && typeof value === 'object') {
                // Populate the appropriate values on the active form
                this.$millenium1.val(value.millenium1);
                this.$century1.val(value.century1);
                this.$decade1.val(value.decade1);
                this.$year1.val(value.year1);
                this.$month1.val(value.month1);
                this.$day1.val(value.day1);
                if (value.approximate1) {
                    this.$approximate1.attr('checked', true);
                }
                if (value.uncertain1) {
                    this.$uncertain1.attr('checked', true);
                }

                this.$millenium2.val(value.millenium2);
                this.$century2.val(value.century2);
                this.$decade2.val(value.decade2);
                this.$year2.val(value.year2);
                this.$month2.val(value.month2);
                this.$day2.val(value.day2);
                if (value.approximate2) {
                    this.$approximate2.attr('checked', true);
                }
                if (value.uncertain2) {
                    this.$uncertain2.attr('checked', true);
                }
            }
        },

        validate: function() {
            return this.$tpl.find('.required').length > 0 ?
                'Please fill in all required fields' : '';
        },

        /**
           Returns value of input.

           @method input2value()
        **/
        input2value: function() {
            return this.value2submit();
        },

        /**
           @method value2submit(value)
           @param {mixed} value
           @returns {mixed}
        **/
        value2submit: function(value) {
            var error = this.validate();

            return {
                'errors': error,
                'is_range': this.$millenium2.is(':visible'),
                'millenium1': this.$millenium1.val(),
                'data.century1': this.$century1.val(),
                'data.decade1': this.$decade1.val(),
                'data.year1': this.$year1.val(),
                'data.month1': this.$month1.val(),
                'data.day1': this.$day1.val(),
                'data.approximate1': this.$approximate1.is(':checked'),
                'data.uncertain1': this.$uncertain1.is(':checked'),

                'data.millenium2': this.$millenium2.val(),
                'data.century2': this.$century2.val(),
                'data.decade2': this.$decade2.val(),
                'data.year2': this.$year2.val(),
                'data.month2': this.$month2.val(),
                'data.day2': this.$day2.val(),
                'data.approximate2': this.$approximate2.is(':checked'),
                'data.uncertain2': this.$uncertain2.is(':checked')
            };
        },

        /**
           Activates input: sets focus on the first field.

           @method activate()
        **/
        activate: function() {
        },

        /**
           Attaches handler to submit form in case of 'showbuttons=false' mode

           @method autosubmit()
        **/
        autosubmit: function() {
            this.$input.keydown(function(e) {
                if (e.which === 13) {
                    $(this).closest('form').submit();
                }
            });
        }
    });

    ExtendedDateTimeFormat.defaults = $.extend(
        {}, $.fn.editabletypes.abstractinput.defaults,
        {inputclass: ''});

    $.fn.editabletypes.edtf = ExtendedDateTimeFormat;

}(window.jQuery));
