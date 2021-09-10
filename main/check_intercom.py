from .models import Conversation
from django.utils.timezone import make_aware
import requests
import json
import os
import datetime

IntercomConversationUrl = 'https://api.intercom.io/conversations/'
IntercomContactsUrl = 'https://api.intercom.io/contacts/'
AccessToken = os.environ.get('AccessToken')
headers = {
    'Authorization': 'Bearer ' + AccessToken,
    'Accept': 'application/json'
}


def get_open_conversations():
    conversation_ids = get_conversations_with_no_email()
    for conversation_id in conversation_ids:
        r = requests.get(IntercomConversationUrl + str(conversation_id), headers=headers)
        conversation_json = json.loads(r.text)
        intercom_user_id = conversation_json['contacts']['contacts'][0]['id']
        contact = requests.get(IntercomContactsUrl + str(intercom_user_id), headers=headers)
        contact_json = json.loads(contact.text)
        intercom_user_email = contact_json['email']

        if intercom_user_email != '':
            print('Email is not empty for ' + str(intercom_user_id))
            print('Updating ' + intercom_user_email)
            update_conversation_in_database(conversation_id, intercom_user_email)
        else:
            print('No email found to update')


def get_conversations_with_no_email():
    conversations = Conversation.objects.filter(intercom_user_email='')
    conversation_ids = []
    for conversation in conversations:
        conversation_ids.append(conversation.conversation_id)
    return conversation_ids


def get_conversation_ids(conversation_json):
    conversation_ids = []
    conversations = conversation_json['conversations']

    for conversation in conversations:
        current_id = conversation['id']
        conversation_ids.append(current_id)
    return conversation_ids


def update_conversation_in_database(conversation_id, intercom_user_email):
    conversation = Conversation.objects.get(conversation_id=conversation_id)
    current_time = make_aware(datetime.datetime.now())
    closed_time = conversation.conversation_closed_at
    check_if_closed_within_a_week = (current_time - closed_time).days < 7
    if check_if_closed_within_a_week:
        conversation.conversation_impacted_sale = True
        conversation.intercom_user_email = intercom_user_email
        conversation.save()
        print('Saved email in database and updated conversation to show impact on sale')
    else:
        conversation.intercom_user_email = intercom_user_email
        conversation.save()
        print('Saved email in database')