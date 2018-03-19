var page = require('webpage').create();
page.open('https://newfeedback.bmsit.ac.in/__/__/--/__/__reports/VISHAKHAY', function(status) {
  console.log("Status: " + status);
  if(status === "success") {
    console.log('Done');
  }
  phantom.exit();
});
