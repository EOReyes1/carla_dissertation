import os
import subprocess
import multiprocessing
import time
from road_factory import get_road
import config as cfg
from os import path
from data_handler import get_values
import copy

def run_command(cmd):
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               universal_newlines=True)

    while True:
        output = process.stdout.readline()

        return_code = process.poll()
        if return_code is not None:
            # Process has finished, read rest of the output
            for output in process.stdout.readlines():
                print(output.strip())
            break
        return return_code


def run_command_without_printing(cmd, ignore_err_msgs=False):
    if ignore_err_msgs:
        process = subprocess.Popen(cmd, universal_newlines=True,
                                   stderr=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL)
    else:
        process = subprocess.Popen(cmd, universal_newlines=True)
    return_code = process.poll()


def stop_pylot_container(sim_proc):
    if sim_proc and sim_proc.poll() is None:  # still running
        sim_proc.terminate()
        try:
            sim_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            sim_proc.kill()
    print("Simulator stopped.")


def start_pylot_container():
    # Apptainer doesn't need to "start" containers like Docker
    # Containers are executed directly when needed
    print("Apptainer containers execute directly - no start needed")


def start_simulator(tree, buildings, port=2000):
    egg_cache_dir = '/mnt/parscratch/users/jap24omr/tmp/python-eggs'
    os.makedirs(egg_cache_dir, exist_ok=True)

    cmd = [
        'apptainer', 'exec', '--containall',
        '--bind', '/mnt/parscratch/users/jap24omr/SAMOTA/implementation/pylot:/home/erdos/workspace/pylot/pylot',
        '--bind', '/mnt/parscratch/users/jap24omr/SAMOTA/implementation/scripts:/home/erdos/workspace/pylot/scripts',
        '--bind', '/mnt/parscratch/users/jap24omr/SAMOTA/implementation/runner/Results:/home/erdos/workspace/results',
        '--bind', f'{egg_cache_dir}:/tmp/python-eggs:rw',  # NEEDED - storage
        '--bind', '/tmp/.X11-unix:/tmp/.X11-unix:rw',      # NEEDED - X11 display
        # Essential environment
        '--env', f'DISPLAY={os.environ.get("DISPLAY", ":0")}',  # NEEDED - display
        '--env', 'PYTHON_EGG_CACHE=/tmp/python-eggs',            # NEEDED - eggs
        '--env', 'XDG_RUNTIME_DIR=/tmp/runtime-erdos', 
        '--nv',
        '/mnt/parscratch/users/jap24omr/SAMOTA/pylot_improvedv2.sif',
        '/bin/bash', '/home/erdos/workspace/pylot/scripts/run_simulator.sh',
        str(port)  # pass port down to run_simulator.sh
    ]

    # Launch simulator, return process handle
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc



def remove_finished_file():
    #cmd = ['docker', 'exec', 'pylot', 'rm', '-rf', '/home/erdos/workspace/results/finished.txt']

    #run_command_without_printing(cmd)
    #if path.exists("finished.txt"):
    #    os.remove("finished.txt")
    pass

def cleanup_carla():
    """Kill any existing CARLA processes"""
    commands_to_try = [
        ['pkill', '-f', 'apptainer.*pylot'],
        ['pkill', '-f', 'run_simulator.sh'],
        ['pkill', '-f', 'CarlaUE4'],
        ['pkill', '-9', '-f', 'CarlaUE4'],  # Force kill
    ]
    
    for cmd in commands_to_try:
        try:
            result = subprocess.run(cmd, check=False, capture_output=True)
            if result.returncode == 0:
                print(f"Successfully ran: {' '.join(cmd)}")
        except:
            pass
    
    # Wait longer for cleanup
    time.sleep(8)

