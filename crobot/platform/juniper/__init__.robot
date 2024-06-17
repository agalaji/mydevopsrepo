###############################################################################
# LEGALESE:   "Copyright (C) 2020-      Celestica Corp. All rights reserved." #
#                                                                             #
# This source code is confidential, proprietary, and contains trade           #
# secrets that are the sole property of Celestica Corp.                       #
# Copy and/or distribution of this source code or disassembly or reverse      #
# engineering of the resultant object code are strictly forbidden without     #
# the written consent of Celestica Corp.                                      #
#                                                                             #
###############################################################################

#*** Settings ***
#Documentation   juniper suite
#Force Tags      juniper
#Library         ../JuniperCommonLib.py
#
#Suite Setup     DiagOS Connect Device
#Suite Teardown  DiagOS Disconnect Device
#
#
#*** Keywords ***
#DiagOS Connect Device
#    DiagOSConnect
#
#DiagOS Disconnect Device
#    DiagOSDisconnect
