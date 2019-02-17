The goal of this project is to log when the active router change. Log are displayed on terminal and can be saved
in a log file and/or in an InfluxDB.

# This tool uses :

* [Requests](http://docs.python-requests.org/) - HTTP library

# Requirements

* Python 3
* Pip

# Install and start the application

1. Download or clone –> https://github.com/lyon-esport/Monitor-VRRP.git

2. Extract the Monitor-VRRP files

3. Install the requirements: `pip install -r requirements.txt`

4. Create config.json (example : config.example)
    * timer - timer between each test
    * log - save in log file
    * influxdb_url - HTTP request InfluxDB (can be an empty string if you don't use it)
    * routers - Array of object (name = router name, hop = number of routers from its source to its destination, vrrp_ip = router VRRP IP)
    
5. Start the program `python main.py`

# HTTP request InfluxDB
For each routers -> `VRRP,name=<router_name> IP=<IP_router_address>`

# Licence

The code is under CeCILL license.

You can find all details here: http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html

# Credits

Copyright © Lyon e-Sport, 2018

Contributor(s):

-Ortega Ludovic - ludovic.ortega@lyon-esport.fr