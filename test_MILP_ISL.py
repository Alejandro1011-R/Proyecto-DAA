import random
import json
from ortools.linear_solver import pywraplp  # For MILP

def generate_instance(instance_id, min_scenes=8, max_scenes=40, min_actors=8, max_actors=20, 
                      min_locations=5, max_locations=20, min_days_factor=1.0, max_days_factor=3.0):
    """Generates a random instance of the Talent Scheduling Problem with Location Costs."""
    num_scenes = random.randint(min_scenes, max_scenes)
    num_actors = random.randint(min_actors, max_actors)
    num_locations = random.randint(min_locations, max_locations)
    
    # Generate scene durations (random between 1 and 5 days)
    scene_durations = {f"s{j}": random.randint(1, 5) for j in range(num_scenes)}
    
    # Total duration required for all scenes
    total_duration = sum(scene_durations.values())
    
    # Define planning horizon
    planning_horizon = random.randint(int(min_days_factor * total_duration), int(max_days_factor * total_duration))
    
    # Generate actors' wages (random between $100 and $1000 per day)
    actor_wages = {f"a{i}": random.randint(100, 1000) for i in range(num_actors)}
    
    # Generate actor participation matrix (binary)
    actor_participation = {f"a{i}": {f"s{j}": random.choice([0, 1]) for j in range(num_scenes)} for i in range(num_actors)}
    
    # Ensure each scene has at least one actor
    for j in range(num_scenes):
        if sum(actor_participation[f"a{i}"][f"s{j}"] for i in range(num_actors)) == 0:
            actor_participation[f"a{random.randint(0, num_actors - 1)}"][f"s{j}"] = 1
    
    # Generate location rental costs (random between $500 and $5000 per day per location)
    location_costs = {f"l{k}": {day: random.randint(500, 5000) for day in range(1, planning_horizon + 1)} 
                      for k in range(num_locations)}
    
    # Save instance to a JSON file
    instance_data = {
        "instance_id": instance_id,
        "num_scenes": num_scenes,
        "num_actors": num_actors,
        "num_locations": num_locations,
        "planning_horizon": planning_horizon,
        "scene_durations": scene_durations,
        "actor_wages": actor_wages,
        "actor_participation": actor_participation,
        "location_costs": location_costs
    }
    
    filename = f"tsp_lc_instance_{instance_id}.json"
    with open(filename, "w") as f:
        json.dump(instance_data, f, indent=4)
    
    print(f"Instance {instance_id} saved to {filename}")
    return instance_data

# MILP Solver using model from the paper

def solve_milp(instance_data):
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        print("Solver not available.")
        return None
    
    num_scenes = instance_data["num_scenes"]
    num_actors = instance_data["num_actors"]
    planning_horizon = instance_data["planning_horizon"]
    
    # Decision Variables
    x = {(i, j): solver.BoolVar(f'x_{i}_{j}') for i in range(num_scenes) for j in range(num_scenes) if i != j}
    y = {(i, j): solver.BoolVar(f'y_{i}_{j}') for i in range(num_scenes) for j in range(1, planning_horizon + 1)}
    t = {i: solver.IntVar(0, planning_horizon, f't_{i}') for i in range(num_scenes)}
    e = {i: solver.IntVar(0, planning_horizon, f'e_{i}') for i in range(num_actors)}
    l = {i: solver.IntVar(0, planning_horizon, f'l_{i}') for i in range(num_actors)}
    
    # Objective function (minimize total actor and location costs)
    objective = solver.Objective()
    for i in range(num_actors):
        objective.SetCoefficient(l[i] - e[i] + 1, instance_data["actor_wages"][f"a{i}"])
    objective.SetMinimization()
    
    solver.Solve()
    print("MILP solution computed.")

# Iterated Local Search (ILS)

def compute_cost(schedule, instance_data):
    """Computes the total cost based on the actor wages and location costs."""
    total_cost = 0
    actor_usage = {actor: [0] * instance_data["planning_horizon"] for actor in instance_data["actor_wages"]}
    
    for i, scene in enumerate(schedule):
        start_day = i
        duration = instance_data["scene_durations"][f"s{scene}"]
        for actor, scenes in instance_data["actor_participation"].items():
            if scenes[f"s{scene}"]:
                for d in range(start_day, start_day + duration):
                    actor_usage[actor][d] = 1
    
    for actor, days in actor_usage.items():
        total_cost += sum(days) * instance_data["actor_wages"][actor]
    
    return total_cost

def solve_ils(instance_data):
    num_scenes = instance_data["num_scenes"]
    
    def local_search(schedule):
        random.shuffle(schedule)
        return schedule
    
    best_schedule = list(range(num_scenes))
    best_cost = compute_cost(best_schedule, instance_data)
    
    for _ in range(100):  # Number of iterations
        new_schedule = local_search(best_schedule[:])
        new_cost = compute_cost(new_schedule, instance_data)
        if new_cost < best_cost:
            best_schedule, best_cost = new_schedule, new_cost
    
    print("ILS solution computed.", best_schedule, "Cost:", best_cost)

# Example: Generate 5 test instances and test both algorithms
for i in range(5):
    instance = generate_instance(i)
    solve_milp(instance)
    solve_ils(instance)
