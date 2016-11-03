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
                jQuery(this).parents('tr').next().toggle();
                jQuery(this).toggleClass('minus');
                return false;
            });

            var $elts = this.$tpl.find('.edtf-entry');
            $elts.keypress(function(evt) {
                var charCode = (evt.which) ? evt.which : event.keyCode;
                if (charCode >= 48 && charCode <= 57) {
                    var len = parseInt(jQuery(this).attr('maxlength'), 10);
                    if (this.value.length >= len) {
                        return false;
                    }
                }
            });

            $elts.filter('.jump').keyup(function(evt) {
                var charCode = (evt.which) ? evt.which : event.keyCode;
                if (charCode >= 48 && charCode <= 57 &&
                        jQuery(this).val().length > 0) {
                    jQuery(this).nextAll('input').first().focus();
                }
            });

            $elts.filter('input[type="number"]').keyup(function() {
                self.renderDateDisplay();
            });
            $elts.filter('select').change(function() {
                self.renderDateDisplay();
            });
            $elts.filter('input[type="checkbox"]').click(function() {
                self.renderDateDisplay();
            });
        },
        hasValue: function() {
            var value = jQuery(this).val();
            return value && value.length > 0;
        },
        markRequired: function() {
            var self = this;

            this.$tpl.find('.date-display').html('');
            jQuery('.edtf-entry').removeClass('required');

            this.$tpl.parents('.form-group')
                     .removeClass('has-error')
                     .find('.help-block').hide();

            if (this.$millenium1.val().length < 1 ||
                    this.$millenium1.val() < 1) {
                this.$millenium1.addClass('required');
            }

            if (this.$millenium2.is(':visible') &&
                    (this.$millenium2.val().length < 1 ||
                     this.$millenium2.val() < 1)) {
                this.$millenium2.addClass('required');
            }

            // for date1 && date 2
            this.$tpl.find('.date-display-row').each(function() {
                // grab rightmost edtf-entry field with a value
                // then verify the specified dependencies have values
                // mark class with "required" if no value is found
                var elts = jQuery(this).find('input[type="number"],select')
                    .filter(self.hasValue).get().reverse();
                var selector = jQuery(jQuery(elts).first()).data('required');
                jQuery(this).find(selector)
                            .not(self.hasValue).each(function() {
                                jQuery(this).addClass('required');
                            });
            });
        },
        renderDateDisplay: function() {
            var msg = this.validate();
            if (msg.length > 0) {
                this.$tpl.parents('.form-group')
                         .addClass('has-error')
                         .find('.help-block')
                         .html('Please fill out all required fields').show();
                return;
            }

            var self = this;
            var data = this.value2submit();
            jQuery.ajax({
                url: '/date/display/',
                type: 'post',
                data: data,
                success: function(data) {
                    self.$tpl.find('.date-display').html(data.display);
                },
                error: function() {
                    self.$tpl.find('.date-display').html('invalid');
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
            this.markRequired();
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
                'century1': this.$century1.val(),
                'decade1': this.$decade1.val(),
                'year1': this.$year1.val(),
                'month1': this.$month1.val(),
                'day1': this.$day1.val(),
                'approximate1': this.$approximate1.is(':checked'),
                'uncertain1': this.$uncertain1.is(':checked'),

                'millenium2': this.$millenium2.val(),
                'century2': this.$century2.val(),
                'decade2': this.$decade2.val(),
                'year2': this.$year2.val(),
                'month2': this.$month2.val(),
                'day2': this.$day2.val(),
                'approximate2': this.$approximate2.is(':checked'),
                'uncertain2': this.$uncertain2.is(':checked')
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
