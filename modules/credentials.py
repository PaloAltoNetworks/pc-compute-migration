import time
from tqdm import tqdm

def create_name(single_mode, session_name, data_name):
    if single_mode:
        return data_name
    else:
        session_name + ' - ' + data_name

def migrate(dst_session, src_session_list, options, single_mode, logger):
    # logger.warning('Credentials migration not implemented')

    MODULE = 'Credential'
    NAME_INDEX = '_id'
    PULL_ENDPOINT = '/api/v1/credentials?cloud=false'
    PUSH_ENDPOINT = '/api/v1/credentials'
    DATA_INDEX = ''
    DATA_INDEX2 = ''
    skip = False
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
                new_name = create_name(single_mode,src_session.tenant, ent.get(NAME_INDEX,''))
                
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
            new_name = create_name(single_mode, src_session.tenant, ent_payload.get(NAME_INDEX,''))
            if entities_to_migrate[index].get(NAME_INDEX,''):
                entities_to_migrate[index][NAME_INDEX] = new_name

            payload = {}

            #TYPE =apiToken========================================================================
            if entities_to_migrate[index]['type'] == 'apiToken':
                payload = {
                    "secret": {
                        "encrypted": "",
                        "plain": "x"
                    },
                    "serviceAccount": {},
                    "description": "",
                    "skipVerify": False,
                    "_id": "MIGRATE MEEE - TOKEN",
                    "type": "apiToken"
                }
                payload['description'] = entities_to_migrate[index].get('description', '')
                payload['_id'] = entities_to_migrate[index]['_id']
            
            #TYPE = basic =========================================================================
            elif entities_to_migrate[index]['type'] == 'basic':
                payload = {
                    "secret": {
                        "encrypted": "",
                        "plain": "x"
                    },
                    "serviceAccount": {},
                    "description": "",
                    "skipVerify": False,
                    "type": "basic",
                    "_id": "MIGRATE ME - Basic",
                    "accountID": "asdasd"
                }
                payload['description'] = entities_to_migrate[index].get('description', '')
                payload['accountID'] = entities_to_migrate[index]['accountID']
                payload['_id'] = entities_to_migrate[index]['_id']

            #TYPE = dtr ===========================================================================
            elif entities_to_migrate[index]['type'] == 'dtr':
                payload = {
                    "secret": {
                        "plain": "x",
                        "encrypted": ""
                    },
                    "serviceAccount": {},
                    "apiToken": {
                        "encrypted": "",
                        "plain": "x"
                    },
                    "description": "",
                    "skipVerify": False,
                    "_id": "MIGRATE ME - DTR",
                    "type": "dtr",
                    "accountID": "x"
                }
                payload['description'] = entities_to_migrate[index].get('description', '')
                payload['accountID'] = entities_to_migrate[index]['accountID']
                payload['_id'] = entities_to_migrate[index]['_id']
            
            #TYPE = githubEnterpriseToken =========================================================
            elif entities_to_migrate[index]['type'] == 'githubEnterpriseToken':
                payload = {
                    "caCert": None,
                    "serviceAccount": {},
                    "apiToken": {
                        "encrypted": "",
                        "plain": "x"
                    },
                    "description": "",
                    "url": "https://lasdjflasjfasldkasdflkfljlasdjfjasfasdjlasdfjasdfjlj.org",
                    "skipVerify": False,
                    "_id": "MIGRATRE ME - GITHUB ENTERPRISE SERCER ACCESS TOKEN",
                    "type": "githubEnterpriseToken"
                }
                payload['caCert'] = entities_to_migrate[index].get('caCert', None)
                payload['description'] = entities_to_migrate[index].get('description', '')
                payload['url'] = entities_to_migrate[index].get('url', '')
                payload['skipVerify'] = entities_to_migrate[index].get('skipVerify', False)
                payload['_id'] = entities_to_migrate[index]['_id']
            
            #TYPE = githubToken ===================================================================
            elif entities_to_migrate[index]['type'] == 'githubToken':
                payload = {
                    "serviceAccount": {},
                    "apiToken": {
                        "encrypted": "",
                        "plain": "x"
                    },
                    "description": "",
                    "skipVerify": False,
                    "_id": "MIGRATE ME - Github Cloud Access Token",
                    "type": "githubToken"
                }
                payload['description'] = entities_to_migrate[index].get('description', '')
                payload['_id'] = entities_to_migrate[index]['_id']

            #TYPE = 
            elif entities_to_migrate[index]['type'] == 'ibmCloud':
                payload = {
                    "secret": {
                        "encrypted": "",
                        "plain": "x"
                    },
                    "serviceAccount": {},
                    "description": "",
                    "skipVerify": False,
                    "_id": "MIGRATE ME - IBM",
                    "type": "ibmCloud",
                    "accountGUID": "sdfasdf"
                }
                payload['description'] = entities_to_migrate[index].get('description', '')
                payload['_id'] = entities_to_migrate[index]['_id']
                payload['accountGUID'] = entities_to_migrate[index]['accountGUID']

            elif entities_to_migrate[index]['type'] == 'kubeconfig':
                payload = {
                    "secret": {
                        "plain": "apiVersion: v1",
                        "encrypted": ""
                    },
                    "serviceAccount": {},
                    "description": "",
                    "skipVerify": False,
                    "_id": "MIGRATE ME - Kube Config",
                    "type": "kubeconfig"
                }
                payload['description'] = entities_to_migrate[index].get('description', '')
                payload['_id'] = entities_to_migrate[index]['_id']

            elif entities_to_migrate[index]['type'] == 'aws':
                payload = {
                    "caCert": "",
                    "secret": {
                        "encrypted": "",
                        "plain": "x"
                    },
                    "apiToken": {
                        "encrypted": "",
                        "plain": ""
                    },
                    "description": "",
                    "skipVerify": False,
                    "accountID": "a_key_id",
                    "useAWSRole": False,
                    "type": "aws",
                    "_id": "blahh",
                    "accountName": "test emtpy aws account",
                    "useSTSRegionalEndpoint": False
                }

                payload['description'] = entities_to_migrate[index].get('description', '')
                payload['_id'] = entities_to_migrate[index]['_id']
                payload['accountName'] = entities_to_migrate[index]['accountName']
                payload['useAWSRole'] = entities_to_migrate[index]['useAWSRole']

            elif entities_to_migrate[index]['type'] == 'azure':
                payload = {
                    "caCert": "",
                    "secret": {
                        "encrypted": "",
                        "plain": "{\"secret\":\"x\"}"
                    },
                    "apiToken": {
                        "encrypted": "",
                        "plain": ""
                    },
                    "description": "",
                    "skipVerify": False,
                    "accountID": "",
                    "useAWSRole": False,
                    "type": "azure",
                    "_id": "",
                    "accountName": "s",
                    "useSTSRegionalEndpoint": False
                }
                payload['description'] = entities_to_migrate[index].get('description', '')
                payload['_id'] = entities_to_migrate[index]['_id']
                payload['accountName'] = entities_to_migrate[index]['accountName']
            
            # elif entities_to_migrate[index]['type'] == 'certificate':

            else:
                print("ttype:", entities_to_migrate[index]['type'])
                continue
                
            

            #Add entity
            logger.info(f'Adding {MODULE} from \'{src_session.tenant}\'')
            dst_session.request('POST', PUSH_ENDPOINT, json=payload)

    end_time = time.time()
    time_completed = round(end_time - start_time,3)
    logger.info(f'{MODULE}s migration finished - {time_completed} seconds')