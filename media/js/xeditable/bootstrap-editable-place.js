/**
Place editable input.

@class place
@extends abstractinput
**/
(function($) {
    'use strict';

    var Place = function(options) {
        this.init('place', options, Place.defaults);

        // Europe, @todo - allow this to be configurable
        this.defaultLatLng = new google.maps.LatLng(
            48.6908333333, 9.14055555556);

        this.mapOptions = {
            zoom: 3,
            center: this.defaultLatLng,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            zoomControl: true,
            zoomControlOptions: {
                style: google.maps.ZoomControlStyle.SMALL,
                position: google.maps.ControlPosition.RIGHT_BOTTOM
            },
            mapTypeControl: false,
            streetViewControl: false
        };

        this.geocoder = new google.maps.Geocoder();
    };

    //inherit from Abstract input
    $.fn.editableutils.inherit(Place, $.fn.editabletypes.abstractinput);

    $.extend(Place.prototype, {
        geocodePosition: function() {
            var self = this;
            self.geocoder.geocode({
                latLng: self.marker.getPosition(),
            }, function(responses) {
                self.$city.val('');
                self.$country.val('');
                self.$address.val('');

                if (responses && responses.length > 0) {
                    var components = responses[0].address_components;

                    for (var i = 0; i < components.length; i++) {
                        if (components[i].types.indexOf('locality') > -1) {
                            self.$city.val(components[i].long_name);
                        } else if (components[i].types
                                   .indexOf('country') > -1) {
                            self.$country.val(components[i].long_name);
                        }
                    }
                }
            });
        },
        dropMarker: function(latlng) {
            var self = this;
            if (self.marker) {
                self.marker.setMap(null);
            }
            self.marker = new google.maps.Marker({
                position: latlng,
                map: self.mapInstance,
                draggable: true,
                animation: google.maps.Animation.DROP
            });
            self.mapInstance.setCenter(latlng);
            self.geocodePosition();

            google.maps.event.addListener(self.marker, 'dragend', function() {
                self.geocodePosition();
            });
        },
        mapSearchResult: function() {
            var self = this;
            var places = self.searchBox.getPlaces();

            if (places.length > 0) {
                self.place = places[0];
                var bounds = new google.maps.LatLngBounds();

                // Create a marker for the place.
                if (self.marker) {
                    self.marker.setMap(null);
                }
                self.marker = new google.maps.Marker({
                    map: self.mapInstance,
                    title: self.place.name,
                    position: self.place.geometry.location,
                    draggable: true,
                    animation: google.maps.Animation.DROP
                });
                google.maps.event
                    .addListener(self.marker, 'dragend', function() {
                        self.geocodePosition();
                    });

                bounds.extend(places[0].geometry.location);
                self.mapInstance.fitBounds(bounds);
                self.mapInstance.setZoom(10);
                self.geocodePosition();
            }
        },
        /**
           Renders input from tpl

           @method render()
        **/
        render: function() {
            var self = this;

            self.$tpl.parents('.editable-input').addClass('wide');

            self.$city =  self.$tpl.find('input[name="city"]').first();
            self.$country =  self.$tpl.find('input[name="country"]').first();
            self.$address =  self.$tpl.find('input[name="address"]').first();
            self.mapContainer = self.$tpl.find('.map-container')[0];

            self.mapInstance = new google.maps.Map(self.mapContainer,
                                                   self.mapOptions);
            self.mapInstance.controls[google.maps.ControlPosition.TOP_LEFT]
                .push(self.$address[0]);

            // drop a marker on click
            google.maps.event
                .addListener(self.mapInstance, 'click', function(event) {
                    self.dropMarker(event.latLng);
                });

            self.searchBox = new google.maps.places.SearchBox(
                /** @type {HTMLInputElement} */(self.$address[0]));

            // Listen for the event fired when the user selects an item from the
            // pick list. Retrieve the matching places for that item.
            google.maps.event
                .addListener(self.searchBox, 'places_changed', function() {
                    self.mapSearchResult();
                });

            setTimeout(function() {
                google.maps.event.trigger(self.mapInstance, 'resize');
                self.mapInstance.setCenter(self.defaultLatLng);
            }, 0);
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

        validate: function(values) {
            if (this.marker === undefined) {
                return 'Please select a location on the map';
            } else if (this.$country.val().length < 1) {
                return 'Please specify a country';
            }
        },

        /**
           Returns value of input.

           @method input2value()
        **/
        input2value: function() {
            var values = {};
            values.error = this.validate();

            if (this.marker !== undefined) {
                values.latitude = this.marker.getPosition().lat();
                values.longitude = this.marker.getPosition().lng();
            }
            values.city = this.$city.val();
            values.country = this.$country.val();
            return values;
        },

        /**
           @method value2submit(value)
           @param {mixed} value
           @returns {mixed}
        **/
        value2submit: function(value) {
            return {
                position: this.marker.getPosition().toUrlValue(),
                city: this.$city.val(),
                country: this.$country.val()
            };
        },

        /**
           Activates input: sets focus on the first field.

           @method activate()
        **/
        activate: function() {
            this.$address.focus();
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
        error: function(response, newValue) {
            if (response.status === 500) {
                return 'Service unavailable. Please try later.';
            } else {
                return response.responseText;
            }
        }
    });

    Place.defaults = $.extend({}, $.fn.editabletypes.abstractinput.defaults, {
        inputclass: ''
    });

    $.fn.editabletypes.place = Place;

}(window.jQuery));
