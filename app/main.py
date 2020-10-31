from flask import Flask, abort, request, url_for, Blueprint
from flask_restx import Resource, Api, fields
from flask_cors import CORS
from .utils.query import getTwitterInfo

app = Flask(__name__)
cors = CORS(app)

blueprint = Blueprint("api", __name__, url_prefix="/api")

api = Api(
    blueprint,
    version="0.1.0",
    title="Twitter Dashboard API",
    doc="/docs"
)

app.register_blueprint(blueprint)

GET_TWITTER_INFO = api.model("UserInfo", {"username": fields.String})

# documentation for swagger UI
ns_analytics = api.namespace(
    "analytics", description="Gets the user's dashboard analytics"
)

@ns_analytics.route("")
class GetUserAnalytics(Resource):
    """
    For now we can just return some junk data
    """

    @api.param(
        "Username",
        description="The username of the twitter account you would like to get analytics for.",
        type="string",
    )
    @api.marshal_with(GET_TWITTER_INFO, mask=None)

    def get(self):
        # user's screen name
        name = getTwitterInfo(request.args.get("Username"))
        return {"username": name}