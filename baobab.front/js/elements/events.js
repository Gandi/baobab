var Q = require('q'),
    api = require('../api'),
    router_utils = require('../router_utils'),
    templates = require('../templates'),
    $ = require('jquery-browserify'),
    moment = require('moment');

var target = $('main');
var maintenancesBox = $('header .maintenances');

var size = 240;

function maintenances(events) {
  var futureEvents = events.filter(function(el) {
    return el.date_start.isAfter();
  }).filter(function(el) {
    return el.category == "Maintenance";
  });

  if (futureEvents.length > 0) {
    maintenancesBox.html(templates['maintenances'](futureEvents))
      .show();
  }
  return events;
}

module.exports = Q.fcall(function() {
  var now = moment();
  var days = 30;

  return api.events(now, days)
    .then(function (json) {
      return json.map(function(el) {
        el.date_start = moment(el.date_start);
        if (el.date_end) {
          el.date_end = moment(el.date_end);
          el.duration = moment.duration(el.date_start.diff(el.date_end));
        }
        el.estimate_date_end = moment(el.estimate_date_end);
        return el;
      });
    })
    .then(maintenances)
    .then(function (json) {
      var events = {};

      json.forEach(function (el) {
        date_end = el.date_end || el.estimate_date_end;
        // because of day change
        if (el.date_start < now && date_end > moment().endOf('day')) {
          date_end = moment();
          if (el.date_end) {
            el.date_end = date_end;
          }
          el.estimate_date_end = date_end;
        }
        date_end = moment.utc(date_end).format('YYYY-MM-DD');

        events[date_end] = events[date_end] || [];
        events[date_end].push(el);
      });

      return events;
    })
    .then(function(events) {
      var iter_date = moment.utc(now).startOf('day');

      var content = [];

      for(var i = 0; i < days; i++) {
        day_events_tmp = events[iter_date.format('YYYY-MM-DD')] || []
        day_events = day_events_tmp.map(function(el) {
          date_end = el.date_end || el.estimate_date_end;
          diff = date_end.diff(iter_date) / 1000 / 3600 / 24; // Results as percent of day
          el.pos = Math.round(size - diff*size) + 'px';

          diff = date_end.diff(el.date_start) / 1000 / 3600 / 24;
          el.height = Math.round(diff*size) + 'px';
          return el;
        })

        day = templates['day']({
          day: iter_date,
          events: day_events
        })

        iter_date.subtract(1, 'days');

        content.push(day);
      }

      target.html(content.join(''))
        .children('section').children('article').on('click', function(e) {
          router_utils.goto($(this).attr('data-href'));
          e.preventDefault();
        });

    });
})