def handle_container(fv):
    cleanup_carla()
    remove_finished_file()
    port = 2000  # or compute a different one if needed
    proc = start_simulator(fv[13], fv[14], port=port)

    if proc is None:
        raise RuntimeError("Failed to start CARLA simulator")

    print("Waiting for CARLA server to initialize...")
    time.sleep(35)  # give CARLA time to boot

    if proc.poll() is not None:
        stdout, stderr = proc.communicate()
        print(f"CARLA process died! Return code: {proc.returncode}")
        print(f"STDOUT: {stdout.decode()}")
        print(f"STDERR: {stderr.decode()}")
        raise RuntimeError(f"CARLA server failed to start: {stderr.decode()}")

    return proc


def handle_pylot():
    cmd = [cfg.base_directory+'./pylot_runner.sh']
    run_command_without_printing(cmd)


def read_base_file():
    base_file = open(cfg.base_file_name, "r")
    return base_file.read()


def update_file_contents(fv, file_contents):

    file_contents = file_contents + "#####SIMULATOR CONFIG##### \n"

    file_contents = get_road(fv,file_contents)

    file_contents = file_contents + "\n--vehicle_in_front=" + str(fv[3])
    file_contents = file_contents + "\n--vehicle_in_adjcent_lane=" + str(fv[4])
    file_contents = file_contents + "\n--vehicle_in_opposite_lane=" + str(fv[5])
    file_contents = file_contents + "\n--vehicle_in_front_two_wheeled=" + str(fv[6])
    file_contents = file_contents + "\n--vehicle_in_adjacent_two_wheeled=" + str(fv[7])
    file_contents = file_contents + "\n--vehicle_in_opposite_two_wheeled=" + str(fv[8])
    weather = ""
    if (fv[9] == 0):  # noon

        if (fv[10] == 0):  # clear
            weather = "ClearNoon"
        if (fv[10] == 1):  # clear
            weather = "CloudyNoon"
        if (fv[10] == 2):  # clear
            weather = "WetNoon"
        if (fv[10] == 3):  # clear
            weather = "WetCloudyNoon"
        if (fv[10] == 4):  # clear
            weather = "MidRainyNoon"
        if (fv[10] == 5):  # clear
            weather = "HardRainNoon"
        if (fv[10] == 6):  # clear
            weather = "SoftRainNoon"
    if (fv[9] == 1):  # sunset

        if (fv[10] == 0):  # clear
            weather = "ClearSunset"
        if (fv[10] == 1):  # clear
            weather = "CloudySunset"
        if (fv[10] == 2):  # clear
            weather = "WetSunset"
        if (fv[10] == 3):  # clear
            weather = "WetCloudySunset"
        if (fv[10] == 4):  # clear
            weather = "MidRainSunset"
        if (fv[10] == 5):  # clear
            weather = "HardRainSunset"
        if (fv[10] == 6):  # clear
            weather = "SoftRainSunset"
    if (fv[9] == 2):  # sunset

        if (fv[10] == 0):  # clear
            weather = "ClearSunset"
        if (fv[10] == 1):  # clear
            weather = "CloudySunset"
        if (fv[10] == 2):  # clear
            weather = "WetSunset"
        if (fv[10] == 3):  # clear
            weather = "WetCloudySunset"
        if (fv[10] == 4):  # clear
            weather = "MidRainSunset"
        if (fv[10] == 5):  # clear
            weather = "HardRainSunset"
        if (fv[10] == 6):  # clear
            weather = "SoftRainSunset"
        file_contents = file_contents + "\n--night_time=1"

    file_contents = file_contents + "\n--simulator_weather=" + weather
    num_of_pedestrians = 0
    if fv[11] == 0:
        num_of_pedestrians = 0
    if fv[11] == 1:
        num_of_pedestrians = 18

    file_contents = file_contents + "\n--simulator_num_people=" + str(num_of_pedestrians)

    file_contents = file_contents + "\n--target_speed=" + str(fv[12] / 3.6)
    
    log_file_name = '/home/erdos/workspace/results/' + str(fv)
    file_contents = file_contents + "\n--log_fil_name=" + log_file_name

    return file_contents


def move_config_file():
    # Not needed - bind mounting e2e.conf
    pass


def handle_config_file(fv):
    file_contents = read_base_file()

    file_contents = update_file_contents(fv, file_contents)

    e2e_File = open(cfg.base_directory+"e2e.conf", "w")
    e2e_File.write(file_contents)
    e2e_File.close()
    move_config_file()


