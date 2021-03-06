import os
import uuid

import flask

import bus
import http_response as http
import queries
import handlers
import commands


class Server(flask.Flask):
    def __init__(self, import_name, repository=None):
        self.bus = None
        self.query_dispatcher = None

        self.repository = repository

        root_dir = os.path.dirname(__file__)
        super().__init__(import_name,
                         static_folder=os.path.join(root_dir, 'client', 'static'),
                         template_folder=os.path.join(root_dir, 'client'))

    def configure_handlers(self):
        self.bus = bus.Bus()
        self.bus.register(commands.CreateRangeVoteCommand, handlers.CreateRangeVoteHandler(self.repository))
        self.bus.register(commands.UpdateRangeVoteCommand, handlers.UpdateRangeVoteHandler(self.repository))
        self.bus.register(commands.CreateVoteCommand, handlers.CreateVoteHandler(self.repository))

        self.query_dispatcher = bus.QueryDispatcher()
        self.query_dispatcher.register(queries.GetRangeVoteQuery, handlers.GetRangeVoteHandler(self.repository))
        self.query_dispatcher.register(queries.GetRangeVotesQuery, handlers.GetRangeVotesHandler(self.repository))
        self.query_dispatcher.register(queries.GetRangeVoteResultsQuery, handlers.GetRangeVoteResultsHandler(self.repository))


app = Server(__name__)


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/rangevotes')
def get_rangevotes():
    query = queries.GetRangeVotesQuery()
    rangevotes = app.query_dispatcher.execute(query)
    if rangevotes:
        return http.jsonify(rangevotes)
    return http.jsonify([])


@app.route('/rangevotes', methods=['POST'])
def create_rangevote():
    if commands.RangeVoteCommandValidator(flask.request.json).is_valid():
        command = commands.CreateRangeVoteCommand(uuid.uuid4(), flask.request.json['question'], flask.request.json['choices'])
        result = app.bus.execute(command)
        if result.ok:
            rangevote_id = str(command.uuid)
            return http.jsonify({'id': rangevote_id}, 201, {'Location': '/rangevotes/{0}'.format(rangevote_id)})
    return http.bad_request()


@app.route('/rangevotes/<path:rangevote_id>')
def get_rangevote(rangevote_id):
    query = queries.GetRangeVoteQuery(rangevote_id)
    rangevote = app.query_dispatcher.execute(query)
    if rangevote:
        return http.jsonify(rangevote)
    return http.not_found()


@app.route('/rangevotes/<path:rangevote_id>', methods=['PUT'])
def update_rangevote(rangevote_id):
    if commands.RangeVoteCommandValidator(flask.request.json).is_valid():
        command = commands.UpdateRangeVoteCommand(rangevote_id, flask.request.json['question'], flask.request.json['choices'],
                                                  flask.request.json['votes'])
        result = app.bus.execute(command)
        if result.ok:
            return http.jsonify()
    return http.bad_request()


@app.route('/rangevotes/<path:rangevote_id>/votes', methods=['POST'])
def create_vote(rangevote_id):
    if commands.VoteCommandValidator(flask.request.json).is_valid():
        command = commands.CreateVoteCommand(rangevote_id, flask.request.json['elector'], flask.request.json['opinions'])
        result = app.bus.execute(command)
        if result.ok:
            return http.jsonify({'id': rangevote_id}, 201, {'Location': '/rangevotes/{0}'.format(rangevote_id)})
    return http.bad_request()


@app.route('/rangevotes/<path:rangevote_id>/results')
def get_rangevote_results(rangevote_id):
    query = queries.GetRangeVoteResultsQuery(rangevote_id)
    results = app.query_dispatcher.execute(query)
    if results:
        return http.jsonify(results)
    return http.bad_request()
