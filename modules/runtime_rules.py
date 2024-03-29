from modules import generic_pull_put_migrate
import time

def migrate(dst_session, src_session_list, options, single_mode, logger):
    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'Runtime Rules - Container', '/api/v1/policies/runtime/container', 'name', 'rules', single_mode, logger, translate_custom_rule_ids=True)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'Runtime Rules - App Embedded', '/api/v1/policies/runtime/app-embedded', 'name', 'rules', single_mode, logger)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'Runtime Rules - Host', '/api/v1/policies/runtime/host', 'name', 'rules', single_mode, logger, translate_custom_rule_ids=True)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'Runtime Rules - Serverless', '/api/v1/policies/runtime/serverless', 'name', 'rules', single_mode, logger)