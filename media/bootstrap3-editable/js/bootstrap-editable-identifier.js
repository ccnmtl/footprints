(function ($) {
    "use strict";
    
    var Identifier = function (options) {
        this.init('identifier', options, Identifier.defaults);
    };

    //inherit from Abstract input
    $.fn.editableutils.inherit(Identifier, $.fn.editabletypes.abstractinput);

    $.extend(Identifier.prototype, {
        /**
        Renders input from tpl

        @method render() 
        **/        
        render: function() {
           var self = this;

           this.$input = this.$tpl.find('input[name="identifier"]');
           this.$type = this.$tpl.find('select[name="standardized-identifier"]');
           
           var value = jQuery(this.options.scope).data('value');
           this.value2input(value);
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
               for(var k in value) {
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
           this.$input.val(value.identifier);
           this.$type.val(value.identifier_type);
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
               identifier: this.$input.val(),
               identifier_type: this.$type.val()
            }
       },
       
        /**
        Activates input: sets focus on the first field.
        
        @method activate() 
       **/        
       activate: function() {
            this.$input.filter('[name="identifier"]').focus();
       },  
       
       /**
        Attaches handler to submit form in case of 'showbuttons=false' mode
        
        @method autosubmit() 
       **/       
       autosubmit: function() {
           this.$input.keydown(function (e) {
                if (e.which === 13) {
                    $(this).closest('form').submit();
                }
           });
       }       
    });

    Identifier.defaults = $.extend({}, $.fn.editabletypes.abstractinput.defaults, {
        inputclass: ''
    });

    $.fn.editabletypes.identifier = Identifier;

}(window.jQuery));