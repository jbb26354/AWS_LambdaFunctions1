import boto3
import json
import uuid
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info('Loading function')
dynamo = boto3.client('dynamodb')


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def create_new_item(request):
    item_id = str(uuid.uuid4())
    item = {
            'id': {"S": item_id},
            'quote': {"S": request['quote']},
            'movie': {"S": request['movie']},
    }
    logger.info("Creating Object: {}".format(item))
    
    result = dynamo.put_item(TableName="GCUPasteBin", Item=item)
    return {
            'id': item_id,
            'quote': request['quote'],
            'movie': request['movie'],
    }

def lambda_handler(event, context):
    logger.info("Received event: " + json.dumps(event, indent=2))

    operations = {
        'DELETE': lambda dynamo, x: dynamo.delete_item(**x),
        'GET': lambda dynamo, x: dynamo.scan(**x),
        'POST': create_new_item,
        'PUT': lambda dynamo, x: dynamo.update_item(**x),
    }

    operation = event['httpMethod']
    if operation == 'POST':
        return respond(None, create_new_item(json.loads(event['body'])))
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))

    #if operation in operations:
    #    payload = event['queryStringParameters'] if operation == 'GET' else json.loads(event['body'])
    #    return respond(None, operations[operation](dynamo, payload))

