import time
import logging as log

from flask import Flask, render_template, Blueprint, request, jsonify
from nichirin.retriever.solr import SolrRetriever

app = Flask(__name__)

# Define a blueprint (optional)
bp = Blueprint("app", __name__, static_folder="static", template_folder="templates")

solr = SolrRetriever()


@bp.route("/", methods=["GET"])
def home():
    return render_template("home.html")


@bp.route("/givencontext", methods=["POST"])
def data_handeler_route():
    st = time.time()
    result = {}
    data = request.get_json(force=True)
    result = {"input": data}
    errors = []
    story = data.get("story", None)
    if isinstance(story, str):
        story = story.strip()
        if not story:
            errors.append('"context" has to be an non empty string')
    else:
        errors.append('a text field named "context" is required in input json document')
    if errors:
        result["errors"] = errors
        return result, 400
    texts = [story][0]
    try:
        response = solr.get_response(texts, "wiki")
        # need to add core_name
        result["output"] = response
    except Exception as e:
        log.error(e, exc_info=True)
        errors.append(
            "Something went wrong with the given input. We couldnt process it."
        )
        result["errors"] = errors
        return jsonify(result), 500

    result["time"] = f"{time.time() - st:.3f}s"
    return jsonify(result)


def main():
    # Register the blueprint (optional)
    app.register_blueprint(bp)

    # Run the Flask app
    app.run(debug=True)


if __name__ == "__main__":
    main()
