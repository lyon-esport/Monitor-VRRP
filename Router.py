# ----------------------------------------------------------------------------
# Copyright © Lyon e-Sport, 2018
#
# Contributeur(s):
#     * Ortega Ludovic - ludovic.ortega@lyon-esport.fr
#
# Ce logiciel, Monitor-VRRP, est un programme informatique servant à récupérer l'adresse IP
# du routeur actif.
#
# Ce logiciel est régi par la licence CeCILL soumise au droit français et
# respectant les principes de diffusion des logiciels libres. Vous pouvez
# utiliser, modifier et/ou redistribuer ce programme sous les conditions
# de la licence CeCILL telle que diffusée par le CEA, le CNRS et l'INRIA
# sur le site "http://www.cecill.info".
#
# En contrepartie de l'accessibilité au code source et des droits de copie,
# de modification et de redistribution accordés par cette licence, il n'est
# offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
# seule une responsabilité restreinte pèse sur l'auteur du programme,  le
# titulaire des droits patrimoniaux et les concédants successifs.
#
# A cet égard  l'attention de l'utilisateur est attirée sur les risques
# associés au chargement,  à l'utilisation,  à la modification et/ou au
# développement et à la reproduction du logiciel par l'utilisateur étant
# donné sa spécificité de logiciel libre, qui peut le rendre complexe à
# manipuler et qui le réserve donc à des développeurs et des professionnels
# avertis possédant  des  connaissances  informatiques approfondies.  Les
# utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
# logiciel à leurs besoins dans des conditions permettant d'assurer la
# sécurité de leurs systèmes et ou de leurs données et, plus généralement,
# à l'utiliser et l'exploiter dans les mêmes conditions de sécurité.
#
# Le fait que vous puissiez accéder à cet en-tête signifie que vous avez
# pris connaissance de la licence CeCILL, et que vous en avez accepté les
# termes.
# ----------------------------------------------------------------------------

import threading
import subprocess
import logging
from datetime import datetime
import re
import sys
import requests
import os
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Router(threading.Thread):
    def __init__(self, name, hop, next_ip, regex_ip, log, influxdb_url, timer):
        threading.Thread.__init__(self)
        self.regex_ip = regex_ip
        self.router_name = name
        self.hop = hop
        self.next_ip = next_ip
        self.log = log
        self.influxdb_url = influxdb_url
        self.timer = timer
        self.active_router_ip = ""

    def run(self):
        while True:
            self.start_test()
            time.sleep(self.timer)

    def start_test(self):
        pings = {}
        for i in range(0, 3):
            if os.name == "nt":
                proc = subprocess.Popen(["ping", "-n", "1", "-i", str(self.hop), self.next_ip], shell=False,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                check = "ms"
            else:
                proc = subprocess.Popen(["ping", "-c", "1", "-t", str(self.hop), self.next_ip], shell=False,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.wait()
            result = proc.communicate()[0].decode('utf-8', 'ignore')
            try:
                if os.name == "nt":
                    pings[i] = {"returncode": proc.poll(), "line": result.split("\n")[2],
                                "ip": result.split("\n")[2].split(" ")[2][:-1]}
                else:
                    pings[i] = {"returncode": proc.poll(), "line": result.split("\n")[1],
                                "ip": result.split("\n")[1].split(" ")[1]}
            except:
                pass
            try:
                if re.match(self.regex_ip, pings[i]["ip"]):
                    if self.active_router_ip != pings[i]["ip"]:
                        self.active_router_ip = pings[i]["ip"]
                        logger.info("({time}) - {router} : {ip}\n".format(
                            time=datetime.now().replace(microsecond=0), router=self.router_name,
                            ip=pings[i]["ip"]))
                        if self.log:
                            self.write_to_logfile(self.active_router_ip)
                        if self.influxdb_url != "":
                            self.write_to_influx(self.active_router_ip)
                    return 0
                else:
                    if i == len(pings) - 1:
                        if self.active_router_ip != "DOWN":
                            if self.log:
                                self.write_to_logfile("DOWN")
                            if self.influxdb_url != "":
                                self.write_to_influx("DOWN")
                        self.active_router_ip = "DOWN"
                    raise Exception(pings[i]["line"])
            except Exception as e:
                logger.error(
                    "({time}) - {router} Can't parse ping -> {error}".format(time=datetime.now().replace(microsecond=0),
                                                                             router=self.router_name, error=e))

    def write_to_logfile(self, info):
        try:
            file = open("log", "a")
            file.write(
                "{time} - {router} : {ip}\n".format(time=datetime.now().replace(microsecond=0), router=self.router_name,
                                                    ip=info))
            file.close()
        except Exception as e:
            logger.error("%s", e)
            sys.exit(1)

    def write_to_influx(self, info):
        try:
            data = "VRRP,name=" + self.router_name + " IP=\"" + info + "\""
            r = requests.post(self.influxdb_url, data=data)
            if r.status_code != 204:
                logger.error(
                    "Error can't send data to InfluxDB URL --> {url}\nHTTP Error code --> {error_code}".format(url=self.influxdb_url,
                                                                                                               error_code=r.status_code))
        except Exception as e:
            logger.error("Error can't send data to InfluxDB URL --> {url}\nError --> {error}".format(url=self.influxdb_url, error=e))
