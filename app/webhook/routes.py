
from flask import Blueprint, json, jsonify,request
from datetime import datetime, timezone
from app.extensions import mongo
from flask_cors import CORS
from bson import json_util
webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')


# @webhook.route('/receiver', methods=["POST"])
# def receiver():
#     return {}, 200

# @webhook.route('/status', methods=["GET"])
# def status():
#     return json.jsonify({"status": "Server is running"}), 200

@webhook.route('/events', methods=['GET'])
def get_events():
    try:
        events = list(mongo.db.events.find().sort('timestamp', -1))
        # Convert ObjectId to string in each document
        for event in events:
            event['_id'] = str(event['_id'])

        # Return JSON response using json_util.dumps for proper serialization
        return jsonify(json.loads(json.dumps(events))), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def format_timestamp(timestamp):
    return timestamp.strftime("%d %B %Y - %I:%M %p UTC")

@webhook.route('/receiver', methods=['POST'])
def receiver():
    data = request.json

    if 'zen' in data:
        return jsonify({'message': 'Ping received'})

    event_type = request.headers.get('X-GitHub-Event')
    payload = {}
    current_time = datetime.now(timezone.utc)

    if event_type == 'push':
        payload = {
            'author': data['pusher']['name'],
            'action': 'pushed',
            'to_branch': data['ref'].split('/')[-1],
            'timestamp': format_timestamp(current_time)
        }
    # elif event_type == 'pull_request':
    #     payload = {
    #         'author': data['pull_request']['user']['login'],
    #         'action': 'submitted a pull request',
    #         'from_branch': data['pull_request']['head']['ref'],
    #         'to_branch': data['pull_request']['base']['ref'],
    #         'timestamp': format_timestamp(current_time)
    #     }
    #     print(payload)
    elif event_type == 'pull_request':
        action = data['action']
        if action == 'opened':
            payload = {
                'author': data['pull_request']['user']['login'],
                'action': 'submitted a pull request',
                'from_branch': data['pull_request']['head']['ref'],
                'to_branch': data['pull_request']['base']['ref'],
                'timestamp': format_timestamp(current_time)
            }
        elif action == 'closed' and data['pull_request']['merged']:
            payload = {
                'author': data['pull_request']['user']['login'],
                'action': f'merged branch {data["pull_request"]["head"]["ref"]} to {data["pull_request"]["base"]["ref"]} on {format_timestamp(current_time)}',
                'from_branch': data['pull_request']['head']['ref'],
                'to_branch': data['pull_request']['base']['ref'],
                'timestamp': format_timestamp(current_time)
            }
    elif event_type == 'pull_request_review' and data['review']['state'] == 'approved':
        payload = {
            'author': data['review']['user']['login'],
            'action': 'merged',
            'from_branch': data['pull_request']['head']['ref'],
            'to_branch': data['pull_request']['base']['ref'],
            'timestamp': format_timestamp(current_time)
        }

    # if payload:
    #     mongo.db.events.insert_one(payload)

    # return jsonify({'message': 'Event received'})
    if payload:
        existing_event = mongo.db.events.find_one(payload)
        if not existing_event:
            mongo.db.events.insert_one(payload)

@webhook.route('/status', methods=['GET'])
# def status():
#     return jsonify({"status": "Server is running"}), 200
def status():
    try:
        mongo.db.command('ping')
        return jsonify({"status": "MongoDB connected successfully"}), 200
    except Exception as e:
        return jsonify({"status": "MongoDB connection failed", "error": str(e)}), 500
