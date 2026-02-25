import globals from "globals";
import path from "node:path";
import { fileURLToPath } from "node:url";
import js from "@eslint/js";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
    baseDirectory: __dirname,
    recommendedConfig: js.configs.recommended,
    allConfig: js.configs.all
});

export default [...compat.extends("eslint:recommended"), 
    {
    languageOptions: {
        globals: {
            ...globals.browser,
            ...globals.amd,
            ...globals.jquery,
            _: true,
            Backbone: true,
            google: true,
            Footprints: true,
            requirejs: true,
            Promise: true,
            MarkerClusterer: true,
            Highcharts: true,
        },

        ecmaVersion: 9,
        sourceType: "script",

        parserOptions: {
            ecmaFeatures: {
                experimentalObjectRestSpread: true,
            },
        },
    },

    rules: {
        indent: ["error", 4],
        "linebreak-style": ["error", "unix"],

        "no-unused-vars": ["error", {
            vars: "all",
            args: "none",
        }],

        quotes: ["error", "single"],
        semi: ["error", "always"],

        "max-len": [2, {
            code: 80,
            tabWidth: 4,
            ignoreUrls: true,
        }],

        "space-before-function-paren": ["error", "never"],
        "space-in-parens": ["error", "never"],
        "no-trailing-spaces": ["error"],

        "key-spacing": ["error", {
            beforeColon: false,
        }],

        "func-call-spacing": ["error", "never"],
    },
}];
