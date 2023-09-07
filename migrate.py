import argparse
import os

import pcpi
from pcpi import session_loader
from pcpi import saas_session_manager
from loguru import logger as loguru_logger
from tqdm import tqdm

from modules.c_print import c_print
from modules.migrate import migrate

#CONSTANTS---------------------------------------------------------------------
#Arg parsing
DEFAULT_CREDENTIALS_PATH =  'cwp_migrate_credentials.json'
CREDENTIALS_HELP_TEXT =     '<full_path_to_credentials_json_file>'
QUIET_HELP_TEXT =           'Enable progress bar in logging output (True/False)'

#Help text
README_CREDENTIALS_LINK = "https://github.com/PaloAltoNetworks/pc-cwp-migration/blob/main/README.md"


#Getting command line arguments
parser = argparse.ArgumentParser()

parser.add_argument(
    '--credentials_path', 
    type=str, 
    required=False, 
    default=DEFAULT_CREDENTIALS_PATH,
    help=CREDENTIALS_HELP_TEXT
    )
parser.add_argument(
    '--quiet',
    type=bool,
    required=False,
    default=True,
    help=QUIET_HELP_TEXT
)

args = parser.parse_args()

print(args.credentials_path)

#Logger and TQDM setup
loguru_logger.remove()

if args.quiet:
    loguru_logger.level("BAR", no=4)
else:
    loguru_logger.level("BAR", no=51)

loguru_logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True, level='BAR')
loguru_logger.add('logs/{time:DD-MM-YYYY_HH:mm:ss}.log', level='TRACE')


#Get credentials for all consoles----------------------------------------------
if os.path.exists(args.credentials_path):
    c_print('Loading Console credentials...', color='blue')
    c_print(f'See "CREDENTIALS" section of documentation for details.\n\
        {README_CREDENTIALS_LINK}', color='yellow')
else:
    c_print('No credentials found. Generating file...', color='blue')
    c_print(f'See "CREDENTIALS" section of documentation for details.\n\
        {README_CREDENTIALS_LINK}', color='yellow')
    print()
    c_print(
        'Enter migration DESTINATION console credentials first.',
        color='green')
    c_print(
        'Enter migration SOURCE console credential(s) subsequently.',
        color='green')
    print()
    print()

session_managers = session_loader.load_config(
    args.credentials_path, 
    min_tenants=2, 
    logger=loguru_logger
    )



single_mode = True
create_resource_lists_for_collections = False

cspm_session = {}
dst_session = session_managers[0].create_cwp_session()
src_session_list = []
for man in session_managers[1:]:
    src_session_list.append(man.create_cwp_session())


if len(src_session_list) > 1:
    print()
    c_print('Denote each rule/policy/collection with project name it was sourced from? (Recommended when migrating projects) Y/N: ', color='yellow')    
    single_mode_input = input()
    if single_mode_input.lower() == 'y' or single_mode_input.lower() == 'yes':
        single_mode = True
    else:
        single_mode = False


if type(dst_session) == pcpi._saas_cwp_session.SaaSCWPSession:
    print()
    c_print('For each collection, create a Resource List? (Recommended for RBAC) Y/N: ', color='yellow')
    rl_input = input()
    if rl_input.lower() == 'y' or rl_input.lower() == 'yes':
        create_resource_lists_for_collections = True
    else:
        create_resource_lists_for_collections = False

    cspm_session = session_managers[0].create_cspm_session()



#Get modules to migrate--------------------------------------------------------
#Helper function
def get_y_n(res: str) -> bool:
    if res.lower().strip() == 'yes' or res.lower().strip() == 'y':
        return True
    else:
        return False



starting_modules = {
    'Collections': {},
    'Tags': {},
    'Credentials': {},
    'General Settings': {},
    'Custom Feed': {},
    'CNNS Rules': {},
    'Compliance Rules': {},
    'Custom Rules': {},
    'Access Rules': {},
    'Runtime Rules': {},
    'Vulnerability Rules': {},
    'WAAS Firewall Rules': {},
    'Alert Profiles': {}

    
    # 'Registries': {},
    # 'Proxy Settings': {}
}

enabled_modules = {}

print()
c_print('Migration Configuration', color='yellow')
print()
c_print('You will now be prompted with a series of Yes/No questions to configure the migration process.', color='blue')
print()
c_print('Do you want to migrate all modules? Y/N', color='green')
if get_y_n(input()):
    c_print('Press enter key to begin migration...', color='yellow')
    input()
    migrate(dst_session, src_session_list, starting_modules, single_mode, cspm_session, create_resource_lists_for_collections, loguru_logger)
else:
    for mod_name in starting_modules.keys():
        c_print(f'Do you want to enable the \'{mod_name}\' module? Y/N', color='blue')
        if get_y_n(input()):
            enabled_modules.update({mod_name:starting_modules[mod_name]})

    c_print('Press enter key to begin migration...', color='yellow')
    input()
    migrate(dst_session, src_session_list, enabled_modules, single_mode, cspm_session, create_resource_lists_for_collections, loguru_logger)
