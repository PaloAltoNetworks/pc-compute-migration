import time
from tqdm import tqdm
def g_migrate(dst_session, src_session_list, module, endpoint, name_index, data_index, logger, col_dep=True, tag_dep=False, skip='', skip_value='', data_index2='', verb_overwrite='POST'):
    #Const
    MODULE = module
    NAME_INDEX = name_index
    PULL_ENDPOINT = endpoint
    PUSH_ENDPOINT = endpoint
    DATA_INDEX = data_index
    DATA_INDEX2 = data_index2
    COLLECTION_DEPENDENCY = col_dep
    TAG_DEPENDENCY = tag_dep

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
            new_name = src_session.tenant + ' - ' + ent_payload.get(NAME_INDEX,'')
            if entities_to_migrate[index].get(NAME_INDEX,''):
                entities_to_migrate[index][NAME_INDEX] = new_name
            
            if COLLECTION_DEPENDENCY == True:
                #Translate collection names
                for index2, col in enumerate(entities_to_migrate[index]['collections']):
                    if entities_to_migrate[index]['collections'][index2]['system'] == False:
                        entities_to_migrate[index]['collections'][index2]['name'] = src_session.tenant + ' - ' + entities_to_migrate[index]['collections'][index2]['name']
            
            if TAG_DEPENDENCY == True:
                #Translate tag name
                for index2, col in enumerate(entities_to_migrate[index].get('tags', [])):
                    entities_to_migrate[index]['tags'][index2]['name'] = src_session.tenant + ' - ' + entities_to_migrate[index]['tags'][index2]['name']

            #Add entity
            logger.info(f'Adding {MODULE} from \'{src_session.tenant}\'')
            dst_session.request(verb_overwrite, PUSH_ENDPOINT, json=entities_to_migrate[index], status_ignore=[409])

    end_time = time.time()
    time_completed = round(end_time - start_time,3)
    logger.info(f'{MODULE}s migration finished - {time_completed} seconds')