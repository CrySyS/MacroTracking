'''Trace data loader module'''
from enum import Enum
from vehicle.vehicle_model import Vehicle
from map.postition import Position
from utils.utils import Utils


class TraceIds(Enum):
    '''List of supported traces'''
    SAMPLE_TRACE = 1


def get_data(trace_id:TraceIds):
    '''Load data for the specified trace'''
    config = Utils.get_config()
    logger = Utils.get_logger()

    perform_map_based_correction = config.getboolean("Macrotracking", "map_based_correction")
    gps_file = None
    trace_root = config['File_locations']['trace_root']
    ground_truth_log = ""
    
    out_folder = config['File_locations']['output_root'] + trace_id.name
    if not perform_map_based_correction:
        out_folder = out_folder + "_uncorrected/"
    else:
        out_folder = out_folder + "/"

    # create folder if not exists
    Utils.create_folder(out_folder)
    # clear output folder
    #Utils.clear_out_folder(out_folder)

    if trace_id == TraceIds.SAMPLE_TRACE:
        trace = trace_root + "trace.log"
        ground_truth_log = trace_root + "ground_truth.log"
        car = Vehicle(Position(latitude=47.47175, longitude=19.05932), start_heading=45, trace_file=trace)
        start_index = 0
        offset = 125000  # the total trace

    if trace:
        logger.debug(f'Selected trace: {trace.split("/")[-1]}')
        logger.debug(f"Ground truth log location: {ground_truth_log}")

    return car, start_index, offset, gps_file, out_folder, ground_truth_log
