from typing import List
from map.postition import Position


class LocationFileHandler():
    def __init__(self, file_name:str) -> None:
        self.file_name = file_name

    def read_location_file(self):
        location_entries = []
        with open(self.file_name, encoding="ascii") as file:
            for line in file:
                line_parts = [x for x in line.split("\t") if x != '']
                location_entries.append({
                        "time": float(line_parts[0].split(":")[1]),
                        "lat": float(line_parts[1].split(":")[1]),
                        "lon": float(line_parts[2].split(":")[1]),
                        "heading": float(line_parts[3].split(":")[1]),
                        "speed": float(line_parts[4].split(":")[1])
                    })
        return location_entries

    def write_location_file(self, entries):
        with open(self.file_name, "w") as location_file:
            for state in entries:
                location_file.write(f"Time: {state['time']:.6f} \t Lat:{state['lat']:.5f} \t Long:{state['lon']:.5f} \t Heading: {state['heading']:3.5f} \t Speed:{state['speed']:2.5f}\n")

    def read_position_from_location_file(self):
        position_entries = []
        with open(self.file_name, encoding="ascii") as file:
            for line in file:
                line_parts = [x for x in line.split("\t") if x != '']
                position_entries.append(Position(longitude=float(line_parts[2].split(":")[1]),
                                                 latitude=float(line_parts[1].split(":")[1])))
        return position_entries

    def write_positions_to_location_file(self, entries:List['Position']):
        with open(self.file_name, "w") as location_file:
            for state in entries:
                location_file.write(f"Time: {0.0:.6f} \t Lat:{state.latitude:.5f} \t Long:{state.longitude:.5f} \t Heading: {0.0:3.5f} \t Speed:{0.0:2.5f}\n")


class NodeListHandler():
    def __init__(self, file_name:str) -> None:
        self.file_name = file_name


    def read_node_list(self):
        nodes = []
        with open(self.file_name, encoding="ascii") as file:
            for line in file:
                if line not in nodes:
                    nodes.append(int(line.rstrip()))
        return nodes


    def write_node_list(self, entries):
        with open(self.file_name, "w") as node_log:
            for node in entries:
                node_log.write(f"{node['lat']}\t{node['lon']}\t{id}\n")


    def write_nodes_as_location(self, entries):
        with open(self.file_name, "w") as node_log:
            for node in entries:
                node_log.write(f"Time: {0.0:.6f} \t Lat:{node['lat']:.5f} \t Long:{node['lon']:.5f} \t Heading: {1.0:3.5f} \t Speed:{2.0:2.5f}\n")


    def write_positions_as_location(self, entries:List['Position']):
        with open(self.file_name, "w") as node_log:
            for node in entries:
                node_log.write(f"Time: {0.0:.6f} \t Lat:{node.latitude:.5f} \t Long:{node.longitude:.5f} \t Heading: {1.0:3.5f} \t Speed:{2.0:2.5f}\n")