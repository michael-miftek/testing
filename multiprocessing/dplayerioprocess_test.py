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
    QUIT = auto()          # Command to exit/terminate the player
    HOLD = auto()          # Command to pause/freeze the current state
    SPEED = auto()         # Command to adjust playback speed
    SPECIAL = auto()       # Command for special/custom operations
    LOAD = auto()          # Command to load media content
    STOP = auto()          # Command to stop playback completely
    GET = auto()           # Command to retrieve current state/information
    REWIND = auto()        # Command to move backwards in playback
    FASTFORWARD = auto()   # Command to move forwards in playback
    PLAY = auto()          # Command to start/resume playback
    CONFIGURE = auto()     # Command to modify player settings   

class PlayerState:
    """Manages the state of the DAQ player
    
    This class handles the playback state and control parameters for the DAQ player,
    including record tracking, playback speed, and command management.
    """
    def __init__(self):
        """Initialize a new PlayerState instance with default values
        
        Attributes:
            record_n (int): Current record number, starting at 0
            max_n (float): Maximum record number limit (infinity by default)
            min_n (int): Minimum record number limit (0 by default)
            playback_speed (float): Playback speed multiplier (100 by default)
            frame_speed (float): Time between frames (1/playback_speed)
            events (list): List to store playback events
            i (int): Current iteration/frame counter
            command (Command): Current player command (defaults to HOLD)
            previous_command (Command): Last executed command (defaults to HOLD)
            data_file (Optional[DaqFile]): Reference to the DAQ data file being played
        """
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
        """Updates the playback speed and frame timing
        
        Args:
            new_speed (float): The new playback speed multiplier
            
        Raises:
            ValueError: If new_speed is less than or equal to 0
            
        Updates both playback_speed and frame_speed attributes based on the new speed value.
        """
        if new_speed <= 0:
            raise ValueError("Playback speed must be positive")
        self.playback_speed = new_speed
        self.frame_speed = 1/self.playback_speed


def process_event(data_queue: Queue, event: Dict[str, Any], action: str) -> bool:
    """Process and queue an event to the data queue
    
    Args:
        data_queue (Queue): The queue to store the event data
        event (Dict[str, Any]): Event data dictionary to be queued
        action (str): Description of the action being performed, used in error messages
        
    Returns:
        bool: True if event was successfully queued, False if queue is full
        
    Raises:
        Full: Handled internally when queue is at capacity
        
    The function attempts to add the event to the queue in a non-blocking manner.
    If the queue is full, it prints an error message and returns False.
    """
    try:
        data_queue.put(("event", event), block=False)
        return True
    except Full:
        print(f"{action} Output queue is full")
        return False


def update_ui(ui_queue: Queue, frame_number: int) -> None:
    """Updates the UI queue with the current frame number
    
    Args:
        ui_queue (Queue): The queue used to communicate with the UI
        frame_number (int): The current frame number to display
        
    Raises:
        Full: Handled internally when queue is at capacity
        
    The function attempts to add the frame number to the UI queue in a non-blocking manner.
    If the queue is full, it prints an error message but does not raise an exception.
    """
    try:
        ui_queue.put(("frame_number", frame_number))
    except Full:
        print("UI queue is full")


def dplayer_io_process(io_queue: Queue, data_queue: Queue, ui_queue: Queue) -> None:
    """Main IO process handler for the DAQ player
    
    This function manages the core IO processing loop for the DAQ player, handling
    commands, playback control, and data file operations.
    
    Args:
        io_queue (Queue): Queue for receiving input/output commands
        data_queue (Queue): Queue for processing DAQ data events
        ui_queue (Queue): Queue for sending updates to the user interface
        
    The function implements a continuous processing loop that:
    - Reads and processes commands from io_queue
    - Handles playback control (play, pause, rewind, etc.)
    - Manages data file loading and reading
    - Updates UI state through ui_queue
    - Controls playback speed and timing
    
    Commands handled:
        - QUIT: Terminates the process
        - HOLD: Pauses playback
        - SPEED: Adjusts playback speed
        - PLAY/REWIND/FASTFORWARD: Controls playback direction and movement
        - LOAD: Loads a new data file
        
    Raises:
        Exception: Any unhandled exceptions during processing are logged and re-raised
    
    Note:
        The function ensures proper cleanup of all queues on exit through
        the finally block.
    """

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
