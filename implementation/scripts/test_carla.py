import carla
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()

blueprint_library = world.get_blueprint_library()
vehicle_bp = blueprint_library.filter('vehicle.*')[0]  # pick any
spawn_point = world.get_map().get_spawn_points()[0]
vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)

if vehicle:
    print(f"Spawned vehicle id={vehicle.id} at {vehicle.get_location()}")
else:
    print("Failed to spawn vehicle")
