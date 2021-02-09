"""HPG Microwave Simulator

Usage:
    hpg simulator [options]
    hpg (-h | --help | -v | --version)

Connection Options:
    --host HOST             Host to connect to or listen on [default: 127.0.0.1]
    --port PORT             Port to connect to or listen on [default: 5025]

Misc Options:
    -h --help                 Show this screen.
    -v --version              Show version.
    --loglevel LEVEL          Set a specific log level. [default: DEBUG]

"""

VERSION = '1.2.0'

### coding=utf-8 ###
import signal
from .Client import Client
from .Simulator import Simulator
from pyfiglet import Figlet

### docopt ###
from docopt import docopt
arguments = docopt(__doc__, version=VERSION)

### logging ###
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=getattr(logging, arguments['--loglevel'])
)
logger = logging.getLogger('HPG')

if __name__ == '__main__':
    
    if arguments['simulator']:
        figlet = Figlet(font='slant')
        print(figlet.renderText('HPG Simulator'))
        simulator = Simulator(arguments['--host'], int(arguments['--port']))
        simulator.logger.setLevel(arguments['--loglevel'])
        signal.pause()
