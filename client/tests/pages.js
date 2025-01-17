exports.receiver = function() {
  this.viewMostRecentSubmission = async function() {
    await element(by.id("tip-0")).click();
  };

  this.addPublicKey = async function(pgp_key_path) {
    await browser.setLocation("/recipient/preferences");

    await element(by.xpath("//input[@type='file']")).sendKeys(pgp_key_path);

    await element.all(by.cssContainingText("span", "Save")).first().click();
  };

  this.wbfile_widget = function() {
    return element(by.css("#TipPageWBFileUpload"));
  };

  this.uploadWBFile = async function(fname) {
    await element(by.xpath("//input[@type='file']")).sendKeys(fname);
  };
};

exports.whistleblower = function() {
  this.performSubmission = async function() {
    await browser.get("/#/");
    await browser.gl.utils.takeScreenshot("whistleblower/home.png");
    await element(by.id("WhistleblowingButton")).click();
    await browser.gl.utils.waitUntilPresent(by.id("SubmissionForm"));
    await element(by.id("step-0")).element(by.id("step-0-field-0-0-input-0")).sendKeys("summary");
    await element(by.id("step-0")).element(by.id("step-0-field-1-0-input-0")).sendKeys("detail");
    await element(by.id("step-0")).element(by.id("step-0-field-2-0-input-0")).sendKeys("...");
    await element(by.id("step-0")).element(by.id("step-0-field-2-1-input-0")).sendKeys("...");

    await element.all(by.id("step-0-field-3-0-input-0")).first().element(by.xpath(".//*[text()='I witnessed the facts in person']")).click();
    await element.all(by.id("step-0-field-4-0-input-0")).first().element(by.xpath(".//*[text()='Yes']")).click();

    await element(by.id("step-0")).element(by.id("step-0-field-6-0-input-0")).sendKeys("...");

    var fileToUpload1 = browser.gl.utils.makeTestFilePath("evidence-1.pdf");
    var fileToUpload2 = browser.gl.utils.makeTestFilePath("evidence-2.zip");
    await element(by.id("step-0")).element(by.id("step-0-field-5-0-input-0")).element(by.xpath("//input[@type='file']")).sendKeys(fileToUpload1);
    await element(by.id("step-0")).element(by.id("step-0-field-5-0-input-0")).element(by.xpath("//input[@type='file']")).sendKeys(fileToUpload2);

    await element.all(by.id("step-0-field-7-0-input-0")).first().element(by.xpath(".//*[text()='No']")).click();

    await element(by.id("step-0")).element(by.id("step-0-field-10-0-input-0")).sendKeys("...");

    await browser.gl.utils.waitUntilClickable(by.id("SubmitButton"));

    await browser.gl.utils.takeScreenshot("whistleblower/submission.png");

    await element(by.id("SubmitButton")).click();

    await browser.gl.utils.waitUntilPresent(by.id("ReceiptCode"));

    await browser.gl.utils.takeScreenshot("whistleblower/receipt.png");

    return await element(by.id("ReceiptCode")).getAttribute("value");
  };

  this.submitFile = async function(fname) {
    await element(by.xpath("//input[@type='file']")).sendKeys(fname);
  };
};
