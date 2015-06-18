describe('events', function() {
  function click(el) {
    return browser.driver.executeScript('return arguments[0].click();', el.getWebElement());
  }

  it('should open a popup', function() {
    browser.driver.get('http://localhost:8000');
    browser.ignoreSynchronization = true; // Non angular
    browser.driver.sleep(600); // see https://github.com/flatiron/director/blob/v1.2.2/lib/director/browser.js#L83

    var event1 = element.all(by.css('main section article p a')).first();
    var popup = $('body>article');

    event1.then(click);

    expect(popup.getAttribute('style')).toEqual('display: block;');
  });
});
