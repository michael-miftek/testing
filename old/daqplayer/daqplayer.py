import os
import sys
from multiprocessing import Queue
from queue import Empty, Full
import time

sys.path.append("../..")

#TODO:  Fix the locations
from service.controller.eventhelper.datafile import DataFile

class DaqPlayer:

    def __init__(self, player_queue : Queue, event_queue : Queue, controller_queue : Queue, logging_queue : Queue):
        super().__init__()
        
        self.player_queue = player_queue
        self.event_queue = event_queue
        self.controller_queue = controller_queue

        self.record_file = None
        
        self.max_n = 0
        self.frame_n = 0
        self.min_n = 0
        
        self.seek_frame_n = 0
        self.frame_speed = 0.1
        self.rewind_speed = 1

    def load_recording(self, filename):
        if self.record_file:
            self.record_file.close()
            self.record_file = None
        
        self.record_file = DataFile(filename)
        if (self.record_file.playback() and (self.record_file.count() > 0)):
            self.frame_n = 0
            self.max_n = self.record_file.count()
            
            config_check = self.record_file.get(self.frame_n)
            if ("adc_names" in config_check.keys()) and ("photon_names" in config_check.keys()):
                self.controller_queue.put(("Player", ("config", config_check)))
                self.frame_n += 1
                self.min_n = 1
            
            return True
        
        self.close_recording()
        return False
    
    def close_recording(self):
        if self.record_file:
            self.record_file.close()
        self.record_file = None
        self.frame_n = 0
        self.max_n = 0
        self.min_n = 0

    def run(self, waveform_dicts, frame_num_out):
        command = ""
        frame_increment = 1
        events = []
        events_index = 0
        while True:
            try:
                command, *args = self.player_queue.get(block=False)

            except Empty:
                pass

            except Exception as e:
                print(f"failed command to dplayerioprocess: {e}")

            if command == "finish":
                self.close_recording()
                self.controller_queue.put(("player shutdown",))
                break
            
            elif command == "hold":
                time.sleep(0.1)
                continue
            
            elif command == "load":
                command = "hold"
                ret = self.load_recording(args[0])
                self.controller_queue.put(("Player", ("load", ret)))
                if ret == True:
                    events_index = 0
                    events = []
                
            elif command == "special":
                events = args[0]
                if self.min_n == 1:
                    events = [x+1 for x in events]
                command = "hold"
            
            elif self.record_file:               
                if command == "seek":
                    command = "hold"
                    if 0 <= args[0] <= self.max_n:
                        self.frame_n = args[0]
                        self.controller_queue.put(("Player", ("seek", True)))
                    else:
                        self.controller_queue.put(("Player", ("seek", False)))
                    
                elif command == "speed":
                    command = ""
                    self.frame_speed = args[0]
                    frame_increment = 1
                
                elif command == "rewind":
                    command = ""
                    frame_increment = args[0]
                    self.frame_speed = 0.1

                elif command == "fastforward":
                    command = ""
                    frame_increment = args[0]
                    self.frame_speed = 0.03

                elif command == "stop":
                    command = "hold"
                    self.frame_n = 0

                elif command == "play":
                    command = ""
                    frame_increment = 1
                    self.frame_speed = 0.1

                else: 
                    event = self.record_file.get(self.frame_n)

                    try: 
                        self.event_queue.put(("event", event['event']['data']))
                        waveform_dicts = {"adc_data" : event['event']['data']["adc_data"], 
                                        "photon_data" : event['event']['data']["count_data"]}
                        
                        frame_num_out[0] = f"{self.frame_n} / {self.max_n}"
                        
                        if events:
                            events_index += frame_increment
                            if events_index >= len(events):
                                events_index = len(events) - 1
                                self.frame_n = self.max_n
                                command = "hold"
                            elif events_index < 0:
                                events_index = 0
                                self.frame_n = self.min_n
                                command = "hold"
                            else:
                                self.frame_n = events[events_index]
                        else:
                            self.frame_n += frame_increment
                        if self.min_n > self.frame_n:
                            self.frame_n = self.min_n
                            command = "hold"
                        elif self.frame_n > self.max_n:
                            self.frame_n = self.max_n
                            command = "hold"
                    except Full:
                        pass

                time.sleep(self.frame_speed)
            else:
                command = ""
                time.sleep(0.1)

def daqplayer_start(waveform_dicts, frame_num_out, player_queue, event_queue, controller_queue, logging_queue):
    logging_queue.put(("DEBUG", "Starting Player process"))
    DaqPlayer(player_queue, event_queue, controller_queue, logging_queue).run(waveform_dicts, frame_num_out)
    logging_queue.put(("DEBUG", "Ending Player process"))