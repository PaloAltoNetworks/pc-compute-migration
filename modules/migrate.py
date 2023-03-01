from modules import alert_profiles
from modules import collections
from modules import compliance_rules
from modules import credentials
from modules import custom_feed
from modules import general_settings
from modules import registries
from modules import runtime_rules
from modules import tags
from modules import vulnerability_rules
from modules import access_rules
from modules import cnss_rules
from modules import custom_rules
from modules import waas_firewall_rules
from modules import proxy_settings

from tqdm import tqdm

def migrate(dst_session: object, src_session_list: list, enabled_modules: dict, logger) -> None:

    for module in tqdm(enabled_modules.keys(), desc='Processing Modules', leave=False, initial=1):
            if module == 'Collections':
                options = enabled_modules[module]
                collections.migrate(dst_session, src_session_list, options, logger)
            elif module == 'Tags':
                options = enabled_modules[module]
                tags.migrate(dst_session, src_session_list, options, logger)

            elif module == 'General Settings':
                options = enabled_modules[module]
                general_settings.migrate(dst_session, src_session_list, options, logger)

            elif module == 'Custom Feed':
                options = enabled_modules[module]
                custom_feed.migrate(dst_session, src_session_list, options, logger)

            elif module == 'Access Rules':
                options = enabled_modules[module]
                access_rules.migrate(dst_session, src_session_list, options, logger)

            elif module == 'CNSS Rules':
                options = enabled_modules[module]
                cnss_rules.migrate(dst_session, src_session_list, options, logger)

            elif module == 'Compliance Rules':
                options = enabled_modules[module]
                compliance_rules.migrate(dst_session, src_session_list, options, logger)

            elif module == 'Custom Rules':
                options = enabled_modules[module]
                custom_rules.migrate(dst_session, src_session_list, options, logger)

            elif module == 'Runtime Rules':
                options = enabled_modules[module]
                runtime_rules.migrate(dst_session, src_session_list, options, logger)

            elif module == 'Vulnerability Rules':
                options = enabled_modules[module]
                vulnerability_rules.migrate(dst_session, src_session_list, options, logger)

            elif module == 'WAAS Firewall Rules':
                options = enabled_modules[module]
                waas_firewall_rules.migrate(dst_session, src_session_list, options, logger)

            elif module == 'Alert Profiles':
                options = enabled_modules[module]
                alert_profiles.migrate(dst_session, src_session_list, options, logger)

            elif module == 'Cloud Discovery':
                options = enabled_modules[module]
                cloud_accounts.migrate(dst_session, src_session_list, options, logger)

            elif module == 'Credentials':
                options = enabled_modules[module]
                credentials.migrate(dst_session, src_session_list, options, logger)

            elif module == 'Registries':
                options = enabled_modules[module]
                registries.migrate(dst_session, src_session_list, options, logger)

            elif module == 'Proxy Settings':
                options = enabled_modules[module]
                proxy_settings.migrate(dst_session, src_session_list, options, logger)

            else:
                logger.error(f'Unknown module name: \'{module}\' encountered. Skipping...')
