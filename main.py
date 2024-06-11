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

# Mapping of solver types to their respective classes
solver_classes = {
    'NeptuneData': NeptuneData,

}


@app.route('/')
def serve():
    print("Request received")
    input = request.json
    print(input)
    check_input(input)

    solver_info = input.get("solver", {'type': 'NeptuneMinDelayAndUtilization'})
    print("Solver: ", solver_info)
    solver_type = solver_info.get("type")
    print("Solver type: ", solver_type)
    solver_args = solver_info.get("args", {})
    print("Solver args: ", solver_args)
    with_db = input.get("with_db", True)

    # Fetch the solver class from the mapping
    SolverClass = solver_classes.get(solver_type)
    if SolverClass is None:
        raise ValueError(f"Unknown solver type: {solver_type}")

    # Instantiate the solver
    solver = SolverClass(**solver_args)
    print(solver)

    '''
    solver = eval(solver_type)(**solver_args)
    print(solver)
    '''
    solver.load_data(data_to_solver_input(input, with_db=with_db, workload_coeff=input.get("workload_coeff", 1)))
    status = solver.solve()
    # x, c = solver.results()
    solver.results()
    # score = solver.score()
    # print("INTER", score)

    # Check solver status
    if status == pywraplp.Solver.OPTIMAL:
        print('Solution is optimal.')
    elif status == pywraplp.Solver.FEASIBLE:
        print('Solution is feasible.')
    else:
        print('No solution found.')

    # Extract solver.data.nodes and solver.data.node_delay_matrix
    nodes = list(range(len(solver.data.nodes)))
    node_delay_matrix = solver.data.node_delay_matrix.tolist()

    q_ijt_values = {}
    for i in range(len(solver.data.nodes)):
        for j in range(len(solver.data.nodes)):
            for t in range(len(solver.data.tables)):
                q_ijt_values[f"q[{i}][{j}][{t}]"] = solver.q[i, j, t].solution_value()
    c_fi_values = {}
    for i in range(len(solver.data.nodes)):
        for f in range(len(solver.data.functions)):
            c_fi_values[f"c[{f}][{i}]"] = solver.c[f, i].solution_value()
    mu_jt_values = {}
    for j in range(len(solver.data.nodes)):
        for t in range(len(solver.data.tables)):
            mu_jt_values[f"mu[{j}][{t}]"] = solver.mu[j, t].solution_value()

    sigma_jt_values = {}
    for j in range(len(solver.data.nodes)):
        for t in range(len(solver.data.tables)):
            sigma_jt_values[f"sigma[{j}][{t}]"] = solver.sigma[j, t].solution_value()

    y_ftij_values = {}
    for i in range(len(solver.data.nodes)):
        for j in range(len(solver.data.nodes)):
            for f in range(len(solver.data.functions)):
                for t in range(len(solver.data.tables)):
                    y_ftij_values[f"y[{f}][{t}][{i}][{j}]"] = solver.y[f, t, i, j].solution_value()

    response = app.response_class(
        response=json.dumps({
            # "cpu_routing_rules": x,
            # "cpu_allocations": c,
            "gpu_routing_rules": {},
            "gpu_allocations": {},
            "nodes": nodes,
            "node_delay_matrix": node_delay_matrix,
            "q_ijt_values": q_ijt_values,
            "c_fi_values": c_fi_values,
            "mu_jt_values": mu_jt_values,
            "sigma_jt_values": sigma_jt_values,
            "y_ftij_values": y_ftij_values,
            # "score": score
        }),
        status=200,
        mimetype='application/json'
    )

    return response


app.run(host='0.0.0.0', port=5000, threaded=False, processes=10, debug=True)
