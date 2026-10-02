import time

import helics as h

def destroy_federate(fed):
    h.helicsFederateDisconnect(fed)
    h.helicsFederateDestroy(fed)
    while h.HelicsFederateState.FINISHED != h.helicsFederateGetState(fed):
        time.sleep(0.1)