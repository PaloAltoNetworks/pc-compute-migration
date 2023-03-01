import time
from tqdm import tqdm

from modules import generic_pull_put_migrate

def migrate(dst_session, src_session_list, options, logger):

    #==============================================================================================IP Reputation List Addresses
    #Const
    MODULE = 'IP Reputation List Addresses'
    PULL_ENDPOINT = 'api/v1/feeds/custom/ips'
    PUSH_ENDPOINT = 'api/v1/feeds/custom/ips'

    #Logic
    start_time = time.time()
    logger.info(f'Starting {MODULE}s migration')

    for src_session in tqdm(src_session_list, desc='Processing Consoles/Projects', leave=False, initial=1):
        #Compare entities------------------------------------------------------
        logger.debug(f'Comparing {MODULE}s from \'{src_session.tenant}\'')

        #Pull entities
        dst_res = dst_session.request('GET', PULL_ENDPOINT)
        dst_entities = []
        if dst_res.json():
            dst_entities = dst_res.json()['feed']

        res = src_session.request('GET', PULL_ENDPOINT)
        src_entities = []
        if res.json():
            src_entities = res.json()['feed']
        
        #Compare entities
        entities_to_migrate = []
        for ent in src_entities:
            if ent not in dst_entities:
                entities_to_migrate.append(ent)

        #Migrate entities------------------------------------------------------
        if entities_to_migrate:
            logger.debug(f'Migrating {MODULE}s')
        else:
            logger.debug(f'No {MODULE}s to migrate')
            continue
        
        dst_entities.extend(entities_to_migrate)

        payload = dst_res.json()
        payload['feed'] = dst_entities

        #Add entity
        logger.info(f'Adding {MODULE} from \'{src_session.tenant}\'')
        dst_session.request('PUT', PUSH_ENDPOINT, json=payload)

    end_time = time.time()
    time_completed = round(end_time - start_time,3)
    logger.info(f'{MODULE}s migration finished - {time_completed} seconds')

    #==============================================================================================Cookie Cutter migrations

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'Malware Signatures/Trusted Executables', 'api/v1/feeds/custom/malware', 'name', 'feed', logger, col_dep=False)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'Custom Vulnerabilities', 'api/v1/feeds/custom/custom-vulnerabilities', 'name', 'rules', logger, col_dep=False)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'CVE Allow List', '/api/v1/feeds/custom/cve-allow-list', 'description', 'rules', logger, col_dep=False)



    # #Const
    # MODULE = 'Malware Signatures/Trusted Executables'
    # NAME_INDEX = 'name'
    # PULL_ENDPOINT = 'api/v1/feeds/custom/malware'
    # PUSH_ENDPOINT = 'api/v1/feeds/custom/malware'

    # #Logic
    # start_time = time.time()
    # logger.info(f'Starting {MODULE}s migration')

    # for src_session in tqdm(src_session_list, desc='Processing Consoles/Projects', leave=False, initial=1):
    #     #Compare entities------------------------------------------------------
    #     logger.debug(f'Comparing {MODULE}s from \'{src_session.tenant}\'')

    #     #Pull entities
    #     dst_res = dst_session.request('GET', PULL_ENDPOINT)
    #     dst_entities = []
    #     if dst_res.json():
    #         dst_entities = dst_res.json()['feed']

    #     if dst_entities:
    #         dst_names = [x[NAME_INDEX] for x in dst_entities]

    #     res = src_session.request('GET', PULL_ENDPOINT)
    #     src_entities = []
    #     if res.json():
    #         src_entities = res.json()['feed']
        
    #     #Compare entities
    #     entities_to_migrate = []
    #     if src_entities:
    #         for ent in src_entities:
    #             new_name = src_session.tenant + ' - ' + ent[NAME_INDEX]
    #             if new_name not in dst_names:
    #                 entities_to_migrate.append(ent)

    #     #Migrate entities------------------------------------------------------
    #     if entities_to_migrate:
    #         logger.debug(f'Migrating {MODULE}s')
    #     else:
    #         logger.debug(f'No {MODULE}s to migrate')
    #         continue

    #     for index, ent_payload in enumerate(entities_to_migrate):
    #         #Create custom name for entity
    #         new_name = src_session.tenant + ' - ' + ent_payload[NAME_INDEX]
    #         entities_to_migrate[index][NAME_INDEX] = new_name
        
    #     dst_entities.extend(entities_to_migrate)

    #     payload = dst_res.json()
    #     payload['feed'] = dst_entities

    #     #Add entity
    #     logger.info(f'Adding {MODULE} from \'{src_session.tenant}\'')
    #     dst_session.request('PUT', PUSH_ENDPOINT, json=payload)

    # end_time = time.time()
    # time_completed = round(end_time - start_time,3)
    # logger.info(f'{MODULE}s migration finished - {time_completed} seconds')

    #==============================================================================================Custom Vulnerabilities
    # #Const
    # MODULE = 'Custom Vulnerabilities'
    # NAME_INDEX = 'name'
    # PULL_ENDPOINT = 'api/v1/feeds/custom/custom-vulnerabilities'
    # PUSH_ENDPOINT = 'api/v1/feeds/custom/custom-vulnerabilities'
    # DATA_INDEX = 'rules'

    # #Logic
    # start_time = time.time()
    # logger.info(f'Starting {MODULE}s migration')

    # for src_session in tqdm(src_session_list, desc='Processing Consoles/Projects', leave=False, initial=1):
    #     #Compare entities------------------------------------------------------
    #     logger.debug(f'Comparing {MODULE}s from \'{src_session.tenant}\'')

    #     #Pull entities
    #     dst_res = dst_session.request('GET', PULL_ENDPOINT)
    #     dst_entities = []
    #     if dst_res.json():
    #         dst_entities = dst_res.json()[DATA_INDEX]

    #     if dst_entities:
    #         dst_names = [x[NAME_INDEX] for x in dst_entities]

    #     res = src_session.request('GET', PULL_ENDPOINT)
    #     src_entities = []
    #     if res.json():
    #         src_entities = res.json()[DATA_INDEX]
        
    #     #Compare entities
    #     entities_to_migrate = []
    #     if src_entities:
    #         for ent in src_entities:
    #             new_name = src_session.tenant + ' - ' + ent[NAME_INDEX]
    #             if new_name not in dst_names:
    #                 entities_to_migrate.append(ent)

    #     #Migrate entities------------------------------------------------------
    #     if entities_to_migrate:
    #         logger.debug(f'Migrating {MODULE}s')
    #     else:
    #         logger.debug(f'No {MODULE}s to migrate')
    #         continue

    #     for index, ent_payload in enumerate(entities_to_migrate):
    #         #Create custom name for entity
    #         new_name = src_session.tenant + ' - ' + ent_payload[NAME_INDEX]
    #         entities_to_migrate[index][NAME_INDEX] = new_name
        
    #     dst_entities.extend(entities_to_migrate)

    #     payload = dst_res.json()
    #     payload[DATA_INDEX] = dst_entities

    #     #Add entity
    #     logger.info(f'Adding {MODULE} from \'{src_session.tenant}\'')
    #     dst_session.request('PUT', PUSH_ENDPOINT, json=payload)

    # end_time = time.time()
    # time_completed = round(end_time - start_time,3)
    # logger.info(f'{MODULE}s migration finished - {time_completed} seconds')
