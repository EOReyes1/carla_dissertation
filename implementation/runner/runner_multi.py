import os
import subprocess
import multiprocessing
import time
from road_factory import get_road
import config as cfg
from os import path
from data_handler_multi import get_values
import copy
import socket

# JOB SPECIFIC JOB ID
task_id = os.environ.get('SLURM_ARRAY_TASK_ID') or 'single'

# FINDS AVAILABLE PORTS
def find_two_free_ports(start_port=2000, end_port=2200):
    free_ports = []
    for port in range(start_port, end_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
                free_ports.append(port)
                if len(free_ports) == 2:
                    return tuple(free_ports)
            except OSError:
                continue
    raise RuntimeError("No two free ports found in range!")

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

def stop_pylot_container(main_port=None, stream_port=None):
    cmd = ['apptainer', 'instance', 'stop', f'pylot_{task_id}']
    run_command(cmd)
    time.sleep(5)

    # Kill Carla-related processes
    for pattern in ['CarlaUE4', 'carla', 'pylot']:
        subprocess.run(['pkill', '-u', 'jap24omr', '-f', pattern], check=False)

    time.sleep(10)

    for port in [main_port, stream_port]:
        try:
            result = subprocess.run(['lsof', '-ti:' + str(port)], capture_output=True, text=True, check=False)       
            if result.stdout.strip():
                for pid in result.stdout.strip().split('\n'):
                    subprocess.run(['kill', '-9', pid], check=False)
                    print(f"Force killed process on port {port}: {pid}")
            time.sleep(3)
        except:
            pass

    # Verifying cleanup worked
    check_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, check=False)
    leftovers = [p for p in ['CarlaUE4', 'carla', 'pylot'] if p in check_result.stdout]
    if leftovers:
        print("WARNING: CARLA processes still running!")
    else:
        print("[SUCCESS] All CARLA processes cleaned up")

    print(f"Stopped CARLA processes")


def start_pylot_container():
    # SIF file path
    sif_path = '/mnt/parscratch/users/jap24omr/SAMOTA/pylot_improvedv2.sif'
    cmd = ['apptainer', 'instance', 'start',
           '--compat',  # Maximum Docker compatibility
           '--bind', '/mnt/parscratch/users/jap24omr/SAMOTA/implementation/pylot:/home/erdos/workspace/pylot/pylot:rw',
           '--bind', '/mnt/parscratch/users/jap24omr/SAMOTA/implementation/scripts:/home/erdos/workspace/pylot/scripts:rw',
           '--bind', f'/mnt/parscratch/users/jap24omr/SAMOTA/implementation/runner/Results_multi/Results_{task_id}:/home/erdos/workspace/results:rw',
           '--bind', f'/mnt/parscratch/users/jap24omr/SAMOTA/implementation/runner/e2e_{task_id}.conf:/home/erdos/workspace/pylot/configs/e2e.conf:rw',
           '--nv',  # NVIDIA GPU support (equivalent to nvidia-docker)
           sif_path, f'pylot_{task_id}']
    run_command(cmd)

def start_simulator(tree, buildings, main_port, stream_port):
    print(f"Assigned ports: {main_port}, {stream_port}")
    cmd = ['apptainer', 'exec', f'instance://pylot_{task_id}',
               '/home/erdos/workspace/pylot/scripts/run_simulator_multi.sh', str(main_port)]
    run_command_without_printing(cmd)

def remove_finished_file():
    cmd = ['apptainer', 'exec', f'instance://pylot_{task_id}', 'rm', '-rf',
           f'/home/erdos/workspace/results/finished.txt']
    run_command_without_printing(cmd)
    if path.exists(f'finished.txt'):
        os.remove(f'finished.txt')

def handle_container(fv, main_port, stream_port):
    stop_pylot_container(main_port, stream_port)
    start_pylot_container()
    remove_finished_file()
    p = multiprocessing.Process(target=start_simulator, name="start_simulator", args=(fv[13], fv[14], main_port, stream_port))
    p.start()
    time.sleep(35)

    return p

def handle_pylot(main_port):
    cmd = [cfg.base_directory+'./pylot_runner_multi.sh', str(main_port)]
    run_command_without_printing(cmd)

def read_base_file():
    base_file = open(cfg.base_file_name, "r")
    return base_file.read()

def update_file_contents(fv, file_contents):
    # This function remains the same - no Docker-specific code
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

    log_file_name = f'/home/erdos/workspace/results/{fv}'
    file_contents = file_contents + "\n--log_fil_name=" + log_file_name

    return file_contents

def move_config_file():
    # Since we bind mount the directory, we can copy directly to the bound path
    pass

def handle_config_file(fv):
    file_contents = read_base_file()
    file_contents = update_file_contents(fv, file_contents)

    e2e_File = open(cfg.base_directory+f'e2e_{task_id}.conf', "w")
    e2e_File.write(file_contents)
    e2e_File.close()
    move_config_file()

def scenario_finished():
    if path.exists(f'/mnt/parscratch/users/jap24omr/SAMOTA/implementation/runner/Results_multi/Results_{task_id}/finished.txt'):
        return True
    else:
        return False

def copy_to_host(fv):
    # With bind mounts, files should already be accessible on host
    pass

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

    main_port, stream_port = find_two_free_ports()

    sim_proc = handle_container(fv, main_port, stream_port)
    handle_config_file(fv)
    handle_pylot(main_port)

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
            if sim_proc.is_alive():
              sim_proc.terminate()
            sim_proc.join()
            stop_pylot_container(main_port, stream_port)
            copy_to_host(fv)
            file_name = f'Results_multi/Results_{task_id}/{fv}'
            if os.path.exists(file_name):
                DfC_min, DfV_max, DfP_max, DfM_max, DT_max, traffic_lights_max = get_values(f"{fv}", f'{task_id}')
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
    handle_container(fv)
    handle_config_file(fv)
    handle_pylot()
    counter = 0
    while (True):
        counter = counter + 1
        time.sleep(1)

        if (counter > cfg.time_allowed or scenario_finished()):
            stop_pylot_container()
            break;
        else:
            print("Waiting for scenario to finish")
    copy_to_host(fv)


