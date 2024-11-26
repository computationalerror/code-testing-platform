const { defineConfig } = require('@vue/cli-service');
const path = require('path');
const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin');

module.exports = defineConfig({
    // To enable feature flag for Vue 3
    chainWebpack: (config) => {
        // Add a feature flag for Vue hydration mismatch details
        config.plugin('define').tap((definitions) => {
            definitions[0]['__VUE_PROD_HYDRATION_MISMATCH_DETAILS__'] = 'false'; // or 'true' based on your needs
            return definitions;
        });
    },

    // Additional webpack configurations
    configureWebpack: {
        resolve: {
            alias: {
                '@': path.resolve(__dirname, 'src'), // Set '@' to point to 'src' directory
            },
        },
        plugins: [
            new MonacoWebpackPlugin({
                languages: ['javascript', 'typescript', 'python', 'cpp'], // Add required languages
            }),
        ],
    },

    // To avoid the 500 error in API calls, ensure CORS is correctly handled in the backend.
    devServer: {
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:5000', // Change to your backend API URL
                changeOrigin: true,
                secure: false,
                pathRewrite: {
                    '^/api': '', // Remove /api prefix from the request
                },
            },
        },
    },
});