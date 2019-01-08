import base64
import json
import os
import requests

api = 'https://api.ciraas.io'

commands = {
    '0603298d-b1d3-4e70-bf19-21f6e8a89536': {
        "a": {"task_id":"a", "waypoint": {'x': -4, 'y': 4}},
        "b": {"task_id":"b", "waypoint": {'x': -4, 'y': 1}},
        "c": {"task_id":"c", "waypoint": {'x': -1, 'y': 1}},
 	    "d": {"task_id":"d", "waypoint": {'x': -1, 'y': 4}}
    },
    '64da0b1a-5994-4aae-b5cc-8556ffe898da': {
        "a": {"task_id":"a", "waypoint": {'x': 3, 'y': 4}},
        "b": {"task_id":"b", "waypoint": {'x': 3, 'y': 1}},
        "c": {"task_id":"c", "waypoint": {'x': 6, 'y': 1}},
 	    "d": {"task_id":"d", "waypoint": {'x': 6, 'y': 4}}
    }
}

def dispatch_command(robotId, task):
    print('Dispatching', robotId, task)
    auth = requests.post(
        'https://api.ciraas.io/user/{}/{}/auth'.format(os.environ['accountid'],os.environ['username']),
        headers={'content-type':'application/json'},
        data=json.dumps({'password':os.environ['password']}))
    token = auth.json()

    result = requests.post(
        'https://api.ciraas.io/robot/{}/state/task_state'.format(robotId),
        headers={'content-type':'application/json','x-ciraas-api-key':token['apiKey'],'x-ciraas-token':token['token']},
        data=json.dumps({'state':task})
    )
    return result.status_code

def dispatch(event, context):
    records = map(lambda record: json.loads(base64.b64decode(record['kinesis']['data'])), event['Records'])
    for record in records:

        if record['messageType'] == 'partial_state_update':
             print(record)

        if record['messageType'] == 'partial_state_update' and record['direction'] == 'uplink' and 'task_state' in record['payload'].keys():

            if record['robotId'] in commands.keys():

                task_state = record['payload']['task_state']

                if 'status' in task_state.keys() and 'task_id' in task_state.keys() and task_state['status'] == 'completed':
                    next_task = ''
                    if task_state['task_id'] == 'a':
                        next_task = 'b'
                    elif task_state['task_id'] == 'b':
                        next_task = 'c'
                    elif task_state['task_id'] == 'c':
                        next_task = 'd'
                    else:
                        next_task = 'a'
                    dispatch_command(record['robotId'],commands[record['robotId']][next_task])

                elif 'call_for_task' in task_state.keys() and task_state['call_for_task'] == True:
                    print('Dispatching default task.')
                    dispatch_command(record['robotId'],commands[record['robotId']]['a'])

    return 'successfully processed'
