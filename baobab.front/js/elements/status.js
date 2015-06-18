var api = require('../api'),
    $ = require('jquery-browserify'),
    templates = require('../templates');


var contents = {
  'STORMY': 'Oops, we have problems',
  'CLOUDY': 'We\'re currently working on our platform',
  'FOGGY': 'Oops we have problems which are not impacting our services.',
  'SUNNY': 'All services are up and running',
};

var target = $('header > h3');
var button = $('header > a.button');

module.exports = api.status()
  .then(function(json) {
    target.text(contents[json.status])
      .addClass('status-' + json.status.toLowerCase());
    button.html(templates['service-status-button'](json)).show();
  });
