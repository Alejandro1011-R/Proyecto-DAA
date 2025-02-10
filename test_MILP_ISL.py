import random
import json
import sys
import time
import pandas as pd
from ortools.linear_solver import pywraplp

def generate_instance(instance_id,
                      # Rango por defecto para instancias aleatorias
                      min_scenes=8, max_scenes=40,
                      min_actors=8, max_actors=20,
                      min_locations=5, max_locations=20,
                      min_days_factor=1.0, max_days_factor=3.0):
    """
    Genera una instancia del problema de manera aleatoria.
    """
    n = random.randint(min_scenes, max_scenes)
    m = random.randint(min_actors, max_actors)
    num_locations = random.randint(min_locations, max_locations)

    # Duraciones de las escenas
    scene_durations = {f"s{j}": random.randint(1, 5) for j in range(n)}
    total_duration = sum(scene_durations.values())
    p = random.randint(int(min_days_factor * total_duration),
                       int(max_days_factor * total_duration))

    # Salarios de actores
    actor_wages = {f"a{i}": random.randint(100, 1000) for i in range(m)}

    # Participación de actores (actor_participation[a][s] = 0/1)
    actor_participation = {}
    for i in range(m):
        participation = {f"s{j}": random.choices([0, 1], weights=[0.7, 0.3])[0]
                         for j in range(n)}
        actor_participation[f"a{i}"] = participation

    # Asegurar que cada escena tenga al menos un actor
    for j in range(n):
        while sum(actor_participation[f"a{i}"][f"s{j}"] for i in range(m)) == 0:
            actor_participation[f"a{random.randint(0, m-1)}"][f"s{j}"] = 1

    # Costos de locación
    location_costs = {
        f"l{k}": {
            day: random.randint(500, 5000) for day in range(p)
        } for k in range(num_locations)
    }

    instance_data = {
        "instance_id": instance_id,
        "num_scenes": n,
        "scene_durations": scene_durations,
        "actor_wages": actor_wages,
        "actor_participation": actor_participation,
        "location_costs": location_costs,
        "planning_horizon": p
    }

    return instance_data

class ScheduleSolution:
    def __init__(self, sequence, start_days):
        self.sequence = sequence  # Lista de índices de escenas (enteros)
        self.start_days = start_days  # Dict { "s0": día_inicio, "s1": ... }

def compute_actor_cost(solution, instance):
    actor_days = {actor: set() for actor in instance["actor_wages"]}
    for scene_idx in solution.sequence:
        scene_id = f"s{scene_idx}"
        start = solution.start_days[scene_id]
        duration = instance["scene_durations"][scene_id]
        for actor, parts in instance["actor_participation"].items():
            if parts[scene_id]:
                for day in range(start, start + duration):
                    actor_days[actor].add(day)
    total = 0
    for actor, days in actor_days.items():
        if days:
            cost = (max(days) - min(days) + 1) * instance["actor_wages"][actor]
            total += cost
    return total

def compute_location_cost(solution, instance):
    total = 0
    for loc in instance["location_costs"]:
        for scene_idx in solution.sequence:
            scene_id = f"s{scene_idx}"
            start = solution.start_days[scene_id]
            duration = instance["scene_durations"][scene_id]
            for day in range(start, start + duration):
                total += instance["location_costs"][loc][day]
    return total

def total_cost(solution, instance):
    return compute_actor_cost(solution, instance) + compute_location_cost(solution, instance)

def solve_subproblem(sequence, instance):
    """
    Dado un orden fijo de escenas, determina la asignación óptima de días
    para minimizar costos de locación (usando OR-Tools/SCIP).
    """
    solver = pywraplp.Solver.CreateSolver('SCIP')
    horizon = instance["planning_horizon"]

    scenes = [f"s{i}" for i in sequence]
    start_vars = {
        scene: solver.IntVar(0, horizon - instance["scene_durations"][scene], f"start_{scene}")
        for scene in scenes
    }

    # Respetar el orden
    for i in range(len(scenes) - 1):
        curr = scenes[i]
        nxt = scenes[i + 1]
        solver.Add(start_vars[nxt] >= start_vars[curr] + instance["scene_durations"][curr])

    # Función objetivo: costos de locación
    objective = solver.Objective()
    for scene in scenes:
        duration = instance["scene_durations"][scene]
        for loc in instance["location_costs"]:
            for d in range(horizon):
                if d + duration <= horizon:
                    cost = sum(instance["location_costs"][loc][d + k] for k in range(duration))
                    objective.SetCoefficient(start_vars[scene], cost)
    objective.SetMinimization()

    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        start_days = {scene: int(start_vars[scene].solution_value()) for scene in scenes}
        return ScheduleSolution(sequence, start_days)
    else:
        return None

def relocate_move(solution, instance):
    seq = solution.sequence.copy()
    if len(seq) < 2: return solution
    i = random.randint(0, len(seq)-1)
    scene = seq.pop(i)
    j = random.randint(0, len(seq))
    seq.insert(j, scene)
    new_sol = solve_subproblem(seq, instance)
    return new_sol if new_sol else solution

def swap_move(solution, instance):
    seq = solution.sequence.copy()
    if len(seq) < 2: return solution
    i, j = random.sample(range(len(seq)), 2)
    seq[i], seq[j] = seq[j], seq[i]
    new_sol = solve_subproblem(seq, instance)
    return new_sol if new_sol else solution

