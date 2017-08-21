module.exports = {
    "env": {
        "browser": true,
        "amd": true,
        "jquery": true
    },
    "plugins": [
        "security",
        "scanjs-rules",
        "no-unsafe-innerhtml"
    ],
    "extends": [
        "eslint:recommended",
        "plugin:security/recommended"
    ],
    "globals": {
        "_": true,
        "Backbone": true,
        "google": true,
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
        ]
    }
};
