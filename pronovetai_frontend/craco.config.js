// craco.config.js
module.exports = {
  style: {
    postcss: {
      plugins: [
        require('postcss-import'),
        require('@tailwindcss/postcss')(),
        require('autoprefixer'),
      ],
    },
  },
};
