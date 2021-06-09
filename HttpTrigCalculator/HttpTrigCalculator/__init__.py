import logging
import azure.functions as func

import sys

import json
import wolframalpha
import configparser

from azure.servicebus import ServiceBusClient, ServiceBusMessage

config = configparser.ConfigParser()
config.read('./config.ini')

if "service_bus_client" not in config:
    raise RuntimeError("config.ini file should have service_bus_client section")
if "CONNECTION_STR" not in config["service_bus_client"] or "QUEUE_NAME" not in config["service_bus_client"]:
    raise RuntimeError("config.ini file should have CONNECTION_STR and QUEUE_NAME to the service bus")

CONNECTION_STR = config["service_bus_client"]["CONNECTION_STR"]
QUEUE_NAME = config["service_bus_client"]["QUEUE_NAME"]


if "wolfram_api" not in config:
    raise RuntimeError("config.ini file should have wolfram_api section")
if "APP_ID" not in config["wolfram_api"]:
    raise RuntimeError("config.ini file should have APP_ID to the wolframalpha api")

APP_ID = config["wolfram_api"]["APP_ID"]



def some_calculator_magic(question: str) -> str:
    # Instance of wolf ram alpha 
    # client class
    client = wolframalpha.Client(APP_ID)
    
    # Stores the response from 
    # wolf ram alpha
    res = client.query(question)
    
    try:
        # Includes only text from the response
        answer = next(res.results).text    
        
    except StopIteration:
        answer = "It's too hard for us, try WolframAlpha instead."

    return answer


def send_single_message(sender, message):
    # create a Service Bus message
    message = ServiceBusMessage(message)
    # send the message to the queue
    sender.send_messages(message)
    print("Sent a single message")


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    
    try:
        req_body = req.get_json()
        
        question = req_body.get('question')
        # question = data["question"]
    except ValueError:
        return func.HttpResponse(
            "Bad input. Unable to read json body.",
            status_code=400
        )
    
    # get username if no than put None
    try:
        # name = data["username"]
        name = req_body.get('username')
    except KeyError:
        name = None

    answer = some_calculator_magic(question)    

    resault = {
        "username":name,
        "question":question,
        "response":answer
    }

    resault = json.dumps(resault)

    if sys.getsizeof(resault) <= 250*1000:
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)
        with servicebus_client:
            # get a Queue Sender object to send messages to the queue
            sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
            with sender:
                # send one message        
                send_single_message(sender, resault)
        
    return func.HttpResponse(
             json.dumps({"response":answer}),
             status_code=200
    )
