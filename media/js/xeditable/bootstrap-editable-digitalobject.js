(function ($) {
    "use strict";
    
    var DigitalObject = function (options) {
        this.init('digitalobject', options, DigitalObject.defaults);
    };

    //inherit from Abstract input
    $.fn.editableutils.inherit(DigitalObject, $.fn.editabletypes.abstractinput);

    $.extend(DigitalObject.prototype, {
        initializeUploader: function(browseButton, fileList) {
            var uploader = new plupload.Uploader({
                browse_button: browseButton,
                url: '/digitalobject/add/',
                max_retries: 3,
                multi_selection: false,
                runtimes: 'html5,flash,silverlight',
                headers: {
                    'X-Requested-With' : 'XMLHttpRequest'
                }, 
                flash_swf_url: '/media/js/plupload/Moxie.swf',
                silverlight_xap_url: '/media/js/js/Moxie.xap',
                filters: {
                    mime_types: [
                        {title: "Image files", extensions: "jpg,jpeg,png,gif,bmp"}
                    ],
                    max_file_size: "7500000"
                }
            });

            uploader.init();
            
            return uploader;
        },
        filesAdded: function(up, files) {
            while (this.uploader.files.length > 1) {
                this.uploader.removeFile(this.uploader.files[0]);
            }

            this.$tpl.find('.alert').hide();
            
            var html = '';
            plupload.each(files, function(file) {
                html += '<li id="' + file.id + '">' + file.name + ' (' + plupload.formatSize(file.size) + ') <b></b></li>';
            });
            jQuery(this.$list).html(html);
        },
        upload: function(evt, params) {
            evt.stopPropagation();
            evt.preventDefault();
            
            var rv = this.validate(this.value2submit());
            if (typeof rv === 'string') {
                jQuery('.editable-digital-object').parents('.control-group').addClass('has-error');
                jQuery('.editable-error-block').html(rv).show();
            } else {
                this.uploader.setOption('multipart_params', params);
                this.uploader.start();
            }
            
            return false;
        },
        uploadComplete: function(up, data, r) {
            // wait just for a second
            setTimeout(function() {
                jQuery("button.editable-submit").click();
            }, 500);
        },
        uploadError: function(up, err) {
            var $elt;
            if (err.code === -600) {
                $elt =  this.$tpl.find('.filesize.alert')[0];
                jQuery($elt).fadeIn();
            } else {
                $elt =  this.$tpl.find('.general.alert')[0];
                jQuery($elt).fadeIn();                
            }
        },
        uploadProgress: function(up, file) {
            var fileId = document.getElementById(file.id);
            var elt = fileId.getElementsByTagName('b')[0];
            elt.innerHTML = '<span>' + file.percent + "%</span>";
        },
        validate: function(values) {
            if (values.count < 1) {
                return 'Use the Browse button to select an image file';
            } else if (!values.hasOwnProperty('name') || values.name.length < 1) {
                return 'Please enter a short description';
            }
        },
        
        /**
        Renders input from tpl

        @method render() 
        **/        
        render: function() {
            var self = this;

            this.$browse =  this.$tpl.find('button.browse')[0];
            this.$list =  this.$tpl.find('ul.filelist')[0];
            this.$description =  this.$tpl.find('input[name="description"]')[0];

            // hack: steal submit from EditableForm
            // Hide the submit button, make the input div wider
            jQuery("button.editable-submit").hide();
            jQuery(this.$browse).parents('.editable-input').addClass('wide');

            this.uploader = this.initializeUploader(this.$browse, this.$list);

            // gather additional submit params
            var params = $(this.options.scope).data('params');
            jQuery('button.editable-upload').on('click', function(evt) {
                params.description =  jQuery(self.$description).val();
                return self.upload(evt, params);
            });
            
            this.uploader.bind('UploadComplete', this.uploadComplete);
            this.uploader.bind('FilesAdded', function(up, files) {
                return self.filesAdded(up, files);
            });
            this.uploader.bind('UploadProgress', this.uploadProgress);
            this.uploader.bind('Error', this.uploadError, this);
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
           return this.value2submit();
       },
       
       /**
           @method value2submit(value) 
           @param {mixed} value
           @returns {mixed}
       **/
       value2submit: function(value) {
           return {
               'count': this.uploader.files.length,
               'name': jQuery(this.$description).val()
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
           this.$input.keydown(function (e) {
                if (e.which === 13) {
                    $(this).closest('form').submit();
                }
           });
       },
       error: function(response, newValue) {
           if (response.status === 500) {
               return 'Service unavailable. Please try later.';
           } else {
               return response.responseText;
           }
       }
    });

    DigitalObject.defaults = $.extend({}, $.fn.editabletypes.abstractinput.defaults, {
        inputclass: ''
    });

    $.fn.editabletypes.digitalobject = DigitalObject;

}(window.jQuery));