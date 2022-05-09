import json
from logging.config import dictConfig

from flask import Flask, request

from data import data_to_solver_input
from input import check_input

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
app.app_context()


@app.route('/')
def serve():
    print("Request received")
    schedule_input = request.json
    print(schedule_input)
    check_input(schedule_input)
    cpu_routings, cpu_allocations = data_to_solver_input(schedule_input)

    response = app.response_class(
        response=json.dumps({
            "cpu_routing_rules": cpu_routings,
            "cpu_allocations": cpu_allocations,
            "gpu_routing_rules": {},
            "gpu_allocations": {},
        }),
        status=200,
        mimetype='application/json'
    )

    return response

app.run(host='0.0.0.0', port=5000, threaded=False, processes=10)
