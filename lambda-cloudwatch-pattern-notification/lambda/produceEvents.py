import json
import logging

logger=logging.getLogger(__name__)

def lambda_handler(event, context):
    logger.setLevel(logging.DEBUG)
    logger.info("Sample INFO log")
    logger.error("Sample ERROR log")
    logger.critical("Sample CRITICAL log")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Srce Cde!')
    }
