# -*- coding: utf-8 -*-

# Copyright (C) 2019  Infobyte LLC (http://www.infobytesec.com/)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import json

import asyncio

from dispatcher.config import instance as config, reset_config, Sections, control_config
from dispatcher.logic.line_processor import StdErrLineProcessor, StdOutLineProcessor
from dispatcher.models.executor import Executor
from dispatcher.utils.logger import get_logger, setup_logging


logger = get_logger()
setup_logging()


class Dispatcher:

    def __init__(self, session, config_path=None):
        reset_config(filepath=config_path)
        try:
            control_config()
        except ValueError as e:
            logger.error(e)
            raise e
        self.config_path = config_path
        self.host = config.get(Sections.SERVER, "host")
        self.port = config.get(Sections.SERVER, "port")
        self.agent_name = config.get(Sections.AGENT, "agent_name")
        self.session = session
        executors_list_str = config[Sections.AGENT].get("executors", []).split(",")
        if "" in executors_list_str:
            executors_list_str.remove("")
        self.executors = {
            executor_name:
                Executor(executor_name, config) for executor_name in executors_list_str
        }

    def write(self, data: dict):
        data = json.dumps(data).encode() + b'\n'
        self.writer.write(data)

    async def read(self) -> dict:
        data = await self.reader.readline()
        logger.info('Parsing data: %s', data)
        return json.loads(data.decode())

    async def connect(self, loop):

        connected_data = {
                    'action': 'JOIN',
                    'name': self.agent_name,
                    'executors': [{"name": executor.name, "args": executor.params}
                                  for executor in self.executors.values()]
                }

        self.reader, self.writer = await asyncio.open_connection(self.host, 8888, loop=loop)
        self.write(connected_data)
        logger.info("Connection to server succeeded")

        await self.run_await()  # This line can we called from outside (in main)

    async def run_await(self):
        while True:
            data = await self.read()
            asyncio.create_task(self.run_once(data))

    async def run_once(self, data: dict = None):
        if "action" not in data:
            logger.info("Data not contains action to do")
            self.write({"error": "'action' key is mandatory in this websocket connection"})
            return

        if data["action"] not in ["RUN"]:  # ONLY SUPPORTED COMMAND FOR NOW
            logger.info("Unrecognized action")
            self.write({f"{data['action']}_RESPONSE": "Error: Unrecognized action"})
            return

        if data["action"] == "RUN":
            if "code_executor" not in data:
                logger.error("No executor selected")
                self.write(
                    {
                        "action": "RUN_STATUS",
                        "running": False,
                        "message": f"No executor selected to {self.agent_name} agent"
                    }
                )
                return

            if data["code_executor"] not in self.executors:
                logger.error("The selected executor not exists")
                self.write(
                    {
                        "action": "RUN_STATUS",
                        "executor_name": data["code_executor"],
                        "running": False,
                        "message": f"The selected executor {data['code_executor']} not exists in {self.agent_name} "
                                   f"agent"
                    }
                )
                return

            executor = self.executors[data["code_executor"]]

            config_params = list(executor.params.keys()).copy()
            passed_params = data['args'] if 'args' in data else {}

            all_accepted = all(
                [
                    any([
                        param in passed_param           # Control any available param
                        for param in config_params      # was passed
                        ])
                    for passed_param in passed_params   # For all passed params
                ])
            if not all_accepted:
                logger.error("Unexpected argument passed to {} executor".format(executor.name))
                self.write(
                    {
                        "action": "RUN_STATUS",
                        "executor_name": executor.name,
                        "running": False,
                        "message": f"Unexpected argument(s) passed to {executor.name} executor from {self.agent_name} "
                                   f"agent"
                    }
                )
            mandatory_full = all(
                [
                    not executor.params[param]  # All params is not mandatory
                    or any([
                        param in passed_param for passed_param in passed_params  # Or was passed
                        ])
                    for param in config_params
                ]
            )
            if not mandatory_full:
                logger.error("Mandatory argument not passed to {} executor".format(executor.name))
                self.write(
                    {
                        "action": "RUN_STATUS",
                        "executor_name": executor.name,
                        "running": False,
                        "message": f"Mandatory argument(s) not passed to {executor.name} executor from "
                                   f"{self.agent_name} agent"
                    }
                )

            if mandatory_full and all_accepted:
                running_msg = f"Running {executor.name} executor from {self.agent_name} agent"
                logger.info("Running {} executor".format(executor.name))

                process = await self.create_process(executor, passed_params)
                tasks = [
                    StdOutLineProcessor(process, self.session).process_f(),
                    StdErrLineProcessor(process).process_f(),
                ]
                self.write(
                    {
                        "action": "RUN_STATUS",
                        "executor_name": executor.name,
                        "running": True,
                        "message": running_msg
                    }
                )
                await asyncio.gather(*tasks)
                await process.communicate()
                assert process.returncode is not None
                if process.returncode == 0:
                    logger.info("Executor {} finished successfully".format(executor.name))
                    self.write(
                        {
                            "action": "RUN_STATUS",
                            "executor_name": executor.name,
                            "successful": True,
                            "message": f"Executor {executor.name} from {self.agent_name} finished successfully"
                        }
                    )
                else:
                    logger.warning(
                        f"Executor {executor.name} finished with exit code {process.returncode}")
                    self.write(
                        {
                            "action": "RUN_STATUS",
                            "executor_name": executor.name,
                            "successful": False,
                            "message": f"Executor {executor.name} from {self.agent_name} failed"
                        }
                    )

    @staticmethod
    async def create_process(executor: Executor, args):
        env = os.environ.copy()
        if isinstance(args, dict):
            for k in args:
                env[f"EXECUTOR_CONFIG_{k.upper()}"] = str(args[k])
        else:
            logger.error("Args from data received has a not supported type")
            raise ValueError("Args from data received has a not supported type")
        for varenv, value in executor.varenvs.items():
            env[f"{varenv.upper()}"] = value
        process = await asyncio.create_subprocess_shell(
            executor.cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            limit=executor.max_size
            # If the config is not set, use async.io default
        )
        return process
