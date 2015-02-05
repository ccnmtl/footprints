/**
Actor editable input.

@class actor
@extends abstractinput
@final
@example
<a href="#" data-type="name" data-pk="1">Fred Rogers</a>
<script>
$(function(){
    $('#actor').editable({
        url: '/post',
        title: 'Enter the actor's name',
        value: {
            name: "Fred Rogers"
        }
    });
});
</script>
**/
(function ($) {
    "use strict";
    
    var Actor = function (options) {
        var template = jQuery(options.scope).data("template");
        Actor.defaults.tpl = jQuery(template).html(); 
        this.init('actor', options, Actor.defaults);
    };

    //inherit from Abstract input
    $.fn.editableutils.inherit(Actor, $.fn.editabletypes.abstractinput);

    $.extend(Actor.prototype, {
        /**
        Renders input from tpl

        @method render() 
        **/        
        render: function() {
           var self = this;

           this.$input = this.$tpl.find('input[name="person-autocomplete"]');
           this.$roleselect = this.$tpl.find('select[name="role"]');
           this.$actorname =  this.$tpl.find('input[name="actor-name"]');
           jQuery(this.$input).autocomplete({
               change: function(event, ui) {
                   self.$input.data('instance', '');
                   return true;
               },
               select: function (event, ui) {
                   self.$input.data('instance', ui.item.object_id);
                   return true;
               },
               source: function(request, response) {
                   jQuery.ajax({
                       url: "/api/name/",
                       dataType: "jsonp",
                       data: {
                           q: request.term
                       },
                       success: function(data) {
                           var names = [];
                           for (var i=0; i < data.length; i++) {
                               names.push({
                                   object_id: data[i].object_id,
                                   label: data[i].name
                               });
                           }
                           response(names);
                       }
                   });
               },
               minLength: 2,
               open: function() {
                   jQuery(this).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
               },
               close: function() {
                   jQuery(this).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
               }
           });
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
              name: this.$input.val(),
              role: this.$roleselect.val(),
              alias: this.$actorname.val()
           });
       },
       
       /**
           @method value2submit(value) 
           @param {mixed} value
           @returns {mixed}
       **/
       value2submit: function(value) {
           return {
               person_name: this.$input.val(),
               person_id: this.$input.data('instance'),
               role: this.$roleselect.val(),
               alias: this.$actorname.val()
            }
       },
       
        /**
        Activates input: sets focus on the first field.
        
        @method activate() 
       **/        
       activate: function() {
            this.$input.filter('[name="person-autocomplete"]').focus();
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

    Actor.defaults = $.extend({}, $.fn.editabletypes.abstractinput.defaults, {
        tpl: undefined,
        inputclass: ''
    });

    $.fn.editabletypes.actor = Actor;

}(window.jQuery));