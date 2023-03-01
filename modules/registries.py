import time
from tqdm import tqdm

def migrate(dst_session, src_session_list, options, logger):
    #TODO Registry AWS Credentials First


    logger.warning('Registry migration not implemented')
    #/api/v1/settings/registry

        #Const
    MODULE = 'Registries'
    NAME_INDEX = 'name'
    PULL_ENDPOINT = '/api/v1/settings/registry'
    PUSH_ENDPOINT = '/api/v1/settings/registry'
    DATA_INDEX = 'specifications'
    DATA_INDEX2 = ''
    COLLECTION_DEPENDENCY = True

    #Logic
    start_time = time.time()
    logger.info(f'Starting {MODULE}s migration')

    for src_session in tqdm(src_session_list, desc='Processing Consoles/Projects', leave=False, initial=1):
        #Compare entities------------------------------------------------------
        logger.debug(f'Comparing {MODULE}s from \'{src_session.tenant}\'')

        #Pull entities
        dst_res = dst_session.request('GET', PULL_ENDPOINT)
        dst_entities = []
        dst_names = []

        if DATA_INDEX:
            if dst_res.json():
                dst_entities = dst_res.json().get(DATA_INDEX, [])

                if DATA_INDEX2:
                    dst_entities = dst_entities.get(DATA_INDEX2, [])

            dst_names = []
            if dst_entities:
                dst_names = [x.get(NAME_INDEX,'') for x in dst_entities]

        else:
            if dst_res.json():
                dst_entities = dst_res.json()
                if dst_entities:
                    dst_names = [x.get(NAME_INDEX,'') for x in dst_entities]


        res = src_session.request('GET', PULL_ENDPOINT)
        src_entities = []

        if DATA_INDEX:
            if res.json():
                src_entities = res.json().get(DATA_INDEX, [])
                
                if DATA_INDEX2:
                    src_entities = src_entities.get(DATA_INDEX2, [])
        else:
            src_entities = res.json()
        
        #Compare entities
        entities_to_migrate = []
        if src_entities:
            for ent in src_entities:
                new_name = src_session.tenant + ' - ' + ent.get(NAME_INDEX,'')

                if new_name not in dst_names:
                    entities_to_migrate.append(ent)

        #Migrate entities------------------------------------------------------
        if entities_to_migrate:
            logger.debug(f'Migrating {MODULE}s')
        else:
            logger.debug(f'No {MODULE}s to migrate')
            continue

        for index, ent_payload in enumerate(entities_to_migrate):
            #Create custom name for entity
            new_name = src_session.tenant + ' - ' + ent_payload.get(NAME_INDEX,'')
            if entities_to_migrate[index].get(NAME_INDEX,''):
                entities_to_migrate[index][NAME_INDEX] = new_name
            
            if COLLECTION_DEPENDENCY == True:
                #Translate collection names
                for index2, col in enumerate(entities_to_migrate[index]['collections']):
                    entities_to_migrate[index]['collections'][index2] = src_session.tenant + ' - ' + entities_to_migrate[index]['collections'][index2]

            #Translate Credentials
            entities_to_migrate[index]['credentialID'] = src_session.tenant + ' - ' + entities_to_migrate[index]['credentialID']
            

                        
                        
        dst_entities.extend(entities_to_migrate)


        payload = {DATA_INDEX: dst_entities}

        #Add entity
        logger.info(f'Adding {MODULE} from \'{src_session.tenant}\'')
        dst_session.request('PUT', PUSH_ENDPOINT, json=payload)

    end_time = time.time()
    time_completed = round(end_time - start_time,3)
    logger.info(f'{MODULE}s migration finished - {time_completed} seconds')