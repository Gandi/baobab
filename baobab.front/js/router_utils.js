var Router = require('director').Router,
    $ = require('jquery-browserify');
var self = module.exports;


function sameOrigin(href) {
  var origin = location.protocol + '//' + location.hostname;
  if (location.port) origin += ':' + location.port;
  return href && (0 === href.indexOf(origin));
}

function which(e) {
  e = e || window.event;
  return null === e.which
    ? e.button
    : e.which;
}

function onclick(e) {
  if (1 != which(e)) return;
  if (e.metaKey || e.ctrlKey || e.shiftKey) return;
  if (e.defaultPrevented) return;

  // ensure link
  var el = e.target;
  while (el && 'A' != el.nodeName) el = el.parentNode;
  if (!el || 'A' != el.nodeName) return;

  // ensure non-hash for the same path
  var link = el.getAttribute('href');
  if (el.pathname == location.pathname && (el.hash || '#' == link)) return;

  // Check for mailto: in the href
  if (link && link.indexOf("mailto:") > -1) return;

  // check target
  if (el.target) return;

  // x-origin
  if (!sameOrigin(el.href)) return;

  // rebuild path
  var path = el.pathname + el.search + (el.hash || '');

  // same page
  var orig = path + el.hash;

  module.exports.goto(orig);
  return false;
}

function registerClick() {
  $(window).on('click', onclick);
}

function storeLast() {
  self.router.lastRoute = self.router.getRoute();
}

module.exports = {
  router: undefined,
  init: function(routes) {
    self.router = new Router(routes).configure({html5history: true, on: storeLast})
    self.router.param('id', /([\\w\\-]+)/);
    self.router.init();

    registerClick();
  },
  goto: function(url) {
    self.router.setRoute(url);
  }
}
self = module.exports;
