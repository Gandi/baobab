var api = require('../api'),
    marked = require('marked'),
    moment = require('moment'),
    $ = require('jquery-browserify'),
    template = require('../templates'),
    router_utils = require('../router_utils');

var target = $('body > article');


marked.setOptions({
  gfm: true
});

module.exports = {
  show: function() {
    target.show();
  },
  hide: function (e) {
    target.hide();
    if (e && e.preventDefault != undefined) e.preventDefault();
  }
}

var self = module.exports;

module.exports.unload = function() {
  self.hide();
}

module.exports.load = function(event_id) {
  var short_format =  1000 * 60 * 60 * 18; // 18 hours
  function reldate(date) {
    if ( Math.abs(moment() - date) < short_format ) {
      return date.format('dddd, LT ZZ');
    } else {
      return date.format('LLLL ZZ');
    }
  };

  api.event(event_id)
    .then(function(json) {
      json['marked'] = marked;

      json['date_start'] = moment(json['date_start'])
      json['estimate_date_end'] = moment(json['estimate_date_end'])

      for ( var elt in json['logs']) {
        json['logs'][elt]['date'] = moment(json['logs'][elt]['date'])
      }

      if (json['date_end']) json['date_end'] = moment(json['date_end'])

      var end_date = json.date_end || json.estimate_date_end;
      end_date = moment.utc(end_date);

      json['end_date'] = end_date;

      json['duration'] = moment.duration(json['date_start'].diff(end_date));

      // Change date formating relative to current date
      json['reldate'] = reldate;

      target.html(template['event'](json))
        .removeClass('maintenance')
        .removeClass('incident')
        .addClass(json.category.toLowerCase());
    }).then(function() {
      $(document).on('keydown', function(e) {
        if (e.keyCode === 27) { // Escape
          $(document).unbind('keydown');
          self.hide();
          router_utils.goto('/timeline');
        }
      });
    }).then(function() {
      self.show();
    })
}
