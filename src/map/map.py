import copy
import math
import osmnx
from map.postition import Position
from utils.utils import Utils


class Map:
    '''Position on the map'''

    def __init__(self):
        self.map_radius = 600
        self.max_allowed_distance = 550
        self.map_center = None
        self.map = None
        self.intersection_map = None

        self.max_heading_difference = 60

        self.nodes = []  # save the nodes used

        self.logger = Utils.get_logger()


    def update_map(self, position: Position):
        '''Update map based on new center'''
        
        if self.map_center is not None:
            current_distance = self.map_center.distance_from(position)

        if self.map_center is not None and current_distance < self.max_allowed_distance:
            return

        self.logger.debug("Map edge reached! Updating map... ")

        self.map_center = copy.deepcopy(position)

        self.map = osmnx.graph_from_point(
            (position.latitude, position.longitude), 
            dist=self.map_radius, 
            dist_type='network', 
            simplify=False, 
            network_type='drive', 
            retain_all=False)

        self.intersection_map = osmnx.graph_from_point(
            (position.latitude, position.longitude), 
            dist=self.map_radius, 
            dist_type='network', 
            simplify=True, 
            network_type='drive', 
            retain_all=False)

        # projected map
        self.map = osmnx.project_graph(self.map, to_crs='epsg:3857')
        self.intersection_map = osmnx.project_graph(self.intersection_map, to_crs='epsg:3857')


    def get_nearest_road_position(self, position: Position, heading: float):
        '''Puts the position onto the nearest road'''

        # update map if neccessary
        self.update_map(position)

        # closest edge
        (start_id, end_id, _) = osmnx.distance.nearest_edges(self.map, position.x, position.y)

        # calculate bearing of the edge
        delta_x = self.map.nodes[end_id]['x'] - self.map.nodes[start_id]['x']
        delta_y = self.map.nodes[end_id]['y'] - self.map.nodes[start_id]['y']
        edge_bearing = math.degrees(math.atan2(delta_y, delta_x)) % 360
        
        # correct bearing if neccessary
        if math.fabs(heading - edge_bearing) > 90:
            edge_bearing = (edge_bearing + 180) % 360
        
        #self.logger.debug(f"Used egde: {start_id} - {end_id} with bearing: {edge_bearing} (y:{self.map.nodes[start_id]['y']} x:{self.map.nodes[start_id]['x']} \t to: y:{self.map.nodes[end_id]['y']} x:{self.map.nodes[end_id]['x']})")

        # calculate current position on edge
        normal_vector_x = delta_x
        normal_vector_y = delta_y

        position_x = (normal_vector_x * normal_vector_x * position.x + normal_vector_x * normal_vector_y * position.y + normal_vector_y * normal_vector_y * self.map.nodes[start_id]['x'] - normal_vector_x * normal_vector_y * self.map.nodes[start_id]['y']) / (normal_vector_x * normal_vector_x + normal_vector_y * normal_vector_y)
        position_y = (normal_vector_x * position.x + normal_vector_y * position.y - normal_vector_x * position_x) / normal_vector_y

        latitude, longitude = Position.convert_coordinates_back(position_x, position_y)

        # save the edge nodes for debugging
        if (start_id, _) not in self.nodes:
            self.nodes.append((start_id, self.map.nodes[start_id]))
        if (end_id, _) not in self.nodes:
            self.nodes.append((end_id, self.map.nodes[end_id]))

        return Position(longitude, latitude), edge_bearing, start_id, end_id


    def distance_to_intersection(self, position: Position):
        """Calculates the distance to the nearest node to determine the map data reliability"""
        (neares_node_id, distance_to_node) = osmnx.distance.nearest_nodes(self.intersection_map, position.x, position.y, return_dist=True)
        #self.logger.debug(f"Nearest node is: {neares_node_id} with a distance: {distance_to_node}")
        return distance_to_node


    @staticmethod
    def correct_heading(heading):
        '''Helper function to corrects heading value'''
        return heading % 360


    def save_map_for_offline_usage(self):
        '''Save map to file'''
        if self.map is None:
            self.update_map(Position(longitude=19.0594, latitude=47.4723))
        
        osmnx.save_graphml(self.map, "/workspaces/macrotracking/maps/infopark_map.osm")
        osmnx.save_graphml(self.intersection_map, "/workspaces/macrotracking/maps/infopark_intersection_map.osm")


    def load_map_from_file(self):
        '''Load a saved map file'''
        self.map = osmnx.load_graphml("/workspaces/macrotracking/maps/infopark_map.osm")
        self.intersection_map = osmnx.load_graphml("/workspaces/macrotracking/maps/infopark_intersection_map.osm")


    def dump_nodes_to_files(self, file_name):
        # dump the list of used nodes to file
        node_log = open(file_name, "w")
        for (id, node) in self.nodes:
            node_log.write(f"{node['lat']}\t{node['lon']}\t{id}\n")
