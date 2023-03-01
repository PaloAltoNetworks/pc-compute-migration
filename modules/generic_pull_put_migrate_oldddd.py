import time
from tqdm import tqdm
def g_migrate(dst_session, src_session_list, module, endpoint, name_index, data_index, logger, skip='', skip_value=''):
    #Const
    MODULE = module
    NAME_INDEX = name_index
    PULL_ENDPOINT = endpoint
    PUSH_ENDPOINT = endpoint
    DATA_INDEX = data_index

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
            dst_entities = dst_res.json().get(DATA_INDEX, [])

        if dst_entities:
            dst_names = [x[NAME_INDEX] for x in dst_entities]

        res = src_session.request('GET', PULL_ENDPOINT)
        src_entities = []
        if res.json():
            src_entities = res.json().get(DATA_INDEX, [])
        
        #Compare entities
        entities_to_migrate = []
        if src_entities:
            for ent in src_entities:
                new_name = src_session.tenant + ' - ' + ent[NAME_INDEX]
                
                if skip:
                    if ent[skip] != skip_value:
                        if new_name not in dst_names:
                            entities_to_migrate.append(ent)
                else:
                    if new_name not in dst_names:
                        entities_to_migrate.append(ent)

        #Migrate entities------------------------------------------------------
        if entities_to_migrate:
            logger.info(f'Migrating {MODULE}s')
        else:
            logger.info(f'No {MODULE}s to migrate')
            continue

        for index, ent_payload in enumerate(entities_to_migrate):
            #Create custom name for entity
            new_name = src_session.tenant + ' - ' + ent_payload[NAME_INDEX]
            entities_to_migrate[index][NAME_INDEX] = new_name
        
        dst_entities.extend(entities_to_migrate)

        payload = dst_res.json()
        payload[DATA_INDEX] = dst_entities

        #Add entity
        logger.info(f'Adding {MODULE} from \'{src_session.tenant}\'')
        dst_session.request('PUT', PUSH_ENDPOINT, json=payload)

    end_time = time.time()
    time_completed = round(end_time - start_time,3)
    logger.info(f'{MODULE}s migration finished - {time_completed} seconds')