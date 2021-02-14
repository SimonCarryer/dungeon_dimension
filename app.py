from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

import sys
from flask import Flask, jsonify, redirect, url_for, request, render_template
from flask_restplus import Resource, Api, reqparse
from encounters.encounter_api import EncounterSource
from flask.logging import default_handler
from collections import Counter
from werkzeug.exceptions import BadRequest
from flask_cors import CORS
from dungeons.dungeon_api import DungeonSource
from random import Random
import logging
import random
import uuid
import urllib
import json

app = Flask(__name__)
cors = CORS(app)

api = Api(app,
          version='0.1',
          title='Dungeon Dimension REST API',
          description='REST-ful API for dungeon dimension',
)

dungeon_parser = reqparse.RequestParser()
dungeon_parser.add_argument('level', type=int, required=True, help='Average level of party')
dungeon_parser.add_argument('terrain', type=str, required=False, help='Terrain type for dungeon setting.')
dungeon_parser.add_argument('dungeon_type', type=str, required=False, help='Base type of dungeon.')
dungeon_parser.add_argument('main_antagonist', type=str, required=False, help='Monster set of main dungeon antagonist.')
dungeon_parser.add_argument('guid', type=str, required=False, help='GUID to intialise random state')


@api.route('/dungeon')
class Dungeon(Resource):

    @api.doc(parser=dungeon_parser)
    def get(self):
        '''Returns JSON representation of a random dungeon'''
        args = dungeon_parser.parse_args()
        state = Random()
        app.logger.debug('Making a dungeon')
        d = DungeonSource(random_state=state)
        module = d.get_dungeon()
        return jsonify({'dungeon': module})