def scenario_finished():
    cmd = [cfg.base_directory+'./pylot_finish_file_copier.sh']
    run_command_without_printing(cmd, ignore_err_msgs=True)
    if path.exists("./finished.txt"):
        return True
    else:
        return False


def copy_to_host(fv):
    # Not needed - Results will be bind mounted
    print(f"Results available at: /mnt/parscratch/users/jap24omr/SAMOTA/implementation/runner/Results")
    
    main_log_path = f"/mnt/parscratch/users/jap24omr/SAMOTA/implementation/runner/Results/" + str(fv)
    ex_log_path = f"/mnt/parscratch/users/jap24omr/SAMOTA/implementation/runner/Results/" + str(fv) + "_ex.log"
    
    # Copy main log to _ex.log
    try:
        import shutil
        if os.path.exists(main_log_path):
            shutil.copy2(main_log_path, ex_log_path)
        else:
            print(f"Main log not found: {main_log_path}")
    except Exception as e:
        print(f"Failed to create _ex.log: {e}")

def run_single_scenario(fv_arg):

    fv = copy.deepcopy(fv_arg)
    if fv[12]< 10:
        fv[12] = fv[12]*10
    if fv [0] != 3:
        fv[15]=0

    # DEBUG ONLY ------------------------------------------
    #fv = [2, 0, 0, 0, 0, 0, 0, 1, 0, 0, 4, 1, 2, 1, 0, 0]
    #print(f'DEBUG MODE: the scenario is fixed as fv={fv}')
    # -----------------------------------------------------

    sim_process = handle_container(fv)
    handle_config_file(fv)
    handle_pylot()

    counter = 0
    print(f"Single simulation budget (cfg.time_allowed) = {cfg.time_allowed}")
    print("Waiting for scenario to finish")
    while True:
        counter = counter + 1
        time.sleep(1)

        if counter > cfg.time_allowed or scenario_finished():
            print(f"counter: {counter}, "
                  f"cfg.time_allowed: {cfg.time_allowed}, "
                  f"scenario_finished(): {scenario_finished()}")
            stop_pylot_container(sim_process)
            copy_to_host(fv)
            file_name = 'Results/' + str(fv)
            print(os.path.exists(file_name))
            if os.path.exists(file_name):
                DfC_min, DfV_max, DfP_max, DfM_max, DT_max, traffic_lights_max = get_values(fv)
                print("\n\n\n\n\n\n\n\n\n" + str(DfC_min) + "," + str(DfV_max) + "," + str(DfP_max) + "," + str(
                    DfM_max) + "," + str(DT_max) + "," + str(traffic_lights_max))
                return DfC_min, DfV_max, DfP_max, DfM_max, DT_max, traffic_lights_max
            else:
                print(f'File not found: {file_name}')
                return 1000, 1000, 1000, 1000, 1000, 1000

        else:
            print(".", end="", flush=True)
            if counter % 100 == 0:
                print('\n')

def run(fv):
    #     0  1  2  3  4  5  6  7  8  9  10 11 12  13 14

    sim_process = handle_container(fv)

    # 0 Road type
    # 1 Road ID
    # 2 Scenario Length
    # 3 Vehicle_in_front
    # 4 vehicle_in_adjcent_lane
    # 5 vehicle_in_opposite_lane
    # 6 vehicle_in_front_two_wheeled
    # 7 vehicle_in_adjacent_two_wheeled
    # 8 vehicle_in_opposite_two_wheeled
    # 9 time of day
    # 10 weather
    # 11 Number of People
    # 12 Target Speed
    # 13 Trees in scenario
    # 14 Buildings in Scenario
    # 15 task

    handle_config_file(fv)
    handle_pylot()
    counter = 0
    while (True):
        counter = counter + 1
        time.sleep(1)
        
        if (counter > cfg.time_allowed or scenario_finished()):
        
            stop_pylot_container(sim_process)
            break;
        else:
            print("Waiting for scenario to finish")
    copy_to_host(fv)
