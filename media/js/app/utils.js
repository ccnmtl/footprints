define(function() {

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    function ajaxSetup() {
        // setup some ajax progress indicator
        $('html').ajaxStart(function() {
            $(this).addClass('busy');
        });
        $('html').ajaxStop(function() {
            $(this).removeClass('busy');
        });

        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    const token = $('meta[name="csrf-token"]')
                        .attr('content');
                    xhr.setRequestHeader('X-CSRFToken', token);
                }
            }
        });
    }

    function sanitize(s) {
        // http://shebang.brandonmintern.com/foolproof-html-escaping-in-javascript/
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(s));
        return div.innerHTML;
    }

    return {
        ajaxSetup: ajaxSetup,
        csrfSafeMethod: csrfSafeMethod,
        sanitize: sanitize
    };
});
