
# Selenium Testing

To test the App in the Chrome browser, you need to install the Selenium WebDriver for Chrome.

In this project a copy of ChromeDriver is included in the [/behave_test/driver/](../behave_test/driver/) folder.

You can use this copy or download the latest version from the [ChromeDriver website](https://sites.google.com/chromium.org/driver/?pli=1)

## Running the tests

To run the tests, you need to open a terminal and navigate to the [/behave_test/](../behave_test/) folder.

Then run the following command:

```bash
behave behave_test/features/feature_files/ --tags=zsolt -f pretty -o out/behave-logs/zsolt.txt
```
