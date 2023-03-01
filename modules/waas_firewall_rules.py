from modules import generic_pull_put_migrate
from modules import generic_pull_post_migrate

def migrate(dst_session, src_session_list, options, logger):
    generic_pull_post_migrate.g_migrate(dst_session, src_session_list, 'WaSS Firewall Rules - Network Lists', '/api/v1/policies/firewall/app/network-list', '_id', '', logger, tag_dep=True, col_dep=False)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'WaSS Firewall Rules - Container - In-Line', '/api/v1/policies/firewall/app/container', 'name', 'rules', logger, tag_dep=True, network_list_dep=True)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'WaSS Firewall Rules - Container - Out-Of-Band', '/api/v1/policies/firewall/app/out-of-band', 'name', 'rules', logger, tag_dep=True, network_list_dep=True)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'WaSS Firewall Rules - Host - In-Line', '/api/v1/policies/firewall/app/host', 'name', 'rules', logger, tag_dep=True, network_list_dep=True)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'WaSS Firewall Rules - Host - Out-Of-Band', '/api/v1/policies/firewall/app/out-of-band', 'name', 'rules', logger, tag_dep=True, network_list_dep=True)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'WaSS Firewall Rules - App-Embedded', '/api/v1/policies/firewall/app/app-embedded', 'name', 'rules', logger, tag_dep=True, network_list_dep=True)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'WaSS Firewall Rules - Serverless', '/api/v1/policies/firewall/app/serverless', 'name', 'rules', logger, tag_dep=True, network_list_dep=True)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'WaSS Firewall Rules - Agentless', '/api/v1/policies/firewall/app/agentless', 'name', 'rules', logger, tag_dep=True, network_list_dep=True) 

    # generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'WaSS Firewall Rules - Sensitive Data', '/api/v1/policies/firewall/app/log-scrubbing', 'name', '', logger, tag_dep=True, col_dep=False) #Not needed to do here. Done elsewhere