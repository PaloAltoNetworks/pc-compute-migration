# Pre Alpha 04/01/2023

### Features

Migration of multiple CWPP Consoles into a Single Console. EX: Migrating multiple projects into a single SaaS console.

Entities that are migrated have their name/id modified to have the user supplied console name or project ID prepended to their name/id. This ensures that if multiple different consoles/projects had rules with the same name, each rule will be able to migrate properly.

Migrate all modules or pick and choose.

CWP console configurations that can be migrated by this script:

- 'Collections'
- 'Tags'
- 'General Settings'
- 'Custom Feed Settings’
- 'CNNS Rules'
- 'Compliance Rules'
- 'Custom Rules'
- 'Access Rules'
- 'Runtime Rules'
- 'Vulnerability Rules'
- ‘WAAS Firewall Rules'
- 'Credentials'
- 'Alert Profiles’

### Alpha caveats:

- Credentials all migrate "empty" and will have to be reconfigured post migration.
- - Not all credentials are migrating “empty” yet. These include:
- - - Azure Credentials
- - - Certificate Credentials
- Alert Profiles are not fully supported yet, most types will migrate but not all.
- - Alert Profiles that are dependent on Certificate Credentials currently fail.
- - Out Of Band Alert Profiles are also not supported at this time.
- Registries are not yet supported

# Installation

```pip3 install -r requirements.txt```

# Quick start

Ensure all consoles and projects are on the same Prisma Cloud CWPP verison. Version mismatches will result in certain entities failing to migrate but the script will still run.

Gather keys, passwords, and URLs of all consoles and projects that will be involved in the migration.

Using a Linux or Unix based machine, invoke Python version 3.8 and up from a command line to run the script.

```python3 migrate.py```

When running for the first time, you will be asked to enter credentials first.

The first set of credentials entered are for the DESTINATION CWP Console where all entities will be migrated TO. Changes will be made to this CWP Console so it is important to ensure the correct console is used as the DESTINATION.

The subsequent credentials entered are for the SOURCE CWP Consoles where all the entities will be migrated FROM.

When entering credentials for Projects, make sure to set the Project flag to True when prompted. Also make sure to supply the correct Project Name/ID when prompted to. Failure to do so will render the script unable to make API calls to that project.

Examples:

![Alt text of the image](https://github.com/PaloAltoNetworks/pc-compute-migration/blob/main/images/saas_setup.png)

![Alt text of the image](https://github.com/PaloAltoNetworks/pc-compute-migration/blob/main/images/onprem_setup.png)

![Alt text of the image](https://github.com/PaloAltoNetworks/pc-compute-migration/blob/main/images/project_setup.png)

Once credentials have been set up, you will then be prompted with questions to configure run options for the migration.

To migrate all modules, reply with 'y' to the question 'Do you want to migrate all modules? Y/N'.

To customize which modules are migrated, reply 'n'. Then you will get to pick and choose which modules to enable.

```
Migration Configuration

You will now be prompted with a series of Yes/No questions to configure the migration process.

Do you want to migrate all modules? Y/N
n
Do you want to enable the 'Collections' module? Y/N
n
Do you want to enable the 'Tags' module? Y/N
n
Do you want to enable the 'General Settings' module? Y/N
n
Do you want to enable the 'Custom Feed' module? Y/N
n
Do you want to enable the 'CNNS Rules' module? Y/N
n
Do you want to enable the 'Compliance Rules' module? Y/N
n
Do you want to enable the 'Custom Rules' module? Y/N
n
Do you want to enable the 'Access Rules' module? Y/N
n
Do you want to enable the 'Runtime Rules' module? Y/N
n
Do you want to enable the 'Vulnerability Rules' module? Y/N
n
Do you want to enable the 'WAAS Firewall Rules' module? Y/N
n
Do you want to enable the 'Credentials' module? Y/N
n
Do you want to enable the 'Alert Profiles' module? Y/N
n
Press enter key to begin migration...
```


