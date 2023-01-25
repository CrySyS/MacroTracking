'''Trace reader module'''
import can  # http://skpang.co.uk/blog/archives/1220
from utils.utils import Utils
from typing import List

# example lines
# 1483093132.049669        0380    000    8    30 bb 82 00 9d 53 00 81
# 1483093132.128087        0280    000    8    00 00 00 00 00 00 00 00
# 1483093132.130010        0180    000    6    64 a0 7f ff 44 00
# timestamp                arb_id  flag   dlc  data
# arb_id = arbitration_id
# flag = remote_frame|id_type|error_frame


class TraceFileReader:
    '''Reades trace data from file'''
    def __init__(self, file, debug=False):
        self.file_name = file
        self.debug = debug
        self.logger = Utils.get_logger()

    def read_line(self):
        '''Reads one line from file'''
        cnt = 0
        error_counter = 0
        with open(self.file_name, encoding="ascii") as file:
            for line in file:
                cnt += 1
                try:
                    split_line = line.split()
                    split_line = [x for x in split_line if x != '']

                    dlc=int(split_line[3])

                    data = split_line[4:4+dlc]
                    data = [int(x, 16) for x in data]

                    yield can.Message(timestamp=float(split_line[0]),
                                      is_remote_frame=bool(int(split_line[2][0])),
                                      is_extended_id=bool(int(split_line[2][1])),
                                      is_error_frame=bool(int(split_line[2][2])),
                                      arbitration_id=int(split_line[1], 16),
                                      dlc=dlc,
                                      data=data)
                
                except (ValueError, IndexError):
                    error_counter = error_counter + 1
                    self.logger.debug("Error, unable to parse line #%d (skipping): '%s'" % (cnt, line))

        if error_counter > 0:
            self.logger.error(f"Number of read errors: {error_counter} ")

    
    def read_complete_file(self) -> List[can.Message]:

        cnt = 0
        can_messages = []

        with open(self.file_name) as f:
            for line in f:
                cnt += 1
                try:

                    if line == '\n':
                        continue

                    split_line = line.split(' ')
                    split_line = [x for x in split_line if x != '']

                    can_messages.append(can.Message(
                        msg_id=int(split_line[1], 16),
                        data=Message.data_str_list_2_int_list(split_line[4:]),
                        timestamp=float(split_line[0]),
                        dlc=int(split_line[3]),
                        is_error_frame=bool(int(split_line[2][2])),
                        is_remote_frame=bool(int(split_line[2][0])),
                        is_extended_id=bool(int(split_line[2][1]))
                    ))

                except IndexError:
                    self.logger.debug(f"Error, unable to parse line #{cnt} (skipping): '{line}'")
                    continue

        return can_messages
