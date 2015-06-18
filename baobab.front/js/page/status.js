var $ = require('jquery-browserify');
 //   event = require('./event');

var header = $('#container > header');
var target = $('#container');

module.exports = {
  load: function () {
    target.scrollTop(0);

    $(document).on('keydown', function(e) {
      if (e.keyCode == 34) { // Pagedown
        $(document).unbind('keydown');
        target.scrollTop(header.height());
        e.preventDefault();
      }
    });
  },
  unload: function () {
    $(document).unbind('keydown');
  }

};
