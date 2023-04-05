import json
from logging.config import dictConfig

from flask import Flask, request

from core import data_to_solver_input, check_input
from core.solvers import *

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
    input = request.json
    print(input)
    check_input(input)

    solver = input.get("solver")
    solver_type = solver.get("type")
    solver_args = solver.get("args", {})
    solver = eval(solver_type)(**solver_args)
    solver.load_data(data_to_solver_input(input))
    solver.solve()
    x,c = solver.results()
    response = app.response_class(
        response=json.dumps({
            "cpu_routing_rules": x,
            "cpu_allocations": c,
            "gpu_routing_rules": {},
            "gpu_allocations": {},
        }),
        status=200,
        mimetype='application/json'
    )

    return response

app.run(host='0.0.0.0', port=5000, threaded=False, processes=10)
