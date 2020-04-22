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

"""Console script for dispatcher."""
import asyncio
import os
import sys
import traceback

import click

from aiohttp import ClientSession
from pathlib import Path

from dispatcher.config import DispatcherGlobals, reset_config
from dispatcher.logic.dispatcher import Dispatcher
from dispatcher.utils.logger import get_logger
from dispatcher.utils.text_utils import Colors

logger = get_logger()


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


def process_config_file(config_filepath: Path):
    if config_filepath is None and not os.path.exists(DispatcherGlobals.CONFIG_FILENAME):
        logger.info("Config file doesn't exist")
        exit(1)
    config_filepath = config_filepath or Path(DispatcherGlobals.CONFIG_FILENAME)
    config_filepath = Path(config_filepath)
    reset_config(config_filepath)
    return config_filepath


async def main(config_file):

    config_file = process_config_file(config_file)

    async with ClientSession(raise_for_status=True) as session:
        try:
            dispatcher = Dispatcher(session, config_file)
        except ValueError as ex:
            print(f'{Colors.FAIL}Error configuring dispatcher: '
                  f'{Colors.BOLD}{str(ex)}{Colors.ENDC}')
            print(f'Try checking your config file located at {Colors.BOLD}'
                  f'{DispatcherGlobals.CONFIG_FILENAME}{Colors.ENDC}')
            return 1
        loop = asyncio.get_event_loop()
        await dispatcher.connect(loop)
        loop.close()

    return 0


@click.command(help="dispatcher")
@click.option("-c", "--config-file", default=None, help="Path to config ini file")
def run(config_file):
    logger = get_logger()
    try:
        exit_code = asyncio.run(main(config_file))
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
        raise
    sys.exit(exit_code)


if __name__ == '__main__':
    run()
