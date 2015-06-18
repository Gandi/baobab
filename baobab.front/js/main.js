var Q = require('q'),
    router = require('./router'),
    ie = require('./ie'),
    element_status = require('./elements/status'),
    element_statustime = require('./elements/statustime'),
    element_services = require('./elements/services'),
    element_events = require('./elements/events'),
    element_eventsfilter = require('./elements/eventsfilter');

Q.all([
  ie,
  element_status,
  element_statustime,
  element_services,
  element_eventsfilter
]).then(
  router.init
).then(
  element_events
).done();

