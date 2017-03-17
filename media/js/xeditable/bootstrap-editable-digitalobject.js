/* global csrftoken: true, S3Upload: true */
(function($) {
    'use strict';

    window.s3_upload = function() {
        var s3upload = new S3Upload({
            file_dom_selector: 'file',
            s3_sign_put_url: '/sign_s3/',
            s3_object_name: encodeURIComponent($('#file')[0].value),
            onProgress: function(percent, message) {
                $('#uploaded-status').html(message + ' ' + percent + '%');
            },
            onFinishS3Put: function(url) {
                $('#uploaded-url').val(url);
            },
            onError: function(status) {
                $('#uploaded-status').html('Upload error: ' + status);
            }
        });
    };

    var DigitalObject = function(options) {
        this.init('digitalobject', options, DigitalObject.defaults);
    };

    //inherit from Abstract input
    $.fn.editableutils.inherit(DigitalObject, $.fn.editabletypes.abstractinput);

    $.extend(DigitalObject.prototype, {
        validate: function() {
            var url = this.$url.val();
            if (!url || url.length < 1) {
                return 'Use the Browse button to select an image file';
            }

            var description = this.$description.val();
            if (!description || description.length < 1) {
                return 'Please enter a short description';
            }
        },

        /**
        Renders input from tpl

        @method render()
        **/
        render: function() {
            this.$url = this.$tpl.find('input[name="url"]').first();
            this.$description =
                this.$tpl.find('input[name="description"]').first();
        },

        /**
        Default method to show value in element. Can be overwritten by display option.

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
          Converts string to value. Used for reading value from 'data-value' attribute.

          @method str2value(str)
        */
        str2value: function(str) {
            /*
              this is mainly for parsing value defined in data-value attribute.
              If you will always set value by javascript, no need to overwrite it
            */
            return str;
        },

        /**
           Sets value of input.

           @method value2input(value)
           @param {mixed} value
        **/
        value2input: function(value) {
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
            return {
                error: this.validate(),
                url: this.$url.val(),
                name: this.$description.val()
            };
        },

        /**
           Activates input: sets focus on the first field.

           @method activate()
        **/
        activate: function() {
            this.$description.focus();
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
        },
    });

    DigitalObject.defaults = $.extend(
        {}, $.fn.editabletypes.abstractinput.defaults,
        {inputclass: ''});

    $.fn.editabletypes.digitalobject = DigitalObject;

}(window.jQuery));
