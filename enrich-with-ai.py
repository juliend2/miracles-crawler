import sqlite3
import pprint
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

from dao import fetching, executing
from event import Event

conn = sqlite3.connect('./data.sqlite3')
cursor = conn.cursor()

executing.maybe_create_marys_requests_table(cursor)

events = [Event(event) for event in fetching.all_events_without_marys_demands(cursor)]

def get_demands_from_mary(api_client, description, try_again=False):
    completion = api_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Please respond only in a valid JSON array containing the elements I'm asking for, and nothing else."},
            {
                "role": "user",
                "content": f'''
                For the following description, give an array of the things (as strings) that Mary explicitly demands to the interlocutor or to the world in general:

                    > {description}

                If no demand is found, return an empty array.

                A 'demand' can be in the form of a mission entrusted to the person to whom she speaks.
                '''
            }
        ]
    )

    # TODO:
    # WHEN we pass the param try_again = True, we add another element to the conversation, to insist for the system to
    # try again, and that we don't accept an empty array.
    
    try:
        return json.loads(completion.choices[0].message.content)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")


# client = OpenAI()
client = OpenAI(
  organization='org-BjVsQwktIBNg8a1NNOcS8Svs',
  project='proj_mhC0PhH66KlKKnyLVbEFFtew',
)

def ask_and_print(client, description):
    demands = get_demands_from_mary(client, description)
    print(
        f'''
        Description:
        > {description}'''
    )
    pprint.pprint(demands)
    return demands

for event in events:
    while True:
        demands = ask_and_print(client, event.description)
        answer = input("Do you agree with this answer? (Y/n): ").strip().lower()
        if answer == 'y':
            print("Cool! Let's save it, then.")
            for request in demands:
                executing.insert_marys_request(conn, event.id, request)
            break  # Exit the loop if the answer is 'Y'
        elif answer == 'n':
            print("Let's try another time...")
        else:
            print("Invalid input, please enter 'Y' for yes or 'n' for no.")
    
    # exit()