import json

def export(session, module, endpoint, data_index, data_index2=''):
    #Const
    PULL_ENDPOINT = endpoint

    DATA_INDEX = data_index
    DATA_INDEX2 = data_index2

    #Pull entities
    res = session.request('GET', PULL_ENDPOINT)
    dst_entities = []

    if DATA_INDEX:
        if res.json():
            dst_entities = res.json().get(DATA_INDEX, [])

            if DATA_INDEX2:
                dst_entities = dst_entities.get(DATA_INDEX2, [])

    else:
        if res.json():
            dst_entities = res.json()

    with open(f'export_dumps/{module}_dump.json', 'w') as outfile:
        json.dump(dst_entities, outfile)
