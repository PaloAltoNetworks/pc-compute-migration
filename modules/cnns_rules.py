import time
from tqdm import tqdm
import json
import os

    
def migrate(dst_session, src_session_list, options, logger):
    #NETWORKS MIGRATE FIRST - creation translation table
    MODULE = 'CNNS - Network Entities'
    PULL_ENDPOINT = '/api/v1/policies/firewall/network'
    PUSH_ENDPOINT = '/api/v1/policies/firewall/network'
    DATA_INDEX = 'networkEntities'
    NAME_INDEX = 'name'

    #Logic
    start_time = time.time()
    logger.info(f'Starting {MODULE}s migration')

    for src_session in tqdm(src_session_list, desc='Processing Consoles/Projects', leave=False, initial=1):
        #Compare entities------------------------------------------------------
        logger.debug(f'Comparing {MODULE}s from \'{src_session.tenant}\'')

        #Pull entities
        dst_res = dst_session.request('GET', PULL_ENDPOINT)
        dst_entities = dst_res.json().get(DATA_INDEX, [])
        dst_names = []

        dst_names = []
        if dst_entities:
            dst_names = [x[NAME_INDEX] for x in dst_entities]


        res = src_session.request('GET', PULL_ENDPOINT)
        src_entities = []

        src_entities = res.json().get(DATA_INDEX, [])
        
        #Highest Val
        high_id = 0
        for ent in dst_entities:
            curr_id = int(ent['_id'])
            if curr_id > high_id:
                high_id = curr_id
        high_id += 1


        id_maps = {}
        if os.path.exists(f'id_mappings/{DATA_INDEX}-{src_session.tenant}.json'):
            with open(f'id_mappings/{DATA_INDEX}-{src_session.tenant}.json', 'r') as infile:
                id_maps = json.load(infile)

        #Compare entities and combine, update IDs
        with open(f'id_mappings/{DATA_INDEX}-{src_session.tenant}.json', 'w') as outfile:
            entities_to_migrate = []
            if src_entities:
                for ent in src_entities:
                    new_name = src_session.tenant + ' - ' + ent[NAME_INDEX]
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
            new_name = src_session.tenant + ' - ' + ent_payload[NAME_INDEX]
            entities_to_migrate[index][NAME_INDEX] = new_name

            #Translate collection names
            if 'collections' in ent_payload:
                for index2, col in enumerate(entities_to_migrate[index]['collections']):
                    if entities_to_migrate[index]['collections'][index2]['system'] == False:
                        entities_to_migrate[index]['collections'][index2]['name'] = src_session.tenant + ' - ' + entities_to_migrate[index]['collections'][index2]['name']

            #Add entity
        payload = dst_res.json()
        payload_data = payload.get(DATA_INDEX, [])
        payload_data.extend(entities_to_migrate)
        payload.update({DATA_INDEX: payload_data})


        logger.info(f'Adding {MODULE} from \'{src_session.tenant}\'')
        dst_session.request('PUT', f'{PUSH_ENDPOINT}', json=payload)
        

    end_time = time.time()
    time_completed = round(end_time - start_time,3)
    logger.info(f'{MODULE}s migration finished - {time_completed} seconds')


