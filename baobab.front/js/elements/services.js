var Q = require('q'),
    api = require('../api'),
    templates = require('../templates'),
    $ = require('jquery-browserify');

var button = $('header > .button');
var target = $('.services');
var targetUp = $('.services-up');
var filterButton = $('#service');

function fillServicesDetails (json){
  var content = '';
  var contentUp = '';

  for (var key in json) {
    if (json[key] != undefined && json[key].status != undefined) {
      element = templates['service'](
        $.extend({name: key}, json[key]));
      if (json[key].status != 'SUNNY') {
        content += element;
      } else {
        contentUp += element;
      }
    }
  }
  target.html(content);
  targetUp.html(contentUp);

  return json;
}

function fillFilterServices (json) {
  filterButton.html(templates['service-button'](json));
  return json;
}


module.exports = api.services()
  .then(fillServicesDetails)
  .then(fillFilterServices)
  .then(function() {
    button.on('click', function() {
      targetUp.toggle()
    });
  });


