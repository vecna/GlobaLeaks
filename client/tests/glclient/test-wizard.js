describe('globaLeaks setup wizard', function() {
  it('should allow the user to setup the wizard', function() {
      browser.get('http://127.0.0.1:8082/');
      
      // Go to step 2
      element(by.css('[data-ng-click="step=step+1"]')).click();
      
      // Fill out the form
      element(by.model('admin.node.name')).sendKeys('E2E Test Instance');
      element(by.model('admin.node.description')).sendKeys('This instance is for E2E testing');
      element(by.model('admin.node.email')).sendKeys('info@globaleaks.org');
      element(by.model('admin.node.password')).sendKeys('ACollectionOfDiplomaticHistorySince_1966_ToThe_Pr esentDay#');
      element(by.model('admin.node.check_password')).sendKeys('ACollectionOfDiplomaticHistorySince_1966_ToThe_Pr esentDay#');

      element(by.model('receiver.name')).sendKeys('Laura Poitras');
      element(by.model('receiver.mail_address')).sendKeys('info@globaleaks.org');
      
      // Disable encryption for receiver
      element(by.model('admin.node.allow_unencrypted')).click();
      element(by.css('[data-ng-click="ok()"]')).click();
      
      element(by.model('context.name')).sendKeys('Data Gate');
      
      // Complete the form
      element.all(by.css('[data-ng-click="step=step+1"]')).get(1).click();
      
      expect(element(by.css('.congratulations')).isPresent()).toBe(true) 
      
      // Go to admin interface
      element(by.css('[data-ng-click="finish()"]')).click();
    });
});
