(function() {
    window.AuthorAutocompleteView = Backbone.View.extend({
        events: {
            'click .author-delete': 'onRemoveAuthor'
        },
        initialize: function(options) {
            _.bindAll(this, 'dataSource', 'selectAuthor', 'onRemoveAuthor');

            var html = jQuery('#author-list-template').html()
            this.authorTemplate = _.template(html);

            this.elInput = jQuery(this.el).find("input[name='footprint-author']");
            this.elAuthors = jQuery(this.el).find("ul.authors");
           
            jQuery(this.elInput).autocomplete({
                source: this.dataSource,
                select: this.selectAuthor,
                minLength: 2,
                open: function() {
                    jQuery(this).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
                },
                close: function() {
                    jQuery(this).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
                }
            });
        },        
        dataSource: function(request, response) {
            jQuery.ajax({
                url: "/api/person/",
                dataType: "jsonp",
                data: {
                    q: request.term
                },
                success: function(data) {
                    var names = [];
                    for (var i=0; i < data.length; i++) {
                        names.push({
                            label: data[i].name,
                            object_id: data[i].object_id
                        });
                    }
                    response(names);
                }
            });
        },
        selectAuthor: function(event, ui) {
            event.preventDefault();
            var markup = this.authorTemplate({'ui': ui.item});
            jQuery(this.elAuthors).append(markup);
            jQuery(this.elInput).val('');
            return false;
        },
        onRemoveAuthor: function(evt) {
            jQuery(evt.currentTarget).parent('li').remove();
        }
    });

    window.RecordFootprintView = Backbone.View.extend({
        events: {
            'click .btn-geoposition': 'onChooseLocation',
            'click .save-geoposition': 'onSaveLocation',
            'shown.bs.modal #geoposition-modal': 'onShowLocationModal',
            
        },
        initialize: function(options) {
            _.bindAll(this,
                      'onChooseLocation',
                      'onSaveLocation',
                      'onShowLocationModal');
            
            jQuery(this.el).find("[data-toggle='popover']").popover();
            
            this.authorView = new AuthorAutocompleteView({el: this.el});
        },
        onChooseLocation: function(evt) {
            jQuery('#geoposition-modal').modal({
                backdrop: 'static',  keyboard: false, show: false});
            this.map = new google.maps.Map(document.getElementById("mapCanvas"),
                                           {zoom: 3});
            this.marker = new google.maps.Marker({
                position: new google.maps.LatLng(51.219987, 4.396237),
                draggable: true
            });
            this.marker.setMap(this.map);

            jQuery("#geoposition-modal").modal('show')
        },
        onSaveLocation: function(evt) {
            var pos = this.marker.getPosition();
            jQuery("span.pinpoint-location").html(pos.toString());
            jQuery('#geoposition-modal').modal('hide')
        },
        onShowLocationModal: function(evt) {
            google.maps.event.trigger(this.map, "resize");
            this.map.setCenter(this.marker.position);
        }
    });
})();
