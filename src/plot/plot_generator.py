import folium
from utils.utils import Utils


def generate_plot(folder:str):

    logger = Utils.get_logger()
  
    printed_target = 100

    log_lines = []
    coordinates = []

    location_file = folder + "location.log"


    with open(location_file) as f:
        for line in f:
            log_lines.append(line.split('\t'))

    coordinates = [[log[1].split(':')[1], log[2].split(':')[1]] for log in log_lines]

    m = folium.Map(location=[coordinates[0][0], coordinates[0][1]], zoom_start=17)

    counter = 0
    step = int(len(coordinates) / printed_target) if int(len(coordinates) / printed_target) != 0 else 1
    points = []

    while counter * step < len(coordinates):
        state = coordinates[counter*step]
        points.append([float(state[0]), float(state[1])])    
        folium.Marker(
            [state[0], state[1]],
            icon=folium.Icon(color='orange'),
            tooltip="Position(" + str(counter) + "): " + str(log_lines[counter*step])
        ).add_to(m)
        counter += 1

    folium.PolyLine(points, color='orange', weight=4.5, opacity=.7).add_to(m)
    logger.debug(f"Number of log lines during plotting: {len(log_lines)}")

    m.save(folder + "trace.html")
    logger.debug(f"Plot saved to: {folder + 'trace.html'}.")
