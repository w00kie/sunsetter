'use strict';

const path = require('path');

module.exports = {
    entry: './static/src/tools.coffee',
    context: path.resolve(__dirname),
    output: {
        path: path.resolve(__dirname, 'static/js'),
        filename: 'bundle.js',
    },
    module: {
        rules: [
            {
                test: /\.coffee$/,
                use: ['coffee-loader']
            }
        ]
    },
    resolve: {
    },
    devtool: 'source-map',
    plugins: [
    ]
};
