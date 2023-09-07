import time
from tqdm import tqdm

def create_name(single_mode, session_name, data_name):
    if single_mode:
        return data_name
    else:
        session_name + ' - ' + data_name

def migrate(dst_session, src_session_list, options, single_mode, logger):
    #Const
    skip = False
    MODULE = 'Alert Profile'
    NAME_INDEX = 'name'
    PULL_ENDPOINT = '/api/v1/alert-profiles'
    PUSH_ENDPOINT = '/api/v1/alert-profiles'
    DATA_INDEX = ''
    DATA_INDEX2 = ''
    COLLECTION_DEPENDENCY = False
    TAG_DEPENDENCY = True
    skip_value = ''    

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
            logger.info(f'Migrating {MODULE}s')
        else:
            logger.info(f'No {MODULE}s to migrate')
            continue

        for index, ent_payload in enumerate(entities_to_migrate):
            #Create custom name for entity
            new_name = create_name(single_mode,src_session.tenant, ent_payload.get(NAME_INDEX,''))
            if entities_to_migrate[index].get(NAME_INDEX,''):
                entities_to_migrate[index][NAME_INDEX] = new_name
            
            if COLLECTION_DEPENDENCY == True:
                #Translate collection names
                for index2, col in enumerate(entities_to_migrate[index]['collections']):
                    if entities_to_migrate[index]['collections'][index2]['system'] == False:
                        entities_to_migrate[index]['collections'][index2]['name'] = create_name(single_mode,src_session.tenant,entities_to_migrate[index]['collections'][index2]['name'])
            
            if TAG_DEPENDENCY == True:
                #Translate tag name
                for index2, col in enumerate(entities_to_migrate[index].get('tags', [])):
                    entities_to_migrate[index]['tags'][index2]['name'] = create_name(single_mode, src_session.tenant, entities_to_migrate[index]['tags'][index2]['name'])

            #Translate Credentials
            #'cortex'
            if entities_to_migrate[index]['cortex']['credentialId']:
                curr = entities_to_migrate[index]['cortex']['credentialId']
                entities_to_migrate[index]['cortex']['credentialId'] = create_name(single_mode, src_session.tenant, curr)
            #'email'
            if entities_to_migrate[index]['email']['credentialId']:
                curr = entities_to_migrate[index]['email']['credentialId']
                entities_to_migrate[index]['email']['credentialId'] = create_name(single_mode, src_session.tenant, curr)
            #'gcpPubsub'
            if entities_to_migrate[index]['gcpPubsub']['credentialId']:
                curr = entities_to_migrate[index]['gcpPubsub']['credentialId']
                entities_to_migrate[index]['gcpPubsub']['credentialId'] = create_name(single_mode, src_session.tenant, curr)
            #'jira'
            if entities_to_migrate[index]['jira']['credentialId']:
                curr = entities_to_migrate[index]['jira']['credentialId']
                entities_to_migrate[index]['jira']['credentialId'] = create_name(single_mode, src_session.tenant, curr)
            #'securityAdvisor
            if entities_to_migrate[index]['securityAdvisor']['credentialID']: #WHY IS THIS DIFFERENT????
                curr = entities_to_migrate[index]['securityAdvisor']['credentialID']
                entities_to_migrate[index]['securityAdvisor']['credentialID'] = create_name(single_mode, src_session.tenant, curr)
            #'securityCenter'
            if entities_to_migrate[index]['securityCenter']['credentialId']:
                curr = entities_to_migrate[index]['securityCenter']['credentialId']
                entities_to_migrate[index]['securityCenter']['credentialId'] = create_name(single_mode, src_session.tenant, curr)
            #'securityHub'
            if entities_to_migrate[index]['securityHub']['credentialId']:
                curr = entities_to_migrate[index]['securityHub']['credentialId']
                entities_to_migrate[index]['securityHub']['credentialId'] = create_name(single_mode, src_session.tenant, curr)
            #'serviceNow'
            if entities_to_migrate[index]['serviceNow']['credentialID']: #WHY IS THIS DIFFERENT????
                curr = entities_to_migrate[index]['serviceNow']['credentialID']
                entities_to_migrate[index]['serviceNow']['credentialID'] = create_name(single_mode, src_session.tenant, curr)
            #'webhook'
            if entities_to_migrate[index]['webhook']['credentialId']:
                curr = entities_to_migrate[index]['webhook']['credentialId']
                entities_to_migrate[index]['webhook']['credentialId'] = create_name(single_mode, src_session.tenant, curr)

            #Translate  Policy Rules and remove unsupported policy type
            if "outOfBandAppFirewall" in entities_to_migrate[index]['policy']:
                entities_to_migrate[index]['policy'].pop("outOfBandAppFirewall")

            for plc_name in entities_to_migrate[index]['policy'].keys():
                if entities_to_migrate[index]['policy'][plc_name]['rules']:
                    for index3, rule_name in enumerate(entities_to_migrate[index]['policy'][plc_name]['rules']):
                        new_name = create_name(single_mode,src_session.tenant, rule_name)
                        entities_to_migrate[index]['policy'][plc_name]['rules'][index3] = new_name


            #Add entity
            name =entities_to_migrate[index]['name']
            logger.info(f'Adding {name} {MODULE} from \'{src_session.tenant}\'')
            dst_session.request('POST', PUSH_ENDPOINT, json=entities_to_migrate[index])

    end_time = time.time()
    time_completed = round(end_time - start_time,3)
    logger.info(f'{MODULE}s migration finished - {time_completed} seconds')