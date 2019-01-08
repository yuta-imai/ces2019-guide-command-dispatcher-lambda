import json
import handler

with open('./test/test_data.json','r') as f:
    data = json.loads(f.read())
    handler.dispatch(data,{})