#========================================================================================================================================================================================================

    # #Const
    MODULE = 'CNNS - Container Rule'
    PULL_ENDPOINT = '/api/v1/policies/firewall/network'
    PUSH_ENDPOINT = '/api/v1/policies/firewall/network'
    DATA_INDEX = 'containerRules'
    NAME_INDEX = 'name'

    #Logic
    start_time = time.time()
    logger.info(f'Starting {MODULE}s migration')

    for src_session in tqdm(src_session_list, desc='Processing Consoles/Projects', leave=False, initial=1):
        #Compare entities------------------------------------------------------
        logger.debug(f'Comparing {MODULE}s from \'{src_session.tenant}\'')

        #Pull entities
        dst_res = dst_session.request('GET', PULL_ENDPOINT)
        dst_entities = dst_res.json()[DATA_INDEX]
        dst_names = []

        dst_names = []
        if dst_entities:
            dst_names = [x[NAME_INDEX] for x in dst_entities]


        res = src_session.request('GET', PULL_ENDPOINT)
        src_entities = []

        src_entities = res.json()[DATA_INDEX]
        
        #Highest Val
        high_id = 0
        for ent in dst_entities:
            curr_id = int(ent['id'])
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
                    ent['id'] = high_id
                    high_id += 1
                    entities_to_migrate.append(ent)

        #Migrate entities------------------------------------------------------
        if entities_to_migrate:
            logger.debug(f'Migrating {MODULE}s')
        else:
            logger.debug(f'No {MODULE}s to migrate')
            continue

        id_maps = {}
        if os.path.exists(f'id_mappings/networkEntities-{src_session.tenant}.json'):
            with open(f'id_mappings/networkEntities-{src_session.tenant}.json', 'r') as infile:
                id_maps = json.load(infile)
        else:
            logger.error('No ID Map. Skipping account...')
            continue

        for index, ent_payload in tqdm(enumerate(entities_to_migrate), desc='Custom Rules Migration', leave=False):
            #Create custom name for entity
            new_name = src_session.tenant + ' - ' + ent_payload[NAME_INDEX]
            entities_to_migrate[index][NAME_INDEX] = new_name

            #Translate IDs using translation table
            curr_dst = str(entities_to_migrate[index]['dst'])
            entities_to_migrate[index]['dst'] = id_maps[curr_dst]
            curr_src = str(entities_to_migrate[index]['src'])
            entities_to_migrate[index]['src'] = id_maps[curr_src]

            #Add entity
        payload = dst_res.json()
        payload_data = payload[DATA_INDEX]
        payload_data.extend(entities_to_migrate)
        payload[DATA_INDEX] = payload_data


        logger.info(f'Adding {MODULE} from \'{src_session.tenant}\'')
        dst_session.request('PUT', f'{PUSH_ENDPOINT}', json=payload)
        

    end_time = time.time()
    time_completed = round(end_time - start_time,3)
    logger.info(f'{MODULE}s migration finished - {time_completed} seconds')


#========================================================================================================================================================================================================

# #Const
    MODULE = 'CNNS - Host Rule'
    PULL_ENDPOINT = '/api/v1/policies/firewall/network'
    PUSH_ENDPOINT = '/api/v1/policies/firewall/network'
    DATA_INDEX = 'hostRules'
    NAME_INDEX = 'name'

    #Logic
    start_time = time.time()
    logger.info(f'Starting {MODULE}s migration')

    for src_session in tqdm(src_session_list, desc='Processing Consoles/Projects', leave=False, initial=1):
        #Compare entities------------------------------------------------------
        logger.debug(f'Comparing {MODULE}s from \'{src_session.tenant}\'')

        #Pull entities
        dst_res = dst_session.request('GET', PULL_ENDPOINT)
        dst_entities = dst_res.json()[DATA_INDEX]
        dst_names = []

        dst_names = []
        if dst_entities:
            dst_names = [x[NAME_INDEX] for x in dst_entities]


        res = src_session.request('GET', PULL_ENDPOINT)
        src_entities = []

        src_entities = res.json()[DATA_INDEX]
        
        #Highest Val
        high_id = 0
        for ent in dst_entities:
            curr_id = int(ent['id'])
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
                    ent['id'] = high_id
                    high_id += 1
                    entities_to_migrate.append(ent)

        #Migrate entities------------------------------------------------------
        if entities_to_migrate:
            logger.debug(f'Migrating {MODULE}s')
        else:
            logger.debug(f'No {MODULE}s to migrate')
            continue

        id_maps = {}
        if os.path.exists(f'id_mappings/networkEntities-{src_session.tenant}.json'):
            with open(f'id_mappings/networkEntities-{src_session.tenant}.json', 'r') as infile:
                id_maps = json.load(infile)
        else:
            logger.error('No ID Map. Skipping account...')
            continue

        for index, ent_payload in tqdm(enumerate(entities_to_migrate), desc='Custom Rules Migration', leave=False):
            #Create custom name for entity
            new_name = src_session.tenant + ' - ' + ent_payload[NAME_INDEX]
            entities_to_migrate[index][NAME_INDEX] = new_name

            #Translate IDs using translation table
            curr_dst = str(entities_to_migrate[index]['dst'])
            entities_to_migrate[index]['dst'] = id_maps[curr_dst]
            curr_src = str(entities_to_migrate[index]['src'])
            entities_to_migrate[index]['src'] = id_maps[curr_src]

            #Add entity
        payload = dst_res.json()
        payload_data = payload[DATA_INDEX]
        payload_data.extend(entities_to_migrate)
        payload[DATA_INDEX] = payload_data


        logger.info(f'Adding {MODULE} from \'{src_session.tenant}\'')
        dst_session.request('PUT', f'{PUSH_ENDPOINT}', json=payload)
        

    end_time = time.time()
    time_completed = round(end_time - start_time,3)
    logger.info(f'{MODULE}s migration finished - {time_completed} seconds')