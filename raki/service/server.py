import flask
import flask_restplus

app = flask.Flask(__name__)
blueprint = flask.Blueprint('api', __name__, url_prefix='/api')

api = flask_restplus.Api(blueprint, doc='/doc/')

relay_ns = api.namespace('relay', description='Relay operations')
relay_model = api.model('Relay', {
    'id': flask_restplus.fields.String(
        readOnly=True,
        description='The relay unique identifier',
    ),
    'state': flask_restplus.fields.String(
        readOnly=True,
        description='State of the relay',
    ),
})
command_model = api.model('Command', {
    'type': flask_restplus.fields.String(
        readOnly=True,
        description='Type of the command'
    ),
    'args': flask_restplus.fields.List(
        flask_restplus.fields.String(
            readOnly=True,
            description='Type of the command'
        )
    ),
})

relays_ns = api.namespace('relays', description='Relays operations')

app.register_blueprint(blueprint)


@relays_ns.route('/')
class Relays(flask_restplus.Resource):
    ''' Relays endpoint
    '''
    @relays_ns.doc('list relays')
    @relays_ns.marshal_list_with(relay_model)
    def get(self):
        return []


@relay_ns.route('/<string:id>')
@relay_ns.response(404, 'Relay not found')
@relay_ns.param('id', 'The relay identifier')
class Relay(flask_restplus.Resource):
    ''' Relay endpoint
    '''
    @relay_ns.doc('get relay')
    @relay_ns.marshal_with(relay_model)
    def get(self, id):
        return {}

    @relay_ns.doc('post command on relay')
    @relay_ns.expect(command_model)
    @relay_ns.marshal_with(relay_model)
    def post(self, id):
        return {}


@app.route("/")
def home():
    ''' This function just responds to the browser URL
        localhost:5000/
    :return: the rendered template "home.html"
    '''
    return flask.render_template("home.html")


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