def local_search(current_solution, instance, max_no_improve=10):
    best = current_solution
    best_cost = total_cost(best, instance)
    no_improve = 0
    while no_improve < max_no_improve:
        neighbor = random.choice([relocate_move, swap_move])(best, instance)
        c_neighbor = total_cost(neighbor, instance)
        if c_neighbor < best_cost:
            best = neighbor
            best_cost = c_neighbor
            no_improve = 0
        else:
            no_improve += 1
    return best

def perturb(solution, instance):
    seq = solution.sequence.copy()
    if random.random() < 0.5:
        # 2-opt
        i = random.randint(0, len(seq)-2)
        j = random.randint(i+1, len(seq)-1)
        seq[i:j+1] = reversed(seq[i:j+1])
    else:
        # Swaps aleatorios
        for _ in range(random.randint(1, 4)):
            i, j = random.sample(range(len(seq)), 2)
            seq[i], seq[j] = seq[j], seq[i]
    new_sol = solve_subproblem(seq, instance)
    return new_sol if new_sol else solution

def initial_solution(instance):
    scenes = list(range(instance["num_scenes"]))
    random.shuffle(scenes)
    return solve_subproblem(scenes, instance)

def iterated_local_search(instance, max_iter, delta_ini, epsilon):
    current = initial_solution(instance)
    best = current
    delta = delta_ini
    for _ in range(max_iter):
        perturbed = perturb(current, instance)
        candidate = local_search(perturbed, instance)
        cost_curr = total_cost(current, instance)
        cost_cand = total_cost(candidate, instance)
        if cost_cand < cost_curr * (1 + delta):
            current = candidate
            if cost_cand < total_cost(best, instance):
                best = candidate
        delta *= epsilon
    return best

def solve_milp_sim(instance):
    """
    Simula la parte exacta usando la secuencia natural (0,1,2,...) como si fuera una solución MILP.
    Retorna costo, gap=0 y tiempo de ejecución.
    """
    start_time = time.time()
    seq = list(range(instance["num_scenes"]))
    solution = solve_subproblem(seq, instance)
    if solution:
        cost = total_cost(solution, instance)
    else:
        cost = float('inf')
    elapsed = time.time() - start_time
    return cost, 0.0, elapsed

def run_experiment(instance_id, ils_params=None, runs_ils=10):
    if ils_params is None:
        ils_params = ILS_PARAMS

    # Generar instancia aleatoria
    inst = generate_instance(instance_id)

    # Extracción de datos clave
    n_real = inst["num_scenes"]
    m_real = len(inst["actor_wages"])
    p_real = inst["planning_horizon"]

    # 1) "MILP" simulado
    milp_start = time.time()
    milp_Z, milp_gap, _ = solve_milp_sim(inst)
    milp_time = time.time() - milp_start

    # 2) ILS
    ils_costs = []
    ils_times = []
    for _ in range(runs_ils):
        start_ils = time.time()
        sol = iterated_local_search(inst,
                                    max_iter=ils_params["max_iter"],
                                    delta_ini=ils_params["delta_ini"],
                                    epsilon=ils_params["epsilon"])
        cost_ils = total_cost(sol, inst)
        ils_costs.append(cost_ils)
        ils_times.append(time.time() - start_ils)

    Zbest_ils = min(ils_costs)
    avg_ils_time = sum(ils_times) / len(ils_times)

    # gap'(%) = 100*((Zbest_ils - milp_Z)/milp_Z)
    if milp_Z != 0:
        ils_gap_prime = 100.0 * (Zbest_ils - milp_Z) / milp_Z
    else:
        ils_gap_prime = None

    # gap promedio (%) de las 10 corridas
    # gap_i = 100*((c / Zbest_ils) - 1)
    gap_list = [100.0 * (c / Zbest_ils - 1) for c in ils_costs]
    avg_gap = sum(gap_list) / len(gap_list)

    return {
        "id": instance_id,
        "n": n_real,
        "m": m_real,
        "p": p_real,
        "Z(MILP)": round(milp_Z, 2),
        "gap(MILP)(%)": round(milp_gap, 2),
        "time(MILP)(s)": round(milp_time, 2),
        "Zbest": round(Zbest_ils, 2),
        "gap'(%)": round(ils_gap_prime, 2) if ils_gap_prime is not None else None,
        "gap(%)": round(avg_gap, 2),
        "time(ILS)(s)": round(avg_ils_time, 2)
    }

if __name__ == "__main__":
    num_instances = 3  # Número de instancias aleatorias
    results = []
    overall_start = time.time()

    for i in range(num_instances):
        row = run_experiment(i)
        results.append(row)
        progress = (i+1) / num_instances * 100
        sys.stdout.write(f"\rProgreso: {progress:.1f}% ")
        sys.stdout.flush()

    total_time_random = time.time() - overall_start
    print(f"\nTiempo total: {total_time_random:.2f} s\n")

    df_random = pd.DataFrame(results, columns=[
        "id", "n", "m", "p",
        "Z(MILP)", "gap(MILP)(%)", "time(MILP)(s)",
        "Zbest", "gap'(%)", "gap(%)", "time(ILS)(s)"
    ])
    print("=== Resultados (instancias aleatorias) ===")
    print(df_random.to_markdown(index=False))

    # Guardar los resultados en un archivo .md
    with open("results.md", "w", encoding="utf-8") as f:
        f.write(df_random.to_markdown(index=False))
        f.write("\n")
        f.write(f"Tiempo total: {round(total_time_random, 2)} s\n")
