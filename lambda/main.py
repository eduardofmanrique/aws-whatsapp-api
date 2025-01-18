import os
import json
import boto3

from whatsapp_api.resources.messages import Messages



def handler(event, context):

    try:
        ssm_client = boto3.client('ssm', region_name='sa-east-1')
        secrets = json.loads(ssm_client.get_parameter(Name="whatsapp_api_secrets")['Parameter']['Value'])
        whatsapp_api_token = secrets['WHATSAPP_API_TOKEN']
    except Exception as e:
        raise Exception(f'Registre manualmente as chaves nas variáveis de ambiente - {e}')

    try:
        # Parse SQS message body
        for record in event['Records']:
            message_body = json.loads(record['body'])

            # Extract details from the message
            resource_name = message_body.get("resource_name")
            resource_args = message_body.get("resource_args", {})
            resource_function = message_body.get("resource_function")
            resource_function_args = message_body.get("resource_function_args", {})

            # Dynamically create the resource object
            if resource_name == "messages":
                resource = Messages(token=whatsapp_api_token, **resource_args)
            else:
                raise Exception(f'Resource {resource_name} is not mapped')

            # Dynamically invoke the function
            if hasattr(resource, resource_function):
                func = getattr(resource, resource_function)
                response = func(**resource_function_args)
                print(f"Function executed successfully: {response}")
            else:
                raise Exception(f"Function {resource_function} not found on resource {resource_name}")

    except Exception as e:
        print(f"Error processing SQS message: {e}")
        raise

if __name__ == "__main__":
    pass

