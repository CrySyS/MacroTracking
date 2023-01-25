import math
import copy
from typing import List
from can import Message
from map.map import Map
from map.postition import Position
from utils.utils import Utils


class Vehicle():

    _speed_id = int('0x410', 16)
    _steering_pos_id = int('0x180', 16)

    def __init__(self, start_poition:Position, start_heading:float, trace_file:str):
        self.config = Utils.get_config()
        self.debug:bool = self.config.getboolean("Macrotracking", "debug")
        self.perform_map_based_correction = self.config.getboolean("Macrotracking", "map_based_correction")
        self.logger = Utils.get_logger()
        
        self.start_position:Position = Position(start_poition.longitude, start_poition.latitude)
        self.position:Position = Position(start_poition.longitude, start_poition.latitude)
        self.heading:float = start_heading
        self.speed:float = 0
        self.last_update_time:float = 0

        if not self.perform_map_based_correction:
            self.logger.debug("Map based correction is OFF (disabled)!")
        else:
            self.logger.debug("Map based correction is ON!")
        
        self.trace_file = trace_file
        
        self.previus_states:List[VehicleState] = []
        
        # internal parameters of the car
        self._speed_id = int('0x410', 16)
        self._steering_pos_id = int('0x180', 16)

        # internal parameter of turn
        self._turn_radius:float = 100000000000000  # start value almost infinite -> straight line
        self._vehicle_stearing_constant = 2.8e-05  # kisebb érték => kevésbé kanyarodik
        self._vehicle_speed_constant = 1.1  # kisebb érték => jobban kompenzálja a sebességet -> kisebb érték lesz belőle

        # map reference
        self.map:Map = None

        self.last_correction_location:Position = None
        self.minimum_correction_distance:float = 20
        self.minimum_update_time = 1
        self.minimum_heading_correction:float = 0.0001

        self.map_position_weight = 0.4
        self.map_heading_weight = 0.2
        self.max_map_position_weight = 0.7
        self.max_map_heading_weight = 0.7
        self.map_max_heading_difference = 45
        self.max_intersection_distance = 150 # meters


    def process_can_message(self, msg:Message):
        # for first iteration
        if self.last_update_time == 0:
            self.last_update_time = msg.timestamp

        if msg.arbitration_id == self._steering_pos_id:
            self.update_heading(msg.data)

        elif msg.arbitration_id == self._speed_id:
            self.update_speed(msg.data)

        else:
            # skip other messages
            return -1

        # if enough time passed, update the vehicle position
        if msg.timestamp - self.last_update_time > self.minimum_update_time:
            self.update_vehicle_state(msg.timestamp)
            self.last_update_time = msg.timestamp


    def update_heading(self, data):
        """
        Calculate turn radius of the vehicle based on the current stearing wheel position.

        Steering position in 3rd and 4th bytes in two's complement
        0 center, right 65512-57712, left 0-7824
        transformed to -7824 - 7824 range (total left -7824; total right 7824; center 0)
        right turn -> positive radius; left turn -> negative radius
        right turn, ~360 degree = 5736 -> diameter = 12,7 m radius = 6.35 m
        steer 0 -> wheel pi/2=90; 
        steer 5736 -> wheel 1.1688=66.96 => w= -7.009019694554718e-05 * S + pi/2
        car length 2,7 m
        """
        st_pos = int.from_bytes(data[2:4], 'big')
        if data[2] >= 2 ** 7:
            st_pos -= 2 ** 16
        st_pos *= -1
        wh_pos = self._vehicle_stearing_constant * st_pos + math.pi/2  # in radian
        self._turn_radius = 2.7 * math.tan(wh_pos)


    def update_speed(self, data):
        """
        Update the current speed of the vehicle from the CAN value
        """
        # speed in 2nd and 3rd bytes in two decimal precision (dkm/h)
        speed = int.from_bytes(data[1:3], 'big')
        speed = speed / 3.6 / 100  # speed converted to m/s

        '''
        real distance   measured distance   m/r     r/m
        30	            38,46	            1,282	0,780
        60	            78,66	            1,311	0,762
        90	            118,28	            1,314   0,761
        120	            157,56	            1,313	0,762
        150	            196,78	            1,312	0,762
        '''
        self.speed = speed * self._vehicle_speed_constant  # correction for too high speeds, seems to be working


    def update_vehicle_state(self, current_time):

        # if vehicle is not moving, no update is required
        if self.speed == 0:
            return
        
        # if there was no location correction previously
        if self.last_correction_location is None:
            self.last_correction_location = copy.deepcopy(self.position)
            return

        # calculate movement update parameters
        delta_time = current_time - self.last_update_time
        delta_distance = self.speed * delta_time
        delta_heading = (delta_distance * 360) / (2 * self._turn_radius * math.pi)  # heading change in degree is proportional to distance along the turn circle circumference (approximation)

        # minimaze noise if heading is almost 0
        if math.fabs(delta_heading) < self.minimum_heading_correction:
            delta_heading = 0  

        # update heading and position
        self.heading += delta_heading
        self.heading = self.heading % 360
        self.position.move(delta_distance, self.heading)

        # if enough movement happened then correct location based on the map
        if self.perform_map_based_correction and self.position.distance_from(self.last_correction_location) > self.minimum_correction_distance:
            self.update_vehicle_state_from_map(current_time)
            self.last_correction_location = copy.deepcopy(self.position)
            self.logger.debug(f"State update to ({len(self.previus_states) - 1}): {self}")
        else:
            # save current state to archive
            self.previus_states.append(VehicleState(current_time, self, 0, 0, state_modified=False))


    def update_vehicle_state_from_map(self, current_time):

        map_position, edge_bearing, start_id, end_id = self.map.get_nearest_road_position(self.position, self.heading)

        if self.perform_map_based_correction:
            # update map influence ratio
            self.update_map_weights()
        
            # position update
            self.position.x = (1.0 - self.map_position_weight) * self.position.x + self.map_position_weight * map_position.x
            self.position.y = (1.0 - self.map_position_weight) * self.position.y + self.map_position_weight * map_position.y
            self.position.update_latlong_in_postion()

            # heading update
            if math.fabs(self.heading - edge_bearing) < self.map_max_heading_difference:
                self.heading = (1.0 - self.map_heading_weight) * self.heading + self.map_heading_weight * edge_bearing
            else:
                self.logger.debug(f"CRITICAL ERROR: car heading ({self.heading}) and edge heading ({edge_bearing}) mismatch.")

        # save current state to archive
        self.previus_states.append(VehicleState(current_time, self, start_id, end_id, state_modified=True))


    def update_map_weights(self):
        distance_to_intersection = self.map.distance_to_intersection(self.position)

        if distance_to_intersection > self.max_intersection_distance:
            self.map_position_weight = self.max_map_position_weight
            self.map_heading_weight = self.max_map_heading_weight
        else:
            self.map_position_weight = (distance_to_intersection / self.max_intersection_distance) * self.max_map_position_weight
            self.map_heading_weight = (distance_to_intersection / self.max_intersection_distance) * self.max_map_heading_weight
        

    def get_heading(self, msg:Message):
        """
        Get the stearing wheel position from the message
        """
        if msg.arbitration_id == self._steering_pos_id:
            st_pos = int.from_bytes(msg.data[2:4], 'big')
            if msg.data[2] >= 2 ** 7:
                st_pos -= 2 ** 16
            st_pos *= -1
            return st_pos
        
        return None


    @staticmethod
    def set_heading(heading:int, msg:Message):
        "Set the heading value back to the CAN message"
        
        if msg.arbitration_id != Vehicle._steering_pos_id:
            raise Exception("Message type mismatch during setting heading!")
        
        heading *= -1
        if heading < 0:
            heading += 2 ** 16

        msg.data[2:4] = list(int(heading).to_bytes(2, 'big'))
            
            
    def get_speed(self, msg:Message):
        """
        Get the speed from the message
        """
        if msg.arbitration_id == self._speed_id:
            # speed in 2nd and 3rd bytes in two decimal precision (dkm/h)
            speed = int.from_bytes(msg.data[1:3], 'big')
            speed = speed / 3.6 / 100  # speed converted to m/s
            return speed

        return None

    @staticmethod
    def set_speed(speed:int, msg:Message):
        """
        Set the speed in a CAN message
        """
        if msg.arbitration_id != Vehicle._speed_id:
            raise Exception("Message type mismatch during setting speed!")

        speed = speed * 100 * 3.6
        msg.data[1:3] = list(int(speed).to_bytes(2, 'big'))


    def __str__(self):
        return f"Vehicle at: ({self.position}) \tspeed: {self.speed:.5f} m/s \theading: {self.heading:.5f}"


    def dump_states_to_files(self, location_file):
        # dump all vehicle states to file
        location_file = open(location_file, "w")
        for state in self.previus_states:
            location_file.write(str(state))


class VehicleState():

    def __init__(self, time:float, car:Vehicle, start_id, end_id, state_modified:bool=False):
        self.time = time
        self.position = copy.deepcopy(car.position)
        self.heading = car.heading
        self.speed = car.speed
        self.map_weight = car.map_position_weight
        self.start_id = start_id
        self.end_id = end_id
        self.state_modified = state_modified

    def __str__(self):
        return f"Time: {self.time:.6f} \t Lat:{self.position.latitude:.5f} \t Long:{self.position.longitude:.5f} \t Heading: {self.heading:3.5f} \t Speed:{self.speed:2.5f}\n"

    def map_print(self):
        return f"Lat:{self.position.latitude:.5f} \t Long:{self.position.longitude:.5f} \t x:{self.position.x} \t y:{self.position.y} \t Heading: {self.heading:3.5f} \t (start: {self.start_id} end:{self.end_id}) \t Speed:{self.speed:2.5f} \t Weight:{self.map_weight}\n"

    def gps_print(self):
        return f"{self.position.latitude}\t{self.position.longitude}\n"
