module.exports = {
  /** configure dev options */
  devServer: {
    hot: process.env.NODE_ENV === "development",
    liveReload: process.env.NODE_ENV === "development",
  },

  /** sass options */
  css: {
    loaderOptions: {
      sass: {
        additionalData: `
          @use "@/global/variables.scss" as *;
        `,
      },
    },
  },

  configureWebpack: {
    plugins: [
      /** export webpack-generated stats of compiled bundle for analysis */
      // eslint-disable-next-line
      // new (require("stats-webpack-plugin"))("stats.json"),
    ],
  },
};
