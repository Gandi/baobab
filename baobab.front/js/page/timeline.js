var $ = require('jquery-browserify'),
    event = require('./event');

var target = $('#container');
var status = $('#container > header');

module.exports = {
  load: function() {
    // Direct exit if old route was a subroute
    if (this.lastRoute && this.lastRoute.slice(0,2).join('/') == ['timeline', 'events'].join('/')) return;
    var height = status.height();
    target.scrollTop(height);
  },
  unload: function() {
  }
}

