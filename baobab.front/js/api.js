var Qajax = require('qajax'),
    moment = require('moment');

module.exports = {
  status: function() {
    return Qajax({url: '/api/status', headers:{'Accept': 'application/json'}})
      .then(Qajax.filterSuccess)
      .then(Qajax.toJSON);
  },
  services: function() {
    return Qajax({url: '/api/services', headers:{'Accept': 'application/json'}})
      .then(Qajax.filterSuccess)
      .then(Qajax.toJSON);
  },
  events: function(end_date, days) {
    var end = moment.utc(end_date),
        start = end
      .subtract(days, 'days')
      .startOf('day');
    var args = {
      "date_start__gte": start.format('YYYY-MM-DD')
    };
    return Qajax({url: '/api/events?' + Qajax.serialize(args), headers:{'Accept': 'application/json'}})
      .then(Qajax.filterSuccess)
      .then(Qajax.toJSON)
  },
  event: function(id) {
    return Qajax({url: '/api/events/' + id, headers:{'Accept': 'application/json'}})
      .then(Qajax.filterSuccess)
      .then(Qajax.toJSON)
  }

}
