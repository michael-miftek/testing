# Standard library imports
import os
import sys
import numpy as np
import time
from data.daqfile import DaqFile
from multiprocessing import Queue
from queue import Empty, Full
from enum import Enum, auto
from typing import Optional, Dict, Any

class Command(Enum):
    """Enum class to represent all possible player commands"""
    QUIT = auto()          
    HOLD = auto()          
    SPEED = auto()         
    SPECIAL = auto()       
    LOAD = auto()          
    STOP = auto()          
    GET = auto()           
    REWIND = auto()        
    FASTFORWARD = auto()   
    PLAY = auto()          
    CONFIGURE = auto()     

class PlayerState:
    """Manages the state of the DAQ player"""
    def __init__(self):
        self.record_n = 0              
        self.max_n = np.inf           
        self.min_n = 0                
        self.playback_speed = 100     
        self.frame_speed = 1/self.playback_speed  
        self.events = []              
        self.i = 0                    
        self.command = Command.HOLD   
        self.previous_command = Command.HOLD  
        self.data_file: Optional[DaqFile] = None  

    def update_frame_speed(self, new_speed: float) -> None:
        """Updates the playback speed and frame timing"""
        if new_speed <= 0:
            raise ValueError("Playback speed must be positive")
        self.playback_speed = new_speed
        self.frame_speed = 1/self.playback_speed

def process_event(data_queue: Queue, event: Dict[str, Any], action: str) -> bool:
    """Process and queue an event"""
    try:
        data_queue.put(("event", event), block=False)
        return True
    except Full:
        print(f"{action} Output queue is full")
        return False

def update_ui(ui_queue: Queue, frame_number: int) -> None:
    """Update UI with frame number"""
    try:
        ui_queue.put(("frame_number", frame_number))
    except Full:
        print("UI queue is full")

def dplayer_io_process(io_queue: Queue, data_queue: Queue, ui_queue: Queue) -> None:
    """Main IO process for DAQ player"""
    state = PlayerState()

    try:
        while True:
            try:
                cmd_str, *args = io_queue.get(block=False)
                state.command = Command[cmd_str.upper()]
            except Empty:
                pass
            except (KeyError, ValueError) as e:
                print(f"Invalid command received: {e}")
                continue
            except Exception as e:
                print(f"Failed command to dplayer_io_process: {e}")
                continue

            if state.command == Command.QUIT:
                break

            if state.command == Command.HOLD:
                time.sleep(0.5)
                continue

            if state.command == Command.SPEED and args:
                try:
                    state.update_frame_speed(float(args[0]))
                    if state.previous_command in (Command.PLAY, Command.REWIND):
                        state.command = state.previous_command
                except ValueError as e:
                    print(f"Invalid speed value: {e}")

            if state.command in (Command.PLAY, Command.REWIND, Command.FASTFORWARD):
                if state.data_file is None:
                    print("No data file loaded")
                    state.command = Command.HOLD
                    continue

                if state.command == Command.REWIND:
                    if state.record_n <= state.min_n:
                        state.command = Command.HOLD
                        continue
                    state.record_n -= 1
                else:
                    if state.record_n >= state.max_n:
                        state.command = Command.HOLD
                        continue
                    state.record_n += 1

                try:
                    packet = state.data_file.get(state.record_n)
                    event = packet['event']['data']
                    if process_event(data_queue, event, state.command.name.lower()):
                        update_ui(ui_queue, state.record_n)
                except (KeyError, AttributeError) as e:
                    print(f"Error processing frame: {e}")
                    state.command = Command.HOLD

            if state.command == Command.LOAD and args:
                try:
                    state.data_file = DaqFile(args[0])
                    state.data_file.playback()
                    state.max_n = state.data_file.count()
                    if state.max_n > 0:
                        temp = state.data_file.get(0)
                        if all(key in temp for key in ("adc_names", "photon_names")):
                            ui_queue.put(("config", temp))
                            state.min_n = state.record_n = 1
                        update_ui(ui_queue, state.record_n)
                        state.command = Command.HOLD
                except Exception as e:
                    ui_queue.put(("exception", f"DPlayerIO: Exception loading daqfile: {e}"))

            state.previous_command = state.command
            time.sleep(state.frame_speed)

    except Exception as e:
        print(f"DaqPlayer IO Process leaving queue: {e}")
        raise
    finally:
        for queue in (io_queue, data_queue, ui_queue):
            queue.cancel_join_thread()
        print("DaqPlayer IO Process Shutdown")
