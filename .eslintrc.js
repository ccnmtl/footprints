module.exports = {
    "env": {
        "browser": true,
        "amd": true,
        "jquery": true
    },
    "parserOptions": {
        "ecmaVersion": 9,
        "ecmaFeatures": {
            "experimentalObjectRestSpread": true
        }
    },
    "plugins": [
        "security"
    ],
    "extends": [
        "eslint:recommended",
        "plugin:security/recommended"
    ],
    "globals": {
        "_": true,
        "Backbone": true,
        "google": true,
        "Footprints": true,
        "requirejs": true,
        "Promise": true,
        "MarkerClusterer": true,
        "Highcharts": true
    },
    "rules": {
        "indent": [
            "error",
            4
        ],
        "linebreak-style": [
            "error",
            "unix"
        ],
        "no-unused-vars": [
            "error",
            {"vars": "all", "args": "none"}
        ],
        "quotes": [
            "error",
            "single"
        ],
        "semi": [
            "error",
            "always"
        ],
        "max-len": [2, {"code": 80, "tabWidth": 4, "ignoreUrls": true}],
        "space-before-function-paren": ["error", "never"],
        "space-in-parens": ["error", "never"],
        "no-trailing-spaces": ["error"],
        "key-spacing": ["error", { "beforeColon": false }],
        "func-call-spacing": ["error", "never"],

        'security/detect-buffer-noassert': 1,
        'security/detect-child-process': 1,
        'security/detect-disable-mustache-escape': 1,
        'security/detect-eval-with-expression': 1,
        'security/detect-new-buffer': 1,
        'security/detect-no-csrf-before-method-override': 1,
        'security/detect-non-literal-fs-filename': 1,
        'security/detect-non-literal-regexp': 1,
        'security/detect-non-literal-require': 0, /* requirejs conflict */
        'security/detect-object-injection': 0, /* several false positives */
        'security/detect-possible-timing-attacks': 1,
        'security/detect-pseudoRandomBytes': 1,
        'security/detect-unsafe-regex': 1
    }
};
