/**
Place editable input.

@class place
@extends abstractinput
@final
@example
<a href="#" data-type="name" data-pk="1">Fred Rogers</a>
<script>
$(function(){
    $('#place').editable({
        url: '/post',
        title: 'Enter the place's name',
        value: {
            name: "Fred Rogers"
        }
    });
});
</script>
**/
(function ($) {
    "use strict";
    
    var Place = function (options) {
        this.init('place', options, Place.defaults);
    };

    //inherit from Abstract input
    $.fn.editableutils.inherit(Place, $.fn.editabletypes.abstractinput);

    $.extend(Place.prototype, {
        /**
        Renders input from tpl

        @method render() 
        **/        
        render: function() {
           var self = this;

           this.$continent = this.$tpl.find('select[name="continent"]');
           this.$country =  this.$tpl.find('input[name="country"]');
           this.$city =  this.$tpl.find('input[name="city"]');
           this.$latitude =  this.$tpl.find('input[name="latitude"]');
           this.$longitude =  this.$tpl.find('input[name="longitude"]');
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
       },

       
       /**
        Returns value of input.
        
        @method input2value() 
       **/          
       input2value: function() { 
           return $.param({
               continent: this.$continent.val(),
               country: this.$country.val(),
               city: this.$city.val(),
               latitude: this.$latitude.val(),
               longitude: this.$longitude.val()
           });
       },
       
       /**
           @method value2submit(value) 
           @param {mixed} value
           @returns {mixed}
       **/
       value2submit: function(value) {
           return {
               continent: this.$continent.val(),
               country: this.$country.val(),
               city: this.$city.val(),
               latitude: this.$latitude.val(),
               longitude: this.$longitude.val()
            }
       },
       
        /**
        Activates input: sets focus on the first field.
        
        @method activate() 
       **/        
       activate: function() {
            this.$input.filter('[name="continent"]').focus();
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

    Place.defaults = $.extend({}, $.fn.editabletypes.abstractinput.defaults, {
        tpl: jQuery('#xeditable-place-form').html(),
        inputclass: ''
    });

    $.fn.editabletypes.place = Place;

}(window.jQuery));