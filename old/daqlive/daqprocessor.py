import os
import sys

if 'LIBCYTOSPECTRUM_PATH' in os.environ:
    sys.path.append(os.environ['LIBCYTOSPECTRUM_PATH'])
    import pycytospectrum
else:
    from service.libcytospectrum import pycytospectrum

import queue
from queue import Empty, Full
from multiprocessing import Queue
import numpy as np
import datetime
import time

sys.path.append("../..")

#TODO:  Fix the locations
from service.controller.eventhelper.datafile import DataFile

class DaqProcessor:
    """
    This class is derived from the original daq_io_process
    """

    def __init__(self, processor_queue : Queue, event_queue : Queue, controller_queue : Queue, logging_queue : Queue):
        super().__init__()
        self.processor_queue = processor_queue
        self.event_queue = event_queue
        self.controller_queue = controller_queue
        self.logging_queue = logging_queue

        self.record_file = None
        self.usb_device = []
        self.frame_n = 0

    def open_connection(self):
        devices = None
        new_dev = []
        try:
            devices = pycytospectrum.list_devices()
            
            for n, dev in enumerate(devices):
                print(f"Device {n}: {dev.serial}, Opened? {dev.opened}, SuperSpeed? {dev.super_speed}")            

            new_dev = [dev.serial for dev in devices if dev.serial.startswith("DAQ")]
            
            if new_dev:
                try:
                    self.usb_device = (pycytospectrum.open(new_dev))
                except Exception as e:
                    print(f"Error opening device: {e}")

            if not self.usb_device:
                print(f"Error: no usb-device set: {self.usb_device}")
            else:
                print(f"DAQs connected {self.usb_device}")                
                return True, new_dev
            
        except Exception as e:
            print(f"Opening exception: {e}")
    
        return False, new_dev
    
    def close_connection(self):
        if self.usb_device:
            try:
                self.usb_device.close()
                self.usb_device = []
            except Exception as e:
                print(f"Error in DIO: {e}")
                return False

        return True

    def toggle_recording(self, filename):
        """
        This method is derived from the toggle recording part of the original daq_io long running
        process.
        """
        operation = ""
        if self.record_file is None:
            self.record_file = DataFile(filename)
                
            if self.record_file.record() is False:
                self.record_file = None
                return False, ""
            
            operation = "open"

        else:
            self.record_file.close()
            self.record_file = None
            operation = "close"
        
        self.frame_n = 0
        return True, operation

    def run(self, waveform_dicts, frame_num_out):
        blocking = True
        while True:

            try:
                command, *args = self.processor_queue.get(block=blocking)

                if command == "finish":
                    if self.usb_device:
                        ret = self.close_connection()
                        self.controller_queue.put(("Live", ("close", ret)))
                        if ret == True:
                            blocking=True
                    self.controller_queue.put(("processor_shutdown",))
                    break

                elif command == "open":
                    ret, devices = self.open_connection()
                    self.controller_queue.put(("Live", ("open", ret, devices)))
                    if ret == True:
                        blocking=False

                elif command == "close":
                    ret = self.close_connection()
                    self.controller_queue.put(("Live", ("close",ret)))
                    if ret == True:
                        blocking=True

                elif command == "record":
                    ret, op = self.record_file(args[0])
                    self.controller_queue.put(("Live", ("record", ret, op)))

                else:
                    print(f"Unrecognized command {command}")
                    continue
            
            except Empty:
                pass

            if not self.usb_device:
                blocking=True
                time.sleep(0.1)
                continue


            input_daq_params = []
            input_adc = []
            input_count = []
            pdt_capture = []
            pdt_params = []
            pickleable_event = {}
            pickleable_event["data"] = {}
            pickleable_event["event"] = None
            pickleable_event["data"]["adc_data"] = [None]
            pickleable_event["data"]["count_data"] = [None]
            pickleable_event["data"]["daq_params"] = [None]
            # pickleable_event["data"]["pdt_data"] = [None]
            # pickleable_event["data"]["pdt_params"] = [None]
            # pickleable_event["data"]["time"] = [None]


            try:
                event = self.usb_device.read()
            except Exception as e:
                print(f"Error from pycytospectrum lib: {e} : closing usb connections")
                if self.usb_device:
                    self.usb_device.close()
                self.controller_queue.put(("Live", ("failure", e)))
                
                blocking = True
                continue

            if event is not None:
                # pickleable_event["data"]["time"] = event.summary.get_timestamp()
                pickleable_event["event"] = event.event_id

                # if event.pdt_parameters: 
                #     """     (Laser, 5, 12) only one since this is the QPD
                #     Defined by protocol
                #     Absolute Area
                #     Positive Peak
                #     Positive Width
                #     Negative Peak
                #     Negative Width
                #     """
                #     pdt_params.append(np.array(event.pdt_parameters, copy=False))
                
                # if event.pdt_parameters is not None: 
                # """
                # Defined by protocol (Sample, 12) only one since this is the QPD

                # """
                #     pickleable_event["data"]["pdt_data"] = np.array(event.pdt_capture, copy=False)
                
                for i in event.daq_parameters:
                    """     (Laser, 5, 12) per daq
                    Defined by protocol
                    Area            -> final parameter
                    Peak            -> peak
                    Width           -> width
                    Photon Integral -> Software total
                    Analog Integral -> Software Area
                    """
                    if i is not None:
                        input_daq_params.append(np.array(i, copy=False))
                
                for i in event.daq_analog_capture:    # (Sample, 12) per daq
                    if i is not None:
                        input_adc.append(np.array(i, copy=False))
                    
                for i in event.daq_photon_capture:    # (Sample, 12) per daq
                    if i is not None:
                        input_count.append(np.array(i, copy=False))
                    
                try:
                    if len(input_adc) > 1:
                        pickleable_event["data"]["adc_data"] = np.column_stack(input_adc)
                    else:
                        pickleable_event["data"]["adc_data"] = input_adc[0]

                    if input_count:
                        if len(input_count) > 1:
                            pickleable_event["data"]["count_data"] = np.column_stack(input_count)
                        else:
                            pickleable_event["data"]["count_data"] = input_count[0]

                    if input_daq_params:
                        if len(input_daq_params):
                            pickleable_event["data"]["daq_params"] = np.concatenate(input_daq_params, axis=2)
                        else:
                            pickleable_event["data"]["daq_params"] = input_daq_params[0]
                    # if pdt_params:
                    #     pickleable_event["data"]["pdt_params"] = np.concatenate(pdt_params, axis=2)
                except Exception as e:
                    print(f"Error on trying to stack inputs: {e}")
                    input_adc = []

            if input_adc:

                if self.record_file is not None:
                    self.record_file.append({
                        "time": datetime.now(),
                        "event": pickleable_event
                    })
                    self.frame_n += 1
                    waveform_dicts = {"adc_data" : event['event']['data']["adc_data"], 
                                      "photon_data" : event['event']['data']["count_data"]}
                    
                    frame_num_out[0] = f"{self.frame_n}"
                
                #TODO:  By definition this needs to be just a queue put, the queue should not ever 
                #       lose any data for the finished product
                try:
                    self.event_queue.put(("event", pickleable_event["data"]), block=False)
                except Full:
                    self.logging_queue.put(("WARN", f"Live processor queue was full and didn't send event: {event.event_id}"))
                    pass

def daqprocessor_start(waveform_dicts, frame_num_out, processor_queue, event_queue, controller_queue, logging_queue):
    
    logging_queue.put(("DEBUG", "Starting Live process"))
    DaqProcessor(processor_queue, event_queue, controller_queue, logging_queue).run(waveform_dicts, frame_num_out)
    logging_queue.put(("DEBUG", "Ending Live process"))