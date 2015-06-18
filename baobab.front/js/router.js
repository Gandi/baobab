var router_utils = require('./router_utils'),
    status = require('./page/status'),
    timeline = require('./page/timeline'),
    event = require('./page/event');

module.exports = {
  init: function() {
    router_utils.init({
      '/': {
        on: status.load,
        after: status.unload,
        '/timeline': {
          on: timeline.load,
          after: timeline.unload,
          '/events/:id': {
            on: event.load,
            after: event.unload
          }
        }
      }
    });
  },
  goto: router_utils.goto
}
