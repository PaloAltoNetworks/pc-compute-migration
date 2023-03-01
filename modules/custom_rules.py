import time
from tqdm import tqdm

def migrate(dst_session, src_session_list, options, logger):
    MODULE = 'Custom Rules'
    NAME_INDEX = 'name'
    PULL_ENDPOINT = '/api/v1/custom-rules'
    PUSH_ENDPOINT = '/api/v1/custom-rules'

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

        #Compare entities and combine
        entities_to_migrate = []
        if src_entities:
            for ent in src_entities:
                if ent['owner'] == 'system':
                    continue
                new_name = src_session.tenant + ' - ' + ent[NAME_INDEX]
                if new_name not in dst_names:
                    ent['_id'] = high_id
                    high_id += 1
                    entities_to_migrate.append(ent)

        #Migrate entities------------------------------------------------------
        if entities_to_migrate:
            logger.debug(f'Migrating {MODULE}s')
        else:
            logger.debug(f'No {MODULE}s to migrate')
            continue

        for index, ent_payload in tqdm(enumerate(entities_to_migrate), desc='Custom Rules Migration', leave=False):
            #Create custom name for entity
            new_name = src_session.tenant + ' - ' + ent_payload[NAME_INDEX]
            entities_to_migrate[index][NAME_INDEX] = new_name
            _id = ent_payload['_id']

            #Add entity
            logger.info(f'Adding {MODULE} from \'{src_session.tenant}\'')
            dst_session.request('PUT', f'{PUSH_ENDPOINT}/{_id}', json=ent_payload)
        

    end_time = time.time()
    time_completed = round(end_time - start_time,3)
    logger.info(f'{MODULE}s migration finished - {time_completed} seconds')