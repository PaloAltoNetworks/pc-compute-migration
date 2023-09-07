from modules import generic_pull_put_migrate
from modules import generic_pull_post_migrate

def create_name(single_mode, session_name, data_name):
    if single_mode:
        return data_name
    else:
        session_name + ' - ' + data_name

def migrate(dst_session, src_session_list, options, single_mode, logger):
    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'Compliance Rules - Hosts - Host', '/api/v1/policies/compliance/host', 'name', 'rules', single_mode, logger)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'Compliance Rules - Hosts - VM', '/api/v1/policies/compliance/vms', 'name', 'rules', single_mode, logger)
#========================================================================================================================================================================================================
    import time
    from tqdm import tqdm
    import json
    import os
    #Const
    MODULE = 'Compliance Rules - Application Control'
    NAME_INDEX = 'name'
    PULL_ENDPOINT = '/api/v1/application-control/host'
    PUSH_ENDPOINT = '/api/v1/application-control/host'
    DATA_INDEX = 'applicationControl'

    #Logic
    start_time = time.time()
    logger.info(f'Starting {MODULE}s migration')

    for src_session in tqdm(src_session_list, desc='Processing Consoles/Projects', leave=False, initial=1):
        #Compare entities------------------------------------------------------
        logger.debug(f'Comparing {MODULE}s from \'{src_session.tenant}\'')

        #Pull entities
        dst_res = dst_session.request('GET', PULL_ENDPOINT)
        dst_entities = dst_res.json()
        dst_names = []

        dst_names = []
        if dst_entities:
            dst_names = [x[NAME_INDEX] for x in dst_entities]
        else:
            dst_entities = []


        res = src_session.request('GET', PULL_ENDPOINT)
        src_entities = []

        src_entities = res.json()
        
        #Highest Val
        high_id = 0
        for ent in dst_entities:
            curr_id = int(ent['_id'])
            if curr_id > high_id:
                high_id = curr_id
        high_id += 1

        #Fixes error "{"err":"rule ID xx is outside the allowed bounds [11000, 11999]"} "
        if high_id < 11000:
            high_id = 11000


        id_maps = {}
        if os.path.exists(f'id_mappings/{DATA_INDEX}-{src_session.tenant}.json'):
            with open(f'id_mappings/{DATA_INDEX}-{src_session.tenant}.json', 'r') as infile:
                id_maps = json.load(infile)

        #Compare entities and combine, update IDs
        with open(f'id_mappings/{DATA_INDEX}-{src_session.tenant}.json', 'w') as outfile:
            entities_to_migrate = []
            if src_entities:
                for ent in src_entities:
                    new_name = create_name(single_mode,src_session.tenant, ent[NAME_INDEX])
                    if new_name not in dst_names:
                        id_maps.update({str(ent['_id']): int(high_id)})
                        ent['_id'] = high_id
                        high_id += 1
                        entities_to_migrate.append(ent)

            json.dump(id_maps, outfile)

        #Migrate entities------------------------------------------------------
        if entities_to_migrate:
            logger.debug(f'Migrating {MODULE}s')
        else:
            logger.debug(f'No {MODULE}s to migrate')
            # continue

        for index, ent_payload in tqdm(enumerate(entities_to_migrate), desc='Custom Rules Migration', leave=False):
            #Create custom name for entity
            new_name = create_name(single_mode,src_session.tenant, ent_payload[NAME_INDEX])
            entities_to_migrate[index][NAME_INDEX] = new_name

            logger.info(f'Adding {MODULE} from \'{src_session.tenant}\'')
            dst_session.request('PUT', f'{PUSH_ENDPOINT}', json=entities_to_migrate[index])
        

    end_time = time.time()
    time_completed = round(end_time - start_time,3)
    logger.info(f'{MODULE}s migration finished - {time_completed} seconds')
#========================================================================================================================================================================================================


    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'Compliance Rules - Containers and Images - Deployed', '/api/v1/policies/compliance/container', 'name', 'rules', single_mode, logger)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'Compliance Rules - Functions - Function', '/api/v1/policies/compliance/serverless', 'name', 'rules', single_mode, logger)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'Compliance Rules - Functions - CI', '/api/v1/policies/compliance/ci/serverless', 'name', 'rules', single_mode, logger)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'Compliance Rules - Trusted Images - Trust Groups', '/api/v1/trust/data', 'name', 'groups', single_mode, logger, col_dep=False)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'Compliance Rules - Trusted Images - Policy', '/api/v1/trust/data', 'name', 'policy', single_mode, logger, data_index2='rules') #Trust groups must come first

    

