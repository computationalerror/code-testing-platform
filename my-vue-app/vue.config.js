/* const { defineConfig } = require('@vue/cli-service')

module.exports = {
    // Simple configuration for personal use
    devServer: {
        port: 8080, // Specify the development server port
    },
}; */

const { defineConfig } = require('@vue/cli-service');
const path = require('path');

module.exports = defineConfig({
    configureWebpack: {
        resolve: {
            alias: {
                '@': path.resolve(__dirname, 'src'), // Set '@' to point to 'src' directory
            },
        },
    },
});