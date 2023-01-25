import math
from pyproj import Transformer
#from pyproj import CRS


class Position:
    '''Helper class to store position'''

    def __init__(self, longitude: float, latitude: float) -> None:
        self.longitude = longitude
        self.latitude = latitude
        self.x, self.y = self.project_coodrinate(latitude, longitude)

    def move(self, delta_distance:float, current_heading:float):
        '''Change position'''
        self.x += delta_distance * math.cos(math.radians(current_heading))
        self.y += delta_distance * math.sin(math.radians(current_heading))
        self.latitude, self.longitude = self.convert_coordinates_back(self.x, self.y)

    def distance_from(self, other_position: 'Position') -> float:
        '''Return distance from a nother point in meters'''
        return math.sqrt((self.x - other_position.x)**2 + (self.y - other_position.y)**2)

    def direction_to(self, other_position: 'Position') -> float:
        '''Return direction from this point to another point'''
        delta_x = other_position.x - self.x
        delta_y = other_position.y - self.y
        return math.degrees(math.atan2(delta_y, delta_x)) % 360

    def update_latlong_in_postion(self):
        self.latitude, self.longitude = self.convert_coordinates_back(self.x, self.y)

    def __str__(self) -> str:
        #return f'latitude: {self.latitude:.5f} \tlongitude: {self.longitude:.5f}'
        #return f'y: {self.y} \tx: {self.x} \tlatitude: {self.latitude} \tlongitude: {self.longitude}'
        return f'y: {self.y} \tx: {self.x}'
        
    @staticmethod
    def position_from_node(node):
        """Create a position object from a node"""
        return Position(longitude=node['lon'], latitude=node['lat'])

    @staticmethod
    def project_coodrinate(longitude_x: float, latitude_y: float):
        '''Convert to a projected coordinate system'''
        #crs = CRS.from_epsg(4237)
        #crs = CRS.from_epsg(3857)
        #proj = Transformer.from_crs(crs.geodetic_crs, crs)
        transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
        return transformer.transform(longitude_x, latitude_y)

    @staticmethod
    def convert_coordinates_back(x: float, y: float):
        """inProj = Proj('epsg:3857')
        outProj = Proj('epsg:4326')
        x1,y1 = -11705274.6374,4826473.6922
        x2,y2 = transform(inProj,outProj,x1,y1)
        print x2,y2
        """
        proj = Transformer.from_crs("epsg:3857", "epsg:4326")
        # 0: latitude, 1: longitude
        return proj.transform(x, y)
