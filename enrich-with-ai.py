import json
import os
import pprint
import re
import sqlite3
import textwrap
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

from dao import fetching, executing
from event import Event

conn = sqlite3.connect('./data.sqlite3')
cursor = conn.cursor()

executing.maybe_create_marys_requests_table(cursor)

events = [Event(event) for event in fetching.all_events_without_marys_demands(cursor)]

def get_demands_from_mary(api_client, description, trying_again=False):
    
    messages = [
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

    if trying_again:
        messages.append({"role": "assistant", "content": "[]"})
        messages.append({"role": "user", "content": "This is not correct. Please try again."})

    completion = api_client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    try:
        return json.loads(completion.choices[0].message.content)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")


# client = OpenAI()
client = OpenAI(
  organization='org-BjVsQwktIBNg8a1NNOcS8Svs',
  project='proj_mhC0PhH66KlKKnyLVbEFFtew',
)

def ask_and_print(client, event: Event, trying_again=True):
    demands = get_demands_from_mary(client, event.description, trying_again)
    print(
        textwrap.fill(
            textwrap.dedent(
                f'''Description:                             

                    > {str.replace(event.description, ' .', '.')}

                    ({event.name})

                    ({event.category})
                    
                    '''
            ),
            width=150,
            initial_indent='',
            subsequent_indent='    ',
        )
    )
    
    pprint.pprint(demands)
    return demands

for event in events:
    while True:
        demands = ask_and_print(client, event, trying_again=True)
        answer = input("Do you agree with this answer? (Y/n/s/0,[...]): ").strip().lower()
        if answer == 'y':
            print("Cool! Let's save it, then.")
            if demands == None:
                demands = []
            for request in demands:
                executing.insert_marys_request(conn, event.id, request)
            break  # Exit the loop if the answer is 'Y'
        elif answer == 'n':
            print("Let's try another time...")

        # Expression like 0,2 or 1,2,3
        elif re.match(r'^\d[\d,]*$', answer):
            for index in answer.split(','):
                executing.insert_marys_request(conn, event.id, demands[int(index)])
            break
        elif answer == 's':
            print('Skipping this one.')
            break
        else:
            print("Invalid input, please enter 'Y' for yes or 'n' for no.")
    
    # exit()