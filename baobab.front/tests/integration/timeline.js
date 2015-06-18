describe('timeline', function() {
  function scrollTop(el) {
    return browser.driver.executeScript('return arguments[0].scrollTop;', el.getWebElement());
  }
  function height(el) {
    return browser.driver.executeScript('return arguments[0].getBoundingClientRect().height;', el.getWebElement());
  }

  it('should be scrolled when clicking on click', function() {
    browser.driver.get('http://localhost:8000');
    browser.ignoreSynchronization = true; // Non angular

    var scroll = element(by.css('header a.more'));
    var headerHeight = $('header').then(height);

    expect($('#container').then(scrollTop)).toEqual(0);
    browser.driver.sleep(600); // see https://github.com/flatiron/director/blob/v1.2.2/lib/director/browser.js#L83

    scroll.click();

    expect($('#container').then(scrollTop)).toEqual(headerHeight);
  });

  it('should be scrolled on page down', function() {
    browser.driver.get('http://localhost:8000');
    browser.ignoreSynchronization = true; // Non angular

    browser.driver.sleep(600); // see https://github.com/flatiron/director/blob/v1.2.2/lib/director/browser.js#L83

    $('body').sendKeys(protractor.Key.PAGE_DOWN); // PAGE DOWN

    var headerHeight = $('header').then(height);

    expect($('#container').then(scrollTop)).toEqual(headerHeight);
  });
});
