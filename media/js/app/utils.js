define(function() {
    // Given a camel case string, return a string of upper-case letters
    // :footprintStartDate" returns "fsd"
    function abbreviate(str) {
        return str
            .split(/(?=[A-Z])/)
            .map(word => word.charAt(0).toLowerCase())
            .join('');
    }

    // Simplifying this approach
    // https://stackoverflow.com/questions/50498666/nodejs-async-promise-queue
    class AsyncQueue {
        constructor() {
            this.queue = [];
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

    function parsePageNumber(str) {
        let pageNumber = 1;
        try {
            let result = str.match(/page=(\d+)/);
            pageNumber = parseInt(result[1], 10);
        } catch (err) {
            // continue with default page number
        }
        return pageNumber;
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

    // Sourced from https://snazzymaps.com/style/151/ultra-light-with-labels
    // Creator: http://www.haveasign.pl/, hawsan
    // All SnazzyMap styles are offered under a
    // Creative Commons CC0 1.0 Universal Public Domain Dedication
    const lightGrayStyle = new google.maps.StyledMapType([
        {
            'featureType': 'water',
            'elementType': 'geometry',
            'stylers': [
                {
                    'color': '#cccccc'
                },
                {
                    'lightness': 17
                }
            ]
        },
        {
            'featureType': 'landscape',
            'elementType': 'geometry',
            'stylers': [
                {
                    'color': '#e8e8e8'
                },
                {
                    'lightness': 20
                }
            ]
        },
        {
            'featureType': 'road.highway',
            'elementType': 'geometry.fill',
            'stylers': [
                {
                    'color': '#ffffff'
                },
                {
                    'lightness': 17
                }
            ]
        },
        {
            'featureType': 'road.highway',
            'elementType': 'geometry.stroke',
            'stylers': [
                {
                    'color': '#ffffff'
                },
                {
                    'lightness': 29
                },
                {
                    'weight': 0.2
                }
            ]
        },
        {
            'featureType': 'road.arterial',
            'elementType': 'geometry',
            'stylers': [
                {
                    'color': '#ffffff'
                },
                {
                    'lightness': 18
                }
            ]
        },
        {
            'featureType': 'road.local',
            'elementType': 'geometry',
            'stylers': [
                {
                    'color': '#ffffff'
                },
                {
                    'lightness': 16
                }
            ]
        },
        {
            'featureType': 'poi',
            'elementType': 'geometry',
            'stylers': [
                {
                    'color': '#f5f5f5'
                },
                {
                    'lightness': 21
                }
            ]
        },
        {
            'featureType': 'poi.park',
            'elementType': 'geometry',
            'stylers': [
                {
                    'color': '#dedede'
                },
                {
                    'lightness': 21
                }
            ]
        },
        {
            'elementType': 'labels.text.stroke',
            'stylers': [
                {
                    'visibility': 'on'
                },
                {
                    'color': '#ffffff'
                },
                {
                    'lightness': 16
                }
            ]
        },
        {
            'elementType': 'labels.text.fill',
            'stylers': [
                {
                    'saturation': 36
                },
                {
                    'color': '#333333'
                },
                {
                    'lightness': 20
                }
            ]
        },
        {
            'elementType': 'labels.icon',
            'stylers': [
                {
                    'visibility': 'off'
                }
            ]
        },
        {
            'featureType': 'transit',
            'elementType': 'geometry',
            'stylers': [
                {
                    'color': '#f2f2f2'
                },
                {
                    'lightness': 19
                }
            ]
        },
        {
            'featureType': 'administrative',
            'elementType': 'geometry.fill',
            'stylers': [
                {
                    'color': '#fefefe'
                },
                {
                    'lightness': 20
                }
            ]
        },
        {
            'featureType': 'administrative',
            'elementType': 'geometry.stroke',
            'stylers': [
                {
                    'color': '#fefefe'
                },
                {
                    'lightness': 17
                },
                {
                    'weight': 1.2
                }
            ]
        }
    ]);

    return {
        abbreviate: abbreviate,
        AsyncQueue: AsyncQueue,
        ajaxSetup: ajaxSetup,
        csrfSafeMethod: csrfSafeMethod,
        lightGrayStyle: lightGrayStyle,
        parsePageNumber: parsePageNumber,
        sanitize: sanitize,
        storageAvailable: storageAvailable
    };
});

