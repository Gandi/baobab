var Q = require('q'),
    moment = require('moment'),
    $ = require('jquery-browserify');


var target = $('header > p > time');

module.exports = Q.fcall(function() {
  var now = moment();
  target.attr('datetime', now.format())
    .text(now.format('MMMM Do YYYY, h:mm a ZZ'))
    .parent().show();
});

