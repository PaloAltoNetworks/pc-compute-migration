import time
from tqdm import tqdm
import json


def create_name(single_mode, session_name, data_name):
    if single_mode:
        return data_name
    else:
        session_name + ' - ' + data_name

def g_migrate(dst_session, src_session_list, module, endpoint, name_index, data_index, single_mode, logger, col_dep=True, tag_dep=False, skip='', skip_value='', data_index2='', network_list_dep=False, translate_custom_rule_ids=False):
    #Const
    MODULE = module
    NAME_INDEX = name_index
    PULL_ENDPOINT = endpoint
    PUSH_ENDPOINT = endpoint
    DATA_INDEX = data_index
    DATA_INDEX2 = data_index2
    COLLECTION_DEPENDENCY = col_dep
    TAG_DEPENDENCY = tag_dep
    NETWORK_LIST_DEPENDENCY = network_list_dep


    dst_session.retries = 5

    #Logic
    start_time = time.time()
    logger.info(f'Starting {MODULE}s migration')
    
    dst_res = {}
    dst_rules_list ={}
    if translate_custom_rule_ids:
        dst_res = dst_session.request('GET','/api/v1/custom-rules')
        dst_rules_list = dst_res.json()

    for src_session in tqdm(src_session_list, desc='Processing Consoles/Projects', leave=False, initial=1):
        custom_rules_id_translation_matrix = {}

        if translate_custom_rule_ids:
            src_res = src_session.request('GET','/api/v1/custom-rules')
            src_rules_list = src_res.json()

            for dst_rule in dst_rules_list:
                for src_rule in src_rules_list:
                     #Gotta translate the name with the modifications made to where it was sourced from but the built ins will have the same name
                    if dst_rule['name'] == create_name(single_mode, src_session.tenant,src_rule['name']) or dst_rule['name'] == src_rule['name']:
                        custom_rules_id_translation_matrix.update({src_rule['_id']:dst_rule['_id']})
                        continue
        


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
                dst_entities = []

        else:
            if dst_res.json():
                dst_entities = dst_res.json()
                if dst_entities:
                    dst_names = [x.get(NAME_INDEX,'') for x in dst_entities]
                else:
                    dst_entities = []


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
                new_name = create_name(single_mode, src_session.tenant, ent.get(NAME_INDEX,''))
                
                if skip:
                    if ent[skip] != skip_value:
                        if new_name not in dst_names:
                            entities_to_migrate.append(ent)
                else:
                    if new_name not in dst_names:
                        entities_to_migrate.append(ent)

        #Migrate entities------------------------------------------------------
        if entities_to_migrate:
            logger.debug(f'Migrating {MODULE}s')
        else:
            logger.debug(f'No {MODULE}s to migrate')
            continue
        
        failed_indexes = []

        for index, ent_payload in enumerate(entities_to_migrate):
            #Create custom name for entity
            new_name = create_name(single_mode, src_session.tenant, ent_payload.get(NAME_INDEX,''))
            if entities_to_migrate[index].get(NAME_INDEX,''):
                entities_to_migrate[index][NAME_INDEX] = new_name
            
            if COLLECTION_DEPENDENCY == True:
                #Translate collection names
                for index2, col in enumerate(entities_to_migrate[index]['collections']):
                    if entities_to_migrate[index]['collections'][index2]['system'] == False:
                        entities_to_migrate[index]['collections'][index2]['name'] = create_name(single_mode,src_session.tenant, entities_to_migrate[index]['collections'][index2]['name'])
            
            if TAG_DEPENDENCY == True:
                #Translate tag name
                for index2, col in enumerate(entities_to_migrate[index].get('tags', [])):
                    entities_to_migrate[index]['tags'][index2]['name'] = create_name(single_mode, src_session.tenant, entities_to_migrate[index]['tags'][index2]['name'])

            if NETWORK_LIST_DEPENDENCY == True:
                for index2, col in enumerate(entities_to_migrate[index].get('applicationsSpec', [])):
                    for index3, col in enumerate(entities_to_migrate[index].get('applicationsSpec', [])[index2].get('networkControls', {}).get('subnets', {}).get('allow',[])):
                        val = entities_to_migrate[index]['applicationsSpec'][index2]['networkControls']['subnets']['allow'][index3]
                        entities_to_migrate[index].get('applicationsSpec', [])[index2]['networkControls']['subnets']['allow'][index3] = create_name(single_mode, src_session.tenant, val)

                    for index3, col in enumerate(entities_to_migrate[index].get('applicationsSpec', [])[index2].get('networkControls', {}).get('subnets', {}).get('deny',[])):
                        val = entities_to_migrate[index].get('applicationsSpec', [])[index2]['networkControls']['subnets']['deny'][index3]
                        entities_to_migrate[index].get('applicationsSpec', [])[index2]['networkControls']['subnets']['deny'][index3] = create_name(single_mode, src_session.tenant, val)

            if custom_rules_id_translation_matrix:
                if 'customRules' in entities_to_migrate[index]:
                    for b in range(len(entities_to_migrate[index]['customRules'])):
                        try:
                            new_id = custom_rules_id_translation_matrix[entities_to_migrate[index]['customRules'][b]['_id']]
                            entities_to_migrate[index]['customRules'][b]['_id'] = new_id
                        except:
                            failed_indexes.append(index)
        
        #Remove rules that fail
        if custom_rules_id_translation_matrix:
            for index in failed_indexes:
                del entities_to_migrate[index]


        dst_entities.extend(entities_to_migrate)

        payload = {}
        if DATA_INDEX:
            if DATA_INDEX2:
                payload = dst_res.json()
                if not payload:
                    payload = {}
                payload[DATA_INDEX][DATA_INDEX2] = dst_entities
            else:
                payload = dst_res.json()
                if not payload:
                    payload = {}
                payload[DATA_INDEX] = dst_entities
        else:
            payload = dst_entities

        #Add entity
        logger.info(f'Adding {MODULE} from \'{src_session.tenant}\'')
        dst_session.request('PUT', PUSH_ENDPOINT, json=payload)

    end_time = time.time()
    time_completed = round(end_time - start_time,3)
    logger.info(f'{MODULE}s migration finished - {time_completed} seconds')