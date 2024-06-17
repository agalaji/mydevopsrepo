###############################################################################
# LEGALESE:   "Copyright (C) 2019-2021, Celestica Corp. All rights reserved." #
#                                                                             #
# This source code is confidential, proprietary, and contains trade           #
# secrets that are the sole property of Celestica Corp.                       #
# Copy and/or distribution of this source code or disassembly or reverse      #
# engineering of the resultant object code are strictly forbidden without     #
# the written consent of Celestica Corp.                                      #
#                                                                             #
###############################################################################

*** Settings ***
Documentation       This Suite will vMoonstonedate Sonic package

Library           MoonstoneSonicLib.py
Library           ../MOONSTONECommonLib.py
Library           CommonLib.py
Library           ../diag/MoonstoneDiagLib.py
Variables         ../MoonstoneCommonVariable.py
Variables         MoonstoneSonicVariable.py

Resource          MoonstoneSonicKeywords.resource
Resource	  CommonKeywords.resource

Suite Setup       Connect Device
Suite Teardown    Disconnect Device

*** Variables ***


*** Test Cases ***









*** Keywords ***
Connect Device
    Login Device

Disconnect Device
    Sonic Disconnect
