## How to prepare an AKV instance for the demo.
### Bring up an instance of Azure key vault(TODO)
First you need to create an Azure Key Vault on your resource group

### Create a service principal(in case is not created)
Here at Santander if you ask for a resource group with an Azure Key Vault inside  you should already have a default service principal created already for that resource group.

If that is not the case you need to create a new one with the following command from the azure CLI.
```
az ad sp create-for-rbac --name http://my-application --skip-assignment
```
That command should return the following json:
```
{
    "appId": "generated app id",
    "displayName": "my-application",
    "name": "http://my-application",
    "password": "random password",
    "tenant": "tenant id"
}
```
In this json we have to take 3 of these values and set their values on the "config.py" file.
```
CLIENT_ID = <appId>
PASSWORD = <password>
TENANT_ID = <tenant>
```

### Retrieve service principal for configuration
In case you have created yourself the service principal you don't need to execute this step, because what we will do is to retrieve the info is to retrieve the same info that you get on the json while creating the service principal.

First you need to enter the Secrets tab from the AKV
![Secrets_Azure](./images_readme/Cap1.PNG)
Copy the name the name of that secret, the display-name of your service principal.
![Secrets_Azure](./images_readme/Cap3.PNG)
Now execute the following command with that display-name.
```
az ad sp list --display-name <name>
```

You will get a very long json from which the information we need is at the very begining.
```
[
  {
    "accountEnabled": "True",
    "addIns": [],
    "alternativeNames": [],
    "appDisplayName": "sdis1glbsp3blkpocauth001",
    "appId": "07e9b304-3036-46bb-af24-1eac6124fb48",
    "appOwnerTenantId": "35595a02-4d6d-44ac-99e1-f9ab4cd872db",
    "appRoleAssignmentRequired": false,
    "appRoles": [],
    ...
  }
]
```
You can set now 2 of the variables from the config.py file with the "appOwnerTenantId" and "appId".
```
CLIENT_ID = <appId>
TENANT_ID = <appOwnerTenantId>
```
After this you need to access again the secrets tab and click on the name of the secret that you copied before, to acces the info for that service pricipal.
You will get a view like this.
![Secrets_password](./images_readme/Cap2.PNG)
Just click on the button "Show secret" and copy that value. This value is the password that you need to configure on the config.py.

```
PASSWORD = <secret-value>
```

### Create the key inside AKV to be compatible with Ethereum (TODO)

### Find the key version and set it on config file (TODO)
