define(function() {
    // Simplifying this approach
    // https://stackoverflow.com/questions/50498666/nodejs-async-promise-queue
    class AsyncQueue {
        constructor() {
            this.queue = [];
            // eslint-disable-next-line scanjs-rules/call_setInterval
            setInterval(this.resolveNext.bind(this), 100);
        }
        add(fn, cb, params) {
            this.queue.push({fn, cb, params});
        }
        resolveNext() {
            if (!this.queue.length) {
                return;
            }
            const {fn, cb, params} = this.queue.shift();
            fn(params).then(cb);
        }
    }

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

    // https://developer.mozilla.org/en-US/docs/Web/API/
    //  Web_Storage_API/Using_the_Web_Storage_API
    function storageAvailable(type) {
        try {
            var storage = window[type],
                x = '__storage_test__';
            storage.setItem(x, x);
            storage.removeItem(x);
            return true;
        }
        catch(e) {
            return e instanceof DOMException && (
                // everything except Firefox
                e.code === 22 ||
                // Firefox
                e.code === 1014 ||
                // test name field too, because code might not be present
                // everything except Firefox
                e.name === 'QuotaExceededError' ||
                // Firefox
                e.name === 'NS_ERROR_DOM_QUOTA_REACHED') &&
                // acknowledge QuotaExceededError only if
                // there's something already stored
                storage.length !== 0;
        }
    }

    return {
        AsyncQueue: AsyncQueue,
        ajaxSetup: ajaxSetup,
        csrfSafeMethod: csrfSafeMethod,
        sanitize: sanitize,
        storageAvailable: storageAvailable
    };
});
