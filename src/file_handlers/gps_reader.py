'''GPS file processor'''

def process_gps_file(gps_file):
    '''GPS file processor function'''
    print(f"Processing gps file information from: {gps_file}")
    gps_lines = []
    with open(gps_file, encoding="ascii") as file:
        for line in file:
            gps_lines.append(line)

    if gps_file.endswith("gpx"):
        gps_lines = [a for a in gps_lines if a.startswith('<trkpt')]
        gps_lines = [a.split('>')[0] for a in gps_lines]
        gps_lines = [[float(a.split(' ')[1][5:-1]),float(a.split(' ')[2][5:-1])] for a in gps_lines]
    else:
        gps_lines = [[a.split(',')[1],a.split(',')[2]] for a in gps_lines]


    gps_positions_file = open("../log/gps.log", "w", encoding="ascii")

    for pos in gps_lines:
        gps_positions_file.write(str(pos[0]) + "\t" + str(pos[1]) + "\n")
