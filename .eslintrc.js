module.exports = {
    "env": {
        "browser": true,
        "amd": true,
        "jquery": true
    },
    "extends": "eslint:recommended",
    "globals": {
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
