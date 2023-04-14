from modules import generic_pull_put_migrate
import time
from tqdm import tqdm

def migrate(dst_session, src_session_list, options, logger):
    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'Access Rules - Docker', '/api/v1/policies/docker', 'name', 'rules', logger)

    generic_pull_put_migrate.g_migrate(dst_session, src_session_list, 'Access Rules - Admission', '/api/v1/policies/admission', 'name', 'rules', logger, skip='owner', skip_value='system', col_dep=False)


    #TODO
    #FIXME maybe but have to translate IDs from the src tenant to the DST tenant and that is not easy to do reliably. Would have to dump to file then read from that file. Map src_session_name - custom rule name TO rule ID since the IDs change during migration.
    # #Const
    # MODULE = 'Access Rules - Kubernetes'
    # PULL_ENDPOINT = '/api/v1/policies/kubernetes-audit'
    # PUSH_ENDPOINT = '/api/v1/policies/kubernetes-audit'
    # DATA_INDEX = 'customRulesIDs'

    # #Logic
    # start_time = time.time()
    # logger.info(f'Starting {MODULE}s migration')

    # for src_session in tqdm(src_session_list, desc='Processing Consoles/Projects', leave=False, initial=1):
    #     #Compare entities------------------------------------------------------
    #     logger.debug(f'Comparing {MODULE}s from \'{src_session.tenant}\'')

    #     #Pull entities
    #     dst_res = dst_session.request('GET', PULL_ENDPOINT)
    #     print(dst_res.json())
    #     dst_entities = []
    #     if dst_res.json():
    #         dst_entities = dst_res.json().get(DATA_INDEX,[])


    #     res = src_session.request('GET', PULL_ENDPOINT)
    #     src_entities = []
    #     print(res.json())
    #     if res.json():
    #         src_entities = res.json().get(DATA_INDEX,[])
        
    #     #Compare entities
    #     entities_to_migrate = []
    #     if src_entities:
    #         for ent in src_entities:
    #             if ent not in dst_entities:
    #                 entities_to_migrate.append(ent)

    #     #Migrate entities------------------------------------------------------
    #     if entities_to_migrate:
    #         logger.debug(f'Migrating {MODULE}s')
    #     else:
    #         logger.debug(f'No {MODULE}s to migrate')
    #         continue
        
    #     dst_entities.extend(entities_to_migrate)

    #     payload = dst_res.json()
    #     payload[DATA_INDEX] = dst_entities

    #     #Add entity
    #     logger.info(f'Adding {MODULE} from \'{src_session.tenant}\'')
    #     dst_session.request('PUT', PUSH_ENDPOINT, json=payload)

    # end_time = time.time()
    # time_completed = round(end_time - start_time,3)
    # logger.info(f'{MODULE}s migration finished - {time_completed} seconds')