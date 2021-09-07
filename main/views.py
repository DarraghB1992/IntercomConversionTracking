import datetime
import json
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import make_aware
from .models import Conversation


# Create your views here.
def index(request):
    return render(request, 'checkout.html')


def submit_checkout(request):
    if request.method == 'POST':
        print(request.POST)
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        get_conversations_by_email(email)
        return render(request, 'complete.html', {'email': email, 'first_name': first_name, 'last_name': last_name})
    else:
        print(request)
        return render(request, 'checkout.html')


@csrf_exempt
def accept_webhook(request):
    if request.method == 'POST':
        json_data = request.body
        webhook_json = json.loads(json_data)
        if webhook_json['topic'] == 'conversation.admin.closed':
            print(webhook_json)
            check_if_conversation_exists(webhook_json)
            response = HttpResponse()
            response.status_code = 200
            return response
        else:
            response = HttpResponse()
            response.status_code = 200
            return response


def check_if_conversation_exists(conversation_json):
    conversation_id = conversation_json['data']['item']['id']
    if Conversation.objects.filter(conversation_id=conversation_id).exists():
        conversation_object = Conversation.objects.get(conversation_id=conversation_id)
        print('Updating, conversation_id already exists')
        update_database(conversation_json, conversation_object)
    else:
        print('Creating new conversation')
        conversation_object = Conversation()
        update_database(conversation_json, conversation_object)


def update_database(conversation_json, conversation_object):
    conversation = conversation_object
    conversation_data = conversation_json['data']['item']

    conversation.conversation_created_at = convert_unix_timestamp(conversation_data['created_at'])
    conversation.conversation_id = conversation_data['id']
    conversation.conversation_closed_at = convert_unix_timestamp(conversation_data['updated_at'])

    conversation.intercom_user_id = conversation_data['user']['id']
    conversation.intercom_user_name = conversation_data['user']['name']
    conversation.intercom_user_email = conversation_data['user']['email']

    conversation.teammate_id = conversation_data['assignee']['id']
    conversation.teammate_name = conversation_data['assignee']['name']
    conversation.teammate_email = conversation_data['assignee']['email']

    conversation.save()


def show_conversations(request):
    all_conversations = Conversation.objects.all().order_by('-conversation_impacted_sale')
    return render(request, 'conversations.html', {'conversations': all_conversations})


def convert_unix_timestamp(unix_timestamp):
    unix_time = int(unix_timestamp)
    human_readable_timestamp = datetime.datetime.utcfromtimestamp(unix_time)
    timezone_aware_timestamp = make_aware(human_readable_timestamp)
    return timezone_aware_timestamp


def get_conversations_by_email(email):
    email = email
    current_time = make_aware(datetime.datetime.now())
    if Conversation.objects.filter(intercom_user_email=email).exists():
        print('Email exists')
        conversations = Conversation.objects.filter(intercom_user_email=email)
        for conversation in conversations:
            closed_time = conversation.conversation_closed_at
            check_if_closed_within_a_week = (current_time - closed_time).days < 7
            if check_if_closed_within_a_week:
                conversation_id = conversation.conversation_id
                update_conversation_to_impact_sale(conversation_id)
                print('Closed within a week, updating')
            else:
                print('Older than a week')
    else:
        print('Email not found in database')


def update_conversation_to_impact_sale(conversation_id):
    conversation = Conversation.objects.get(conversation_id=conversation_id)
    conversation.conversation_impacted_sale = True
    conversation.save()
    print('Conversation Updated')
