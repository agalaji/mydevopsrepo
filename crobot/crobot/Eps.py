###############################################################################
# LEGALESE:   "Copyright (C) 2019-2020, Celestica Corp. All rights reserved." #
#                                                                             #
# This source code is confidential, proprietary, and contains trade           #
# secrets that are the sole property of Celestica Corp.                       #
# Copy and/or distribution of this source code or disassembly or reverse      #
# engineering of the resultant object code are strictly forbidden without     #
# the written consent of Celestica Corp.                                      #
#                                                                             #
###############################################################################
import TelnetDevice

class Eps(TelnetDevice):

    def __init__(self, epsDict):
        super().__init__()
        self.userName = epsDict['userName']
        self.password = epsDict['password']
        self.managementIP = epsDict['managementIP']
