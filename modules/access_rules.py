from modules import generic_pull_put_migrate
import time
from tqdm import tqdm

def migrate(dst_session, src_session_list, options, logger):
    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'Access Rules - Docker', '/api/v1/policies/docker', 'name', 'rules', logger)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'Access Rules - Admission', '/api/v1/policies/admission', 'name', 'rules', logger, skip='owner', skip_value='system', col_dep=False)

    #==================================================================================================================================================================================================================

    #Const
    MODULE = 'Access Rules - Kubernetes Audit Settings'
    PULL_ENDPOINT = '/api/v1/settings/kubernetes-audit'
    PUSH_ENDPOINT = '/api/v1/settings/kubernetes-audit'
    DATA_INDEX = 'specifications'

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
            dst_entities = dst_res.json().get(DATA_INDEX,[])


        res = src_session.request('GET', PULL_ENDPOINT)
        src_entities = []
        if res.json():
            src_entities = res.json().get(DATA_INDEX,[])
        
        #Compare entities
        entities_to_migrate = []
        if src_entities:
            for ent in src_entities:
                if src_session.tenant + ' - ' + ent['name'] not in [dst_ent['name'] for dst_ent in dst_entities]:
                    ent['name'] = src_session.tenant + ' - ' + ent['name']
                    entities_to_migrate.append(ent)

        #Migrate entities------------------------------------------------------
        if entities_to_migrate:
            logger.debug(f'Migrating {MODULE}s')
        else:
            logger.debug(f'No {MODULE}s to migrate')
            continue
        
        dst_entities.extend(entities_to_migrate)

        payload = dst_entities

        #Add entity
        logger.info(f'Adding {MODULE} from \'{src_session.tenant}\'')
        dst_session.request('POST', PUSH_ENDPOINT, json=payload)

    end_time = time.time()
    time_completed = round(end_time - start_time,3)
    logger.info(f'{MODULE}s migration finished - {time_completed} seconds')

    #==================================================================================================================================================================================================================

    #TODO
    #FIXME Migrates a rule successfully but does not show up in the list of kubernettes rule in the SaaS CWP tenant
    #Const
    MODULE = 'Access Rules - Kubernetes'
    PULL_ENDPOINT = '/api/v1/custom-rules'
    PUSH_ENDPOINT = PULL_ENDPOINT
    DATA_INDEX = 'customRulesIDs'
    TYPE = "kubernetes-audit"

    #Logic
    start_time = time.time()
    logger.info(f'Starting {MODULE}s migration')

    for src_session in tqdm(src_session_list, desc='Processing Consoles/Projects', leave=False, initial=1):
        #Compare entities------------------------------------------------------
        logger.debug(f'Comparing {MODULE}s from \'{src_session.tenant}\'')

        #Pull entities
        dst_res = dst_session.request('GET', PULL_ENDPOINT)
        dst_entities = []
        dst_entities_raw = []
        if dst_res.json():
            for el in dst_res.json():
                if el['type'] == TYPE and el['owner'] != "system":
                    dst_entities.append(el)
                dst_entities_raw.append(el)

        res = src_session.request('GET', PULL_ENDPOINT)
        src_entities = []
        if res.json():
            for el in res.json():
                if el['type'] == TYPE and el['owner'] != "system":
                    src_entities.append(el)

        #Highest Val
        high_id = 0
        for ent in dst_entities_raw:
            curr_id = int(ent['_id'])
            if curr_id > high_id:
                high_id = curr_id
        high_id += 1

        #Compare entities
        entities_to_migrate = []
        if src_entities:
            for ent in src_entities:
                if src_session.tenant + ' - ' + ent['name'] not in [dst_ent['name'] for dst_ent in dst_entities]:
                    ent['name'] = src_session.tenant + ' - ' + ent['name']
                    ent['_id'] = high_id
                    high_id +=1
                    entities_to_migrate.append(ent)

        #Migrate entities------------------------------------------------------
        if entities_to_migrate:
            logger.debug(f'Migrating {MODULE}s')
        else:
            logger.debug(f'No {MODULE}s to migrate')
            continue
        
        for payload in entities_to_migrate:
            #Add entity
            logger.info(f'Adding {MODULE} from \'{src_session.tenant}\'')
            dst_session.request('PUT', PUSH_ENDPOINT + "/" + str(payload['_id']), json=payload)

        #Update ID list of kuberenttes rules
        id_list = []
        for ent_1 in entities_to_migrate:
            if ent['type'] == "kubernetes-audit":
                id_list.append(int(ent_1['_id']))

        new_payload = {"_id":"kubernetesAudit","enabled":True,"customRulesIDs":id_list}
        logger.info(f'Updating {MODULE} from \'{src_session.tenant}\'')
        dst_session.request('PUT', "/api/v1/policies/kubernetes-audit", json=new_payload)

    end_time = time.time()
    time_completed = round(end_time - start_time,3)
    logger.info(f'{MODULE}s migration finished - {time_completed} seconds')