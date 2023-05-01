
# [iDentity - Biometric Face Recognition Time Management System](https://github.com/Zsolt821201/iDentity-ml-fyp-py)

## Aim

This project aims to develop a web-based time management and user identification system that leverages facial recognition technology. The technology employs cameras to take a picture of the user’s face and then compare it to a previously registered image in the system to verify the user’s identity. The system grants access when the user’s identification has been verified and logs the user’s entry and exit times. This method may be utilized in various settings, such as businesses, institutions of higher learning, and healthcare facilities, to enhance security and time management. To see the full report, go to the [report](./docs/report.pdf).

## Requirements

- [Python 3.9](https://www.python.org/downloads/) - Python is a programming language that lets you work quickly and integrate systems more effectively.

### IDEs

- [VS Code](https://code.visualstudio.com/) - Code editing.Redefined. Free. Built on open source. Runs everywhere.[^vs-code]

[^vs-code]: The Extensions recommended for this project are in [extensions.json](./.vscode/extensions.json)

### Source Code Management

- [Git](https://git-scm.com/) is a free and open-source distributed version control system designed to handle everything from small to very large projects with speed and efficiency.
- [GitHub Desktop](https://desktop.github.com/) - Simple collaboration from your desktop
- [WinMerge](https://winmerge.org/) is an Open Source differencing and merging tool for Windows.


### Online Tools

- [GitHub](https://www.github.com) is a web-based hosting service for version control using Git. It offers all of the distributed version control and source code management (SCM) functionality of Git as well as adding its features.
- [gitignore.io](https://www.toptal.com/developers/gitignore) - Create useful .gitignore files for your project
- [mermaid-js.github.io](https://mermaid-js.github.io/mermaid-live-editor) - Live Editor for the Mermaid diagramming language
- [plantuml.com](https://plantuml.com/) - Open-source tool that uses simple textual descriptions to draw UML diagrams.

## Run Application

1. Clone the repository

    ```bash
    git clone https://github.com/zsolt821201/identity-ml-fyp-py.git
    ```

2. Install dependencies
    - With Pip (To fast execute, run on Windows [pip-install.cmd](./pip-install.cmd))

        ```bash
        pip install -r identity-django/requirements.txt
        ```

    - With conda (To fast execute, run on Windows [conda-install.cmd](./conda-install.cmd))

        ```bash
        conda install --file identity-django/requirements.txt
        ```

3. Run the app
    Open VS Code and run the app by pressing the `F5` Key or  
    Open a terminal and run the following commands:

    ```bash
    cd identity-django
    ```

    ```bash
    python manage.py runserver
    ```

4. Open the app in your browser
    <http://localhost:8000>

Built-in user accounts are:

| Username       | Password       | Role  | Note                             |
|----------------|----------------|-------|----------------------------------|
| Admin          | Password       | admin | Built in admin account           |
| ZsoltToth      | Password1234!  | user  | Built in user account            |
| JoshuaFluke    | Letmein1$      | user  | Built in user account            |

## Testing

This project uses the following testing frameworks: Django Unit Tests, Behave BDD Tests, and Selenium WebDriver.

### Run Django Unit Tests

To run the tests, open a terminal and run the following command:

```bash
cd identity-django
```

```bash
python manage.py test identity.tests
```

To run a select test for example tests in the `identity.tests.FaceRecognitionUtilityTests.test_detect_face_with_blank` module, open a terminal and run the following command:

```bash
python manage.py test identity.tests.FaceRecognitionUtilityTests.test_detect_face_with_blank
```

### BDD Behave Tests

To test the App in the Chrome browser, you need to install the Selenium WebDriver for Chrome.

#### Test Requirements

To test the App in the Chrome browser, you need to install the Selenium WebDriver for Chrome.

- [Chrome](https://www.google.com/chrome/) - Google Chrome is a cross-platform web browser developed by Google.
- [ChromeDriver](https://sites.google.com/chromium.org/driver/?pli=1) - WebDriver is an open-source tool for automated testing of webapps across many browsers.[^chrome-driver]

[^chrome-driver]: In this project, a copy of ChromeDriver is included in the [/behave_test/driver/](../behave_test/driver/) folder.

To run the tests, open a terminal and run the following command:

```bash
behave behave_test/features/feature_files/  -f pretty -o out/behave-logs/all.txt
```

To run selected tests for example tests with the tag `zsolt`, open a terminal and run the following command:

```bash
behave behave_test/features/feature_files/ --tags=zsolt -f pretty -o out/behave-logs/zsolt.txt
```

---
Copyright &copy; 2023, [Zsolt Toth](https://github.com/Zsolt821201/iDentity-ml-fyp-py)
