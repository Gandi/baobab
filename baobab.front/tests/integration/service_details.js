describe('service details', function() {
  it('should be open with two maintenance services', function() {
    browser.driver.get('http://localhost:8000');
    browser.ignoreSynchronization = true; // Non angular

    var services = element(by.css('header .services'));

    expect(services.all(by.tagName('div')).count()).toEqual(2);

    // One of each type
    expect(services.all(by.css('div.status-cloudy')).count()).toEqual(1); 
    expect(services.all(by.css('div.status-stormy')).count()).toEqual(1);
  });
  it('should open/close', function() {
    browser.get('http://localhost:8000');
    browser.ignoreSynchronization = true; // Non angular

    var button = element(by.css('header a.button'));
    var services = element(by.css('header .services-up'));

    button.click();

    expect(services.getAttribute('style')).toEqual('display: block;'); 

    button.click();

    expect(services.getAttribute('style')).toEqual('display: none;'); 
  });
});
