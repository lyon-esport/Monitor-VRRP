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

import json
import sys
import logging
import re

from Router import Router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

regex_ip = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"

# get configuration
try:
    with open('config.json') as json_data_file:
        config = json.load(json_data_file)
except Exception as e:
    logger.error("%s", e)
    sys.exit(1)

# check configuration
try:
    if "timer" not in config or not 5 <= config["timer"] <= 60:
        logger.error("timer field not filled properly")
        sys.exit(1)
    if "log" not in config or not isinstance(config["log"], bool):
        logger.error("log field not filled properly")
        sys.exit(1)
    if "influxdb_url" not in config or not isinstance(config["influxdb_url"], str):
        logger.error("influxdb_url field not filled properly")
        sys.exit(1)
    if len(config["routers"]) == 0:
        logger.error("You need to configure at least one router")
        sys.exit(1)
    for router in config["routers"]:
        if "name" not in router or not isinstance(router["name"], str):
            logger.error("routers (name) field not filled properly")
            sys.exit(1)
        if "hop" not in router or not 1 <= router["hop"] <= 255:
            logger.error("routers (hop) field not filled properly")
            sys.exit(1)
        if "next_ip" not in router or not re.match(regex_ip, router["next_ip"]):
            logger.error("routers (next_ip) field not filled properly")
            sys.exit(1)
except Exception as e:
    logger.error("%s", e)
    sys.exit(1)

routers = []

for router in config["routers"]:
    routers.append(Router(router["name"], router["hop"], router["next_ip"], regex_ip, config["log"], config["influxdb_url"], config["timer"]))
    routers[-1].start()

