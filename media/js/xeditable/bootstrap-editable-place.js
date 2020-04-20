/* eslint security/detect-object-injection: 0 */

/**
Place editable input.

@class place
@extends abstractinput
**/
(function($) {
    'use strict';

    var Place = function(options) {
        this.init('place', options, Place.defaults);

        this.rows = 20;
        this.searchUrl = 'https://secure.geonames.org/search?' +
            'featureClass=P&featureClass=A&' +
            'style=LONG&maxRows=' + this.rows + '&' +
            'username=' + Footprints.geonamesKey + '&type=json';

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
            streetViewControl: false,
            fullscreenControl: false,
            controlSize: 28
        };

        this.geocoder = new google.maps.Geocoder();
    };

    //inherit from Abstract input
    $.fn.editableutils.inherit(Place, $.fn.editabletypes.abstractinput);

    $.extend(Place.prototype, {
        markupName: function(obj) {
            let str = '<div class="separator"><div>' + obj.name;
            if (obj.adminName1) {
                str += ', ' + obj.adminName1;
            }
            str += '</div><div>' + obj.countryName + '</div></div>';
            return str;
        },
        selectName: function(obj) {
            let str = obj.name;
            if (obj.adminName1) {
                str += ', ' + obj.adminName1;
            }
            str += ', ' + obj.countryName;
            return str;
        },
        onPlaceClear: function() {
            this.$country.val('');
            this.$city.val('');
            if (this.marker) {
                this.marker.setMap(null);
            }
        },
        onPlaceChange: function() {
            const value = this.$geoName.select2('data')[0];

            this.$country.val(value.countryName);
            if (value.name !== value.countryName) {
                this.$city.val(value.name);
            }

            let latlng = new google.maps.LatLng(value.lat, value.lng);

            // Create a marker for the place.
            if (this.marker) {
                this.marker.setMap(null);
            }
            this.marker = new google.maps.Marker({
                map: this.mapInstance,
                title: value.text,
                position: latlng,
                animation: google.maps.Animation.DROP
            });

            let bounds = new google.maps.LatLngBounds();
            bounds.extend(latlng);
            this.mapInstance.fitBounds(bounds);
            this.mapInstance.setZoom(10);
        },
        /**
           Renders input from tpl

           @method render()
        **/
        render: function() {
            var self = this;

            this.$tpl.parents('.editable-input').addClass('wide');

            this.$city =
                this.$tpl.find('input[name="city"]').first();
            this.$country =
                this.$tpl.find('input[name="country"]').first();
            this.mapContainer =
                this.$tpl.find('.map-container')[0];

            this.mapInstance = new google.maps.Map(
                this.mapContainer,
                this.mapOptions);

            this.$geoName = this.$tpl.find('[name="geoname"]').first();
            this.$geoName.select2({
                allowClear: true,
                placeholder: 'Search for a place...',
                escapeMarkup: function(markup) {
                    return markup;
                },
                templateResult: function(data) {
                    if (data.loading) {
                        return 'Searching...';
                    }
                    return data.html;
                },
                templateSelection: function(data) {
                    return data.text;
                },
                ajax: {
                    url: this.searchUrl,
                    dataType: 'json',
                    data: function(params) {
                        const page = (params.page - 1) || 0;
                        return {
                            q: params.term,
                            startRow: page * self.rows
                        };
                    },
                    processResults: function(data, params) {
                        let results = $.map(data.geonames, function(obj) {
                            obj.id = obj.geonameId;
                            obj.text = self.selectName(obj);
                            obj.html = self.markupName(obj);
                            return obj;
                        });

                        const page = params.page || 1;
                        const rows = page * self.rows;
                        return {
                            results: results,
                            pagination: {more: rows < data.totalResultsCount}
                        };
                    }
                },
                minimumInputLength: 3
            }).on('select2:select', () => {
                this.onPlaceChange();
            }).on('select2:clear', () => {
                this.onPlaceClear();
            });

            // eslint-disable-next-line scanjs-rules/call_setTimeout
            setTimeout(() => {
                google.maps.event.trigger(this.mapInstance, 'resize');
                this.mapInstance.setCenter(this.defaultLatLng);
            }, 0);
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
                var keys = Object.keys(value);
                keys.forEach(function(k) {
                    str = str + k + ':' + k + ';';
                });
            }
            return str;
        },

        /*
          Converts string to value.
          Used for reading value from 'data-value' attribute.

          @method str2value(str)
        */
        str2value: function(str) {
            /*
              this is mainly for parsing value defined in data-value
              attribute. If you will always set value by javascript,
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
            this.$geoName.focus();
        },

        /**
           Attaches handler to submit form in case of
           'showbuttons=false' mode

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

    Place.defaults =
        $.extend({}, $.fn.editabletypes.abstractinput.defaults, {
            inputclass: ''
        });

    $.fn.editabletypes.place = Place;

}(window.jQuery));
