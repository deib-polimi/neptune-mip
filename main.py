import json
from logging.config import dictConfig

from flask import Flask, request

from core import data_to_solver_input, check_input
from core.utils.convert_values import *
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
    'NeptuneFunctionsFirst': NeptuneFunctionsFirst,
}


@app.route('/')
def serve():
    print("Request received")
    input_data = request.json
    # DEBUG
    # print(input_data)
    check_input(input_data)

    solver_info = input_data.get("solver", {'type': 'NeptuneMinDelayAndUtilization'})
    print("Solver: ", solver_info)
    solver_type = solver_info.get("type")
    print("Solver type: ", solver_type)
    solver_args = solver_info.get("args", {})
    print("Solver args: ", solver_args)
    with_db = input_data.get("with_db", True)
    objective_function_args = solver_args.pop("objective_function", {})

    # Fetch the solver class from the mapping
    SolverClass = solver_classes.get(solver_type)
    if SolverClass is None:
        raise ValueError(f"Unknown solver type: {solver_type}")

    # Instantiate the solver
    solver = SolverClass(**solver_args, **objective_function_args)
    print(solver)

    '''
    solver = eval(solver_type)(**solver_args)
    print(solver)
    '''
    solver.load_data(
        data_to_solver_input(input_data, with_db=with_db, workload_coeff=input_data.get("workload_coeff", 1)))
    status = solver.solve()
    # x, c = solver.results()
    q, c, mu, sigma, y, c_f, c_r, c_w, c_s = solver.results()
    score = solver.score()
    print("INTER", score)

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

    q_ijt_values = convert_q(q, solver.data)
    c_fi_values = convert_c(c, solver.data)
    mu_jt_values = convert_mu(mu, solver.data)
    sigma_jt_values = convert_sigma(sigma, solver.data)
    y_ftij_values = convert_y(y, solver.data)

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
            "score": score,
            "status": status,
            "c_f": c_f,
            "c_r": c_r,
            "c_w": c_w,
            "c_s": c_s
        }),
        status=200,
        mimetype='application/json'
    )

    return response


app.run(host='0.0.0.0', port=5000, threaded=False, processes=10, debug=True)
