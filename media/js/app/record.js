(function() {
    jQuery(document).ready(function() {
        jQuery("[data-toggle='popover']").popover();
        jQuery("input[name='footprint-title']").autocomplete({
            source: function( request, response ) {
                jQuery.ajax({
                  url: "/api/titles/",
                  dataType: "jsonp",
                  data: {
                      q: request.term
                  },
                  success: function(data) {
                      var titles = [];
                      for (var i=0; i < data.length; i++) {
                          titles.push(data[i].title);
                      }
                      response(titles);
                  }
                });
              },
              minLength: 2,
              open: function() {
                jQuery( this ).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
              },
              close: function() {
                jQuery( this ).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
              }
        });
    });
})();
