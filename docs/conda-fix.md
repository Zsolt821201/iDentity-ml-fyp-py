check 

%USER%\Documents\WindowsPowerShell\profile.ps1


conda init powershell

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

Set-ExecutionPolicy RemoteSigned