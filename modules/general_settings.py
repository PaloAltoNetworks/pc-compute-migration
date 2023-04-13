import time
from tqdm import tqdm

import json

def migrate(dst_session, src_session_list, options, logger):

    #Const
    RUNTIME =  '/api/v1/settings/runtime-secret-specs'
    RUNTIME_NAME = 'name'
    RUNTIME_MODULE = 'General Settings Runtime Rule'

    WAAS =      '/api/v1/policies/firewall/app/log-scrubbing'
    WAAS_NAME = 'name'
    WAAS_MODULE = 'General Settings WAAS Rule'

    
    #==============================================================================================Runtime Rules
    #Custom Pull Put migrate for Runtime Rules
    #Const
    MODULE = RUNTIME_MODULE
    NAME_INDEX = RUNTIME_NAME
    PULL_ENDPOINT = RUNTIME
    PUT_ENDPOINT = RUNTIME

    #Logic
    start_time = time.time()
    logger.info(f'Starting {MODULE}s migration')

    for src_session in tqdm(src_session_list, desc='Processing Consoles/Projects', leave=False):
        #Compare entities------------------------------------------------------
        logger.debug(f'Comparing {MODULE}s from \'{src_session.tenant}\'')

        #Pull entities
        res = dst_session.request('GET', PULL_ENDPOINT)
        dst_entities = res.json().get('customSpecs', [])
        dst_skip_default = res.json()['skipDefault']

        dst_entities_names = []
        if "customSpecs" in res.json():
            dst_entities_names = [x[NAME_INDEX] for x in res.json()['customSpecs']]

        res = src_session.request('GET', PULL_ENDPOINT)
        src_entities = res.json().get('customSpecs', [])

        #Compare entities
        entities_to_migrate = []
        for ent in src_entities:
            new_name = src_session.tenant + ' - ' + ent[NAME_INDEX]
            if new_name not in dst_entities_names:
                entities_to_migrate.append(ent)

        #Migrate entities------------------------------------------------------
        if entities_to_migrate:
            logger.debug(f'Migrating {MODULE}s')
        else:
            logger.debug(f'No {MODULE}s to migrate')
            continue

        for index, ent_payload in enumerate(entities_to_migrate):
            #Create custom name for entity
            new_name = src_session.tenant + ' - ' + ent_payload[NAME_INDEX]
            ent_payload[index][NAME_INDEX] = new_name

        #Extend existing src_entities with new entities
        dst_entities.extend(entities_to_migrate)

        #Add entities in a single PUT, including the existing entities and the new ones
        #Create valid payload for this endpoint
        payload = {
            'skipDefault': dst_skip_default,
            'customSpecs': dst_entities
        }
        logger.info(f'Adding {MODULE}s from \'{src_session.tenant}\'')
        dst_session.request('PUT', PUT_ENDPOINT, json=payload)

    end_time = time.time()
    time_completed = round(end_time - start_time,3)
    logger.info(f'{MODULE}s migration finished - {time_completed} seconds')

    #==============================================================================================WAAS Rules
    #WAAS rules work with generic implementation
        #Const
    MODULE = WAAS_MODULE
    NAME_INDEX = WAAS_NAME
    PULL_ENDPOINT = WAAS
    PUT_ENDPOINT = WAAS

    #Logic
    start_time = time.time()
    logger.info(f'Starting {MODULE}s migration')

    for src_session in tqdm(src_session_list, desc='Processing Consoles/Projects', leave=False):
        #Compare entities------------------------------------------------------
        logger.debug(f'Comparing {MODULE}s from \'{src_session.tenant}\'')

        #Pull entities
        res = dst_session.request('GET', PULL_ENDPOINT)
        dst_entities = res.json()
        dst_entities_names = [x[NAME_INDEX] for x in res.json()]
        res = src_session.request('GET', PULL_ENDPOINT)
        src_entities = res.json()
        
        #Compare entities
        entities_to_migrate = []
        for ent in src_entities:
            new_name = src_session.tenant + ' - ' + ent[NAME_INDEX]
           
            #FIXME
            if new_name not in dst_entities_names and ent.get('placeholder', '') != '': #if placeholder is missing its a default rule #TODO this is not true and will cause valid custom rules to not migrate
                entities_to_migrate.append(ent)

        #Migrate entities------------------------------------------------------
        if entities_to_migrate:
            logger.debug(f'Migrating {MODULE}s')
        else:
            logger.debug(f'No {MODULE}s to migrate')
            continue

        for index, ent_payload in enumerate(entities_to_migrate):
            #Create custom name for entity
            new_name = src_session.tenant + ' - ' + ent_payload[NAME_INDEX]
            entities_to_migrate[index][NAME_INDEX] = new_name

        #Extend existing src_entities with new entities
        with open('out1.json', 'w') as outfile:
            json.dump(dst_entities, outfile)
        dst_entities.extend(entities_to_migrate)
        with open('out2.json', 'w') as outfile:
            json.dump(dst_entities, outfile)

        #Add entities in a single PUT, including the existing entities and the new ones
        logger.info(f'Adding {MODULE}s from \'{src_session.tenant}\'')
        dst_session.request('PUT', PUT_ENDPOINT, json=dst_entities)

    end_time = time.time()
    time_completed = round(end_time - start_time,3)
    logger.info(f'{MODULE}s migration finished - {time_completed} seconds')

