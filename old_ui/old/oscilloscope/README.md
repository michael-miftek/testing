# Oscilloscope

This folder contains the entire **Oscilloscope** service, logging, API calls, and all other items that will be attached to the **Oscilloscope** service. This service and all services will be written in a way that they will be able to exist on their own; in each service folder there will be a `main.py` file that will run  the service as a stand alone.


# Files
|     Name	     |Description                    |Purpose                         |
|----------------|-------------------------------|-----------------------------|
|oscilloscope.py 	 |This is the service file       |'Isn't this fun?'            |
|main.py         |This is called to run the oscilloscope service |"Isn't this fun?"            |



## Run Oscilloscope Service

There is one item that need to happen before running `python main.py` with in this directory.

- The user will need to make sure there is current libcytospectrum library files placed in a folder named `libcytospectrum` inside of service

```bash
SSM-KERNEL
├───client
├───config
├───data
├───docs
├───kernel
├───proto
├───service
│   ├───autotrigger
│   ├───controller
│   ├───fluidics
│   ├─── **libcytospectrum**
│   ├───mainboard
├───test
└───ui
```

If the user is building libcytospectrum using the cytospectrum repo the files to copy into the new libcytospectrum directory can be found in `cytospectrum\detection\libcytospectrum\build\Release`

Once this directory and all library files are added then the user can either create a virtual environment by running the next commands in the `ssm-kernel\ui\oscilloscope` directory.
1. `python -m venv venv`  
2. `venv\Scripts\activate` 
3. `pip install -r requirements.txt` 
Or run the command `python main.py` in the `ssm-kernel\ui\oscilloscope` directory

After this is complete, it is important to load the following four files into the /proto/ directory:
- command_pb2.py
- embedded_proto_options_pb2.py
- schema_pb2.py
- shared_pb2.py