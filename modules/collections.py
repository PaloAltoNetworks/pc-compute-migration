import time
from tqdm import tqdm
import json


def create_role(session, collection_name, rl_id):

    session.logger.debug(f'Adding Role for Collection: {collection_name}')
    payload = {
        "additionalAttributes": {
            "hasDefenderPermissions":False,
            "onlyAllowComputeAccess":False
        },
        "accountGroupIds": [
            "bdcfe2be-a232-41b8-b105-a502216ad3ad"
        ],
        "description": "",
        "name": f"Role For {collection_name}",
        "resourceListIds": [
            rl_id
        ],
        "codeRepositoryIds": [],
        "roleType": "Account Group Read Only"
    }

def collection_for_user(session, collection_name):
    session.logger.debug('Getting Collection Usage')
    url = f'/api/v1/collections/{collection_name}/usages'
    res = session.request('GET', url)
    
    
    if res.json():
        for el in res.json():
            if el['type'] == 'user':
                return True
        
    return False


REQUIRED_MEMBER_FIELDS = [
    "appIDs", "clusters", "codeRepos", "containers",
    "functions", "hosts", "images", "labels", "namespaces"
]

def validate_rl_payload(payload):
    errors = []

    if not isinstance(payload.get("name"), str) or not payload["name"].strip():
        errors.append("'name' must be a non-empty string")

    if "resourceListType" not in payload:
        errors.append("'resourceListType' is missing")

    members = payload.get("members")
    if not isinstance(members, list) or len(members) == 0:
        errors.append("'members' must be a non-empty list")
    else:
        member = members[0]
        for field in REQUIRED_MEMBER_FIELDS:
            val = member.get(field)
            if not isinstance(val, list):
                errors.append(f"members[0]['{field}'] must be a list, got {type(val).__name__}")
            elif len(val) == 0:
                errors.append(f"members[0]['{field}'] must not be empty")

    return errors


def create_rl(src_session, session, collection_data):
    name = collection_data['name']

    if collection_for_user(src_session, name):
        import json
        with open('collections.json', 'w') as outfile:
            json.dump(collection_data, outfile)


        def as_list(val):
            if isinstance(val, list):
                return val
            return [val]

        payload = {
            "description": "",
            "members": [
                {
                    "appIDs": as_list(collection_data.get('appIDs', "*")),
                    "clusters": as_list(collection_data.get('clusters', "*")),
                    "codeRepos": as_list(collection_data.get('codeRepos', "*")),
                    "containers": as_list(collection_data.get('containers', "*")),
                    "functions": as_list(collection_data.get('functions', "*")),
                    "hosts": as_list(collection_data.get('hosts', "*")),
                    "images": as_list(collection_data.get('images', "*")),
                    "labels": as_list(collection_data.get('labels', "*")),
                    "namespaces": as_list(collection_data.get('namespaces', "*"))
                }
            ],
            "name": name,
            "resourceListType": "COMPUTE_ACCESS_GROUP"
        }

        validation_errors = validate_rl_payload(payload)
        if validation_errors:
            session.logger.error(f'Invalid Resource List payload for "{name}": {validation_errors}')
            return

        res = session.request('POST', '/v1/resource_list', json=payload)


        if res.status_code == 200 or res.status_code == 201:
            rl_id = res.json()['id']
            create_role(session, name, rl_id)



def create_name(single_mode, session_name, data_name):
    if single_mode:
        return data_name
    else:
        session_name + ' - ' + data_name


def migrate(dst_session, src_session_list, options, single_mode, cspm_session, create_rl_for_collections, logger):
    #Const
    MODULE = 'Collection'
    NAME_INDEX = 'name'
    PULL_ENDPOINT = '/api/v1/collections'
    PUSH_ENDPOINT = '/api/v1/collections'

    #Logic
    start_time = time.time()
    logger.info(f'Starting {MODULE}s migration')

    for src_session in tqdm(src_session_list, desc='Processing Consoles/Projects', leave=False, initial=1):
        #Compare entities------------------------------------------------------
        logger.debug(f'Comparing {MODULE}s from \'{src_session.tenant}\'')

        #Pull entities
        res = dst_session.request('GET', PULL_ENDPOINT)
        dst_entities_names = [x[NAME_INDEX] for x in res.json()]
        res = src_session.request('GET', PULL_ENDPOINT)
        src_entities = res.json()
        
        #Compare entities
        entities_to_migrate = []
        for ent in src_entities:
            new_name = create_name(single_mode, src_session.tenant, ent[NAME_INDEX])
            if new_name not in dst_entities_names:
                entities_to_migrate.append(ent)

        #Migrate entities------------------------------------------------------
        if entities_to_migrate:
            logger.debug(f'Migrating {MODULE}s')
        else:
            logger.debug(f'No {MODULE}s to migrate')

        for ent_payload in tqdm(entities_to_migrate, desc=f'Adding {MODULE}s', leave=False, initial=1):
            #Skip system collections
            if ent_payload.get('system') == True:
                continue

            #Create custom name for entity
            new_name = create_name(single_mode, src_session.tenant, ent_payload[NAME_INDEX])
            ent_payload[NAME_INDEX] = new_name

            #Add entity
            logger.info(f'Adding {MODULE} from \'{src_session.tenant}\'')
            dst_session.request('POST', PUSH_ENDPOINT, json=ent_payload)

            

            if create_rl_for_collections:
                create_rl(src_session, cspm_session, ent_payload) 

    end_time = time.time()
    time_completed = round(end_time - start_time,3)
    logger.info(f'{MODULE}s migration finished - {time_completed} seconds')