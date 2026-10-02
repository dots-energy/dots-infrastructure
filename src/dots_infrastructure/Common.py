import time

import helics as h

def destroy_federate(fed):
    h.helicsFederateDisconnect(fed)
    while h.HelicsFederateState.FINALIZE != h.helicsFederateGetState(fed):
        time.sleep(0.1)
    h.helicsFederateDestroy(fed)