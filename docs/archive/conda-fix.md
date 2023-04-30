
# Conda Fix

## Check

%USER%\Documents\WindowsPowerShell\profile.ps1

```bash
conda init powershell
```

## Visual Code Settings

Open preferences (Ctrl + ,) and search for python.
Ensure you have the following settings in your settings.json file

```json
"python.condaPath": "~/anaconda3/Scripts/conda-script.py",
"python.defaultInterpreterPath": "~/anaconda3/python.exe",
"python.terminal.activateEnvironment": true,
```

## Visual Code Terminal Error

```bash

Error 
```bash
. : File C:\Users\%user%\Documents\WindowsPowerShell\profile.ps1 cannot be loaded because running scripts is disabled on this system. For more information, 
see about_Execution_Policies at https:/go.microsoft.com/fwlink/?LinkID=135170.
At line:1 char:3
+ . 'C:\Users\%user%\Documents\WindowsPowerShell\profile.ps1'
+   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : SecurityError: (:) [], PSSecurityException
    + FullyQualifiedErrorId : UnauthorizedAccess
```

Fix

## PowerShell

```ps1
Set-ExecutionPolicy RemoteSigned
```
