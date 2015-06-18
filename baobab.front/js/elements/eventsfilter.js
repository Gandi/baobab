var Q = require('q'),
    $ = require('jquery-browserify');

var target = $('main');
var categoryButton = $('#category');
var serviceButton = $('#service');

var selected = function(){ return this.selected; }

function filterClassRegex(r) {
  return function(i, classname) {
    return classname.split(/\s+/g).filter(function(el) {
      return (new RegExp(r)).test(el)?el:'';
    }).join(' ');
  };
}

function updateFilterCategory() {
  var newvalue = categoryButton.children().filter(selected).attr('value');

  if (newvalue) {
    target.removeClass(filterClassRegex(/^cat-/))
      .addClass('cat-'+newvalue);
  } else {
    target.removeClass(filterClassRegex(/^cat-/));
  }
}

function updateFilterService() {
  var newvalue = serviceButton.children().filter(selected).attr('value');

  if (newvalue) {
    target.removeClass(filterClassRegex(/^svc-/))
      .addClass('svc-'+newvalue);
  } else {
    target.removeClass(filterClassRegex(/^svc-/));
  }
}

function updateFilterType() {
  var category = categoryButton.children().filter(selected).attr('value'), 
      service = serviceButton.children().filter(selected).attr('value');

  if (category && service) {
    target.removeClass('filtered-category')
      .removeClass('filtered-service')
      .addClass('filtered-category-service');
  } else if (category) {
    target.removeClass('filtered-service')
      .removeClass('filtered-category-service')
      .addClass('filtered-category');
  } else if (service) {
    target.removeClass('filtered-category')
      .removeClass('filtered-category-service')
      .addClass('filtered-service');
  } else {
    target.removeClass('filtered-category')
      .removeClass('filtered-service')
      .removeClass('filtered-category-service');
  }

}


module.exports = Q.fcall(function() {
  categoryButton.on('change', updateFilterCategory);
  serviceButton.on('change', updateFilterService);

  categoryButton.on('change', updateFilterType);
  serviceButton.on('change',  updateFilterType);
});

