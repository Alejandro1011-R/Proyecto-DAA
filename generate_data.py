import random
import json

def generate_instance(instance_id, min_scenes=5, max_scenes=60, min_actors=3, max_actors=20, 
                      min_locations=5, max_locations=20, min_days_factor=1.0, max_days_factor=4.0):
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

# Example: Generate 5 test instances
for i in range(5):
    generate_instance(i)
