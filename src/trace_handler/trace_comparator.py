import statistics
from typing import List
import file_handlers.data_loader as data_loader
from file_handlers.file_handlers import LocationFileHandler
from map.postition import Position
from utils.utils import Utils


class CompareTraces():

    def __init__(self, trace_name:str) -> None:
        self.logger = Utils.get_logger()
        self.compare_target = 100
        _, _, _, _, self.trace_folder, self.ground_truth_nodes  = data_loader.get_data(trace_name)
        self.location_trace=self.trace_folder + "location.log"
        

    def compare_traces(self):
        return self.compare_traces_based_on_closest_node()
        #return self.compare_traces_based_on_fix_number_of_nodes()


    def compare_traces_based_on_fix_number_of_nodes(self):
        ground_truth_nodes = LocationFileHandler(self.ground_truth_nodes).read_location_file()
        locations:List[Position] = LocationFileHandler(self.location_trace).read_position_from_location_file()
        chosen_ground_throuth_nodes = []
        chosen_locations = []
            

        # finding 100 points from the ground truth
        ground_truth_step = int(len(ground_truth_nodes) / self.compare_target)

        counter = 0
        while counter * ground_truth_step < len(ground_truth_nodes):
            chosen_ground_throuth_nodes.append(ground_truth_nodes[counter * ground_truth_step])
            counter += 1
        self.logger.debug(f"Ground thruth locations chosen. Number of points: {len(chosen_ground_throuth_nodes)}")


        # finding 100 points from the locations file
        location_step = int(len(locations) / self.compare_target)

        counter = 0
        while counter * location_step < len(locations):
            chosen_locations.append(locations[counter * location_step])
            counter += 1
        self.logger.debug(f"Locations chosen. Number of points: {len(chosen_locations)}")


        # calculate distances between chosen locations
        distances = []
        counter = 0
        while counter < len(chosen_ground_throuth_nodes) and counter < len(chosen_locations):
            distances.append(chosen_locations[counter].distance_from(Position.position_from_node(chosen_ground_throuth_nodes[counter])))
            counter +=1

        return statistics.mean(distances), statistics.stdev(distances), distances


    def compare_traces_based_on_closest_node(self):
        ground_truth_nodes = LocationFileHandler(self.ground_truth_nodes).read_location_file()
        chosen_ground_throuth_nodes = []
        locations:List[Position] = LocationFileHandler(self.location_trace).read_position_from_location_file()
            
        # finding 100 points from the ground truth
        ground_truth_step = int(len(ground_truth_nodes) / self.compare_target)

        counter = 0
        while counter * ground_truth_step < len(ground_truth_nodes):
            chosen_ground_throuth_nodes.append(ground_truth_nodes[counter * ground_truth_step])
            counter += 1
        self.logger.debug(f"Ground thruth locations chosen. Number of points: {len(chosen_ground_throuth_nodes)}")


        distances = []
        chosen_locations = []

        # find closest location to every node of the ground truth in the trajectory
        for node in chosen_ground_throuth_nodes:
            node_postion = Position.position_from_node(node)
            closest_location = locations[0]
            closest_distance = locations[0].distance_from(node_postion)

            for location in locations:
                if location.distance_from(node_postion) < closest_distance:
                    closest_distance = location.distance_from(node_postion)
                    closest_location = location

            distances.append(closest_distance)
            chosen_locations.append(closest_location)

        # print the list of chosen points for distance calculation
        LocationFileHandler(self.trace_folder + "distance_chosen_locations_from_trace.log").write_positions_to_location_file(chosen_locations)

        return statistics.mean(distances), statistics.stdev(distances), distances
