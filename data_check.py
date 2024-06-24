import numpy as np

def check_workload(core_per_req_matrix, total_cores , workload_on_source_matrix):
    cores_needed = 0
    for i in range(len(core_per_req_matrix)):
            for j in range(len(core_per_req_matrix[i])):
                cores_needed += core_per_req_matrix[i][j] * workload_on_source_matrix[i][j]
    
    return cores_needed >= total_cores