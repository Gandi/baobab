describe('services', function() {

  it('should be listed in the services button', function() {
    browser.driver.get('http://localhost:8000');
    browser.ignoreSynchronization = true; // Non angular

    var services = $('#service');

    expect(services.all(by.tagName('option')).count()).toEqual(7+1); // 7 services + 1 default value
  });
});
