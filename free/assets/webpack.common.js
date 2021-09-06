// Semantic UI adjustments - https://medium.com/@marekurbanowicz/how-to-customize-fomantic-ui-with-less-and-webpack-applicable-to-semantic-ui-too-fbf98a74506c

const path = require("path")
const BundleTracker = require('webpack-bundle-tracker')
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const WebpackCleanupPlugin = require('webpack-cleanup-plugin')
const MiniCssExtractPlugin = require("mini-css-extract-plugin")
const TerserJSPlugin = require('terser-webpack-plugin')
const OptimizeCSSAssetsPlugin = require('optimize-css-assets-webpack-plugin')
const glob = require("glob")
const devMode = process.env.NODE_ENV !== 'production'

module.exports = {
    context: __dirname,

    entry: {
        common: './src/common.js',
        components: glob.sync('./src/components/*.js')
    },

    resolve: {
        alias : {
            "../../theme.config$": path.join(__dirname, "/semantic-ui/theme.config"),
            "../semantic-ui/site": path.join(__dirname, "/semantic-ui/site")
        }
    },

    output: {
        path: path.resolve('../../static/bundles/'),
        filename: "[name]-[hash].js",
    },

    optimization: {
        minimizer: [new TerserJSPlugin({}), new OptimizeCSSAssetsPlugin({})]
    },

    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        new WebpackCleanupPlugin({
            quiet: true
        }),
        new BundleAnalyzerPlugin({
            analyzerMode: "disabled",
            defaultSizes: "gzip"
        }),
        new MiniCssExtractPlugin({
            filename: "./[name].[contenthash].css",
        })
    ],

    module: {
        rules: [
            { test: /\.js$/, loader: ['babel-loader', 'django-react-loader'], exclude: /node_modules/ },
            { test: /\.jsx$/, loader:['babel-loader', 'django-react-loader'], exclude: /node_modules/ },
            {
                test: /\.(sa|sc|c)ss$/,
                use: [
                    devMode ? 'style-loader' : MiniCssExtractPlugin.loader,
                    'css-loader',
                    //'postcss-loader',
                    'sass-loader',
                ],
            },
            //LESS
            {
                test: /\.(less)$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    "css-loader",
                    "less-loader"
                ]
            },
            // this handles images
            {
                test: /\.jpe?g$|\.gif$|\.ico$|\.png$|\.svg$/,
                use: 'file-loader?name=[name]-[hash].[ext]'
            },

            // the following rules handle font extraction
            {
                test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
                loader: 'url-loader?limit=10000&mimetype=application/font-woff'
            },
            {
                test: /\.(ttf|eot)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
                loader: 'file-loader'
            },
            {
                test: /\.otf(\?.*)?$/,
                use: 'file-loader?name=/fonts/[name].[ext]&mimetype=application/font-otf'
            }
        ],
    },

    resolveLoader: {
        alias: {
            'django-react-loader': path.join(__dirname, 'utils', 'django-react-loader.js'),
        }
    }
}