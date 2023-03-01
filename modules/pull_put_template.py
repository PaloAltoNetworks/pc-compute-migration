import time
from tqdm import tqdm
def migrate(dst_session, src_session_list, options, logger):
    #Const
    MODULE = ''
    NAME_INDEX = ''
    PULL_ENDPOINT = '/api/v1/'
    PUT_ENDPOINT = '/api/v1/'

    #Logic
    start_time = time.time()
    logger.info(f'Starting {MODULE}s migration')

    for src_session in tqdm(src_session_list, desc='Processing Consoles/Projects', leave=False, initial=1):
        #Compare entities------------------------------------------------------
        logger.debug(f'Comparing {MODULE}s from \'{src_session.tenant}\'')

        #Pull entities
        dst_res = dst_session.request('GET', PULL_ENDPOINT)
        dst_entities = dst_res.json()
        dst_entities_names = [x[NAME_INDEX] for x in dst_res.json()]

        res = src_session.request('GET', PULL_ENDPOINT)
        src_entities = res.json()
        
        #Compare entities
        entities_to_migrate = []
        if src_entities:
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
            entities_to_migrate[index][NAME_INDEX] = new_name

        #Extend existing src_entities with new entities
        dst_entities.extend(entities_to_migrate)

        #Add entities in a single PUT, including the existing entities and the new ones
        logger.info(f'Adding {MODULE}s from \'{src_session.tenant}\'')
        dst_session.request('PUT', PUT_ENDPOINT, json=dst_entities)

    end_time = time.time()
    time_completed = round(end_time - start_time,3)
    logger.info(f'{MODULE}s migration finished - {time_completed} seconds')