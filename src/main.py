'''Main module to run Macrotracking'''
from trace_handler import trace_reader
from file_handlers import data_loader
from file_handlers import gps_reader
from plot import plot_generator
from utils.utils import Utils
from map.map import Map
from trace_handler.trace_comparator import CompareTraces


config = Utils.get_config()
DEBUG = config.getboolean("Macrotracking", "debug")
MAP_BASED_CORRECTION = config.getboolean("Macrotracking", "map_based_correction")
logger = Utils.get_logger()

traces = [ data_loader.TraceIds.SAMPLE_TRACE ]


for trace_to_analyse in traces:

    logger.info(f"Running macrotracking on {trace_to_analyse.name}")

    local_map = Map()
    car, start_index, offset, gps_file, output_folder, ground_truth = data_loader.get_data(trace_to_analyse)

    car.map = local_map
    if MAP_BASED_CORRECTION:
        local_map.update_map(car.position)

    if gps_file:
        gps_reader.process_gps_file(gps_file)

    tr_reader = trace_reader.TraceFileReader(car.trace_file, DEBUG)
    MESSAGE_COUNTER = 0

    # Read messages by line
    for msg in tr_reader.read_line():

        MESSAGE_COUNTER = MESSAGE_COUNTER + 1
        if MESSAGE_COUNTER < start_index:
            continue

        car.process_can_message(msg)

        if offset == -1:
            continue

        if MESSAGE_COUNTER > (start_index + offset):
            break

    logger.debug(f"Number of messages: {MESSAGE_COUNTER}.")

    car.dump_states_to_files(output_folder + "location.log")
    if MAP_BASED_CORRECTION:
        local_map.dump_nodes_to_files(output_folder + "node.log")


    # calculate total distance
    i = 0
    total_distance = 0.0
    while i + 1 < len(car.previus_states):
        total_distance += car.previus_states[i].position.distance_from(car.previus_states[i+1].position)
        i += 1
    logger.info(f"Car travelled a total distance of: {total_distance} meters.")


    # calculate distance between start and finish
    end_distance = car.start_position.distance_from(car.previus_states[-1].position)
    logger.info(f"Car trajectory end is {end_distance} meters away from the start.")


    # trace comparison
    logger.debug("Starting trace comparison...")

    distance, std_dev_of_distance, distance_array = CompareTraces(trace_name=trace_to_analyse).compare_traces()
    logger.info(f"Measured distance to ground throuth is: {distance} meters.")
    logger.info(f"Std deviation of the distance to ground throuth is: {std_dev_of_distance} meters.")

    with open(output_folder + "distance_measured.log", "w") as distance_file:
        distance_file.write(f"Car travelled a total distance of: {total_distance} meters.\n")
        distance_file.write(f"Car trajectory end is {end_distance} meters away from the start.\n")
        distance_file.write(f"Measured distance to ground throuth is: {distance} meters.\n")
        distance_file.write(f"Std deviation of the distance to ground throuth is: {std_dev_of_distance} meters.\n")
        distance_file.write(f"Distance values: \n {distance_array}")

    logger.info("Generating plot for trace...")
    plot_generator.generate_plot(output_folder)

    logger.info("Macrotracking sequence for trace completed.")
