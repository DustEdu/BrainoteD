import flask

from main import app
import routes
import flask_login


def validated_id(value: int | None, param_name: str) -> int | str:
    if not value:
        return f"Error: Methods GET and DELETE require the {param_name} parameter."

    try: value = int(value)
    except ValueError:
        return f"Error: The {param_name} parameter must be a number."
    return value


@app.route("/")
def index(): return "Tf you wanted to see here bro? Want me to drop database?"


@app.route('/register/')
def register_route(): routes.register()


@app.route('/login/')
def login_route(): routes.login()


@app.route('/logout/')
@flask_login.login_required
def logout_route(): routes.logout()


@app.route("/get_users/")
def users_route(): routes.get_users()


@app.route("/user/<user_id>", methods=["post", "get", "delete"])
def user_route(user_id=None):
    method = flask.request.method
    if method != "POST":    user_id = validated_id(user_id, "user_id")

    if   flask.request.method == "POST":   return routes.post_user()
    elif flask.request.method == "GET":    return routes.get_user(user_id)
    elif flask.request.method == "DELETE": return routes.delete_user(user_id)
    else:
        return f"Error: Unknown method. Allowed methods: {["post", "get", "delete"]}"


@app.route("/note/<note_id>", methods=["post", "get", "delete"])
def note_route(note_id):
    method = flask.request.method
    if method != "POST":    note_id = validated_id(note_id, "note_id")

    if   method == "POST":   return routes.post_note()
    elif method == "GET":    return routes.get_note(note_id)
    elif method == "DELETE": return routes.delete_note(note_id)
    else:
        return f"Error: Unknown method. Allowed methods: {["post", "get", "delete"]}"


@app.route("/item/<item_id>", methods=["post", "get", "delete", "put"])
def item_route(obj_id):
    method = flask.request.method
    obj_id = validated_id(obj_id,
                          "item_id" if method != "POST"
                          else "note_id")

    if   method == "POST":   return routes.post_item(obj_id)
    elif method == "GET":    return routes.get_item(obj_id)
    elif method == "DELETE": return routes.delete_item(obj_id)
    elif method == "PUT":
        content = str(flask.request.args.get("content"))
        if not content: return "Error: No content parameter given."
        return routes.put_item(obj_id, content)

    else:
        return f"Error: Unknown method. Allowed methods: {["post", "get", "delete", "put"]}"
