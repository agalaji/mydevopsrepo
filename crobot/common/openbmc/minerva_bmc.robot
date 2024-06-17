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
#######################################################################################################################
# Script       : minerva_bmc.robot                                                                                    #
# Date         : 15 March, 2024                                                                                       #
# Author       : Harish Kumar P <hkumar@celestica.com>                                                                #
# Description  : This script will validate openbmc                                                                    #
#                                                                                                                     #
# Script Revision Details:                                                                                            #
#   1.0 Final Minerva scripts after EVT                                                                                   #  
#######################################################################################################################

*** Settings ***
Documentation       Tests to verify OpenBMC functions described in the OpenBMC function SPEC for the project Minerva.

# Force Tags        openbmc
Library           OpenBmcLibAdapter.py
Library           openbmc_lib.py
Variables         Openbmc_variable.py
Resource          Openbmc_keywords.robot
Resource          CommonResource.robot

Suite Setup       Bmc Connect Device
Suite Teardown    Bmc Disconnect Device

*** Test Cases ***

FB_BMC_COMM_TC_003_Online_Update_BMC_in_BMC_OS 
    [Documentation]  This test checks the BMC FW programming functions by updating the BMC FW in BMC OS
    [Tags]     common  FB_BMC_COMM_TC_003_Online_Update_BMC_in_BMC_OS  minerva
    [Timeout]  150 min 00 seconds
    [Setup]    prepare BMC images
    Sub-Case  FB_BMC_COMM_TC_003_1  upgrade master bmc and check version
    Sub-Case  FB_BMC_COMM_TC_003_2  prepare BMC images
    Sub-Case  FB_BMC_COMM_TC_003_3  downgrade master bmc and check version
    Sub-Case  FB_BMC_COMM_TC_003_4  prepare BMC images
    Sub-Case  FB_BMC_COMM_TC_003_5  upgrade master bmc and check version
    [Teardown]  clean images  DUT  BMC

FB_BMC_COMM_TC_004_Online_Update_BIOS_in_BMC_OS 
    [Documentation]  This test checks the BMC FW programming functions by updating the BIOS FW in BMC OS
    [Tags]     common  FB_BMC_COMM_TC_004_Online_Update_BIOS_in_BMC_OS  minerva
    [Timeout]  150 min 00 seconds
    [Setup]    prepare BIOS images
    Sub-Case  FB_BMC_COMM_TC_004_1  upgrade master bios lite and check version
    Sub-Case  FB_BMC_COMM_TC_004_2  prepare BIOS images
    Sub-Case  FB_BMC_COMM_TC_004_3  downgrade master bios lite and check version
    Sub-Case  FB_BMC_COMM_TC_004_4  prepare BIOS images
    Sub-Case  FB_BMC_COMM_TC_004_5  upgrade master bios lite and check version
    [Teardown]  clean images  DUT  BIOS

FB_BMC_COMM_TC_005_Online_Update_COMe_CPLD_In_BMC_OS
   [Documentation]  This test checks the BMC FW programming functions by updating the COMe CPLD in BMC OS
   [Tags]     common  FB_BMC_COMM_TC_005_Online_Update_COMe_CPLD_In_BMC_OS  minerva  critical
   [Timeout]  30 min 00 seconds
   [Setup]    prepare COME_CPLD images
   Sub-Case  FB_BMC_COMM_TC_005_1  COMe CPLD upgrade and check CPLD version
   Sub-Case  FB_BMC_COMM_TC_005_2  COMe CPLD downgrade and check CPLD version
   Sub-Case  FB_BMC_COMM_TC_005_3  COMe CPLD upgrade and check CPLD version
   [Teardown]  clean come images and script

FB_BMC_COMM_TC_006_Online_Update_IOB_FPGA_In_BMC_OS
   [Documentation]  This test checks the BMC FW programming functions by updating the IOB FPGA in BMC OS
   [Tags]     common  FB_BMC_COMM_TC_006_Online_Update_IOB_FPGA_In_BMC_OS  minerva  critical
   [Timeout]  70 min 00 seconds
   [Setup]    prepare FPGA images
   Sub-Case  FB_BMC_COMM_TC_006_1  prepare iob_update.sh script
   Sub-Case  FB_BMC_COMM_TC_006_2  FPGA upgrade lite and check FPGA version
   Sub-Case  FB_BMC_COMM_TC_006_3  prepare FPGA images
   Sub-Case  FB_BMC_COMM_TC_006_4  FPGA downgrade lite and check FPGA version
   Sub-Case  FB_BMC_COMM_TC_006_5  prepare FPGA images
   Sub-Case  FB_BMC_COMM_TC_006_6  FPGA upgrade lite and check FPGA version
   Sub-Case  FB_BMC_COMM_TC_006_7  clean iob_update.sh script
   [Teardown]  clean images  DUT  FPGA

FB_BMC_COMM_TC_007_Backup_BMC_Manual_Booting_Test 
    [Documentation]  This test checks BMC can boot from slave by command
    [Tags]     common  FB_BMC_COMM_TC_007_Backup_BMC_Manual_Booting_Test  minerva
    [Timeout]  25 min 00 seconds
    Sub-Case  FB_BMC_COMM_TC_007_1   check current openbmc is booted from master
    Sub-Case  FB_BMC_COMM_TC_007_2   switch bmc flash to Slave then to Master
    [Teardown]  switch bmc flash to Master

FB_BMC_COMM_TC_009_BMC_Network_Config_Test 
    [Documentation]  This test checks BMC port could communicate with CPU and Terminal PC with IPv6
    [Tags]     common  FB_BMC_COMM_TC_009_BMC_Network_Config_Test  minerva
    [Timeout]  10 min 00 seconds
    [Setup]  go to openbmc
    Sub-Case  FB_BMC_COMM_TC_009_1  reboot and check dhcp setting info and check ipv6 address lite
    Sub-Case  FB_BMC_COMM_TC_009_2  ping dhcp server with eth0
    Sub-Case  FB_BMC_COMM_TC_009_3  using scp command to copy file from BMC to CPU by eth0 ipv6 lite
    [Teardown]  clean up file on both bmc and cpu

FB_BMC_COMM_TC_011_IPv6_Ping_Test
    [Documentation]  This test verifies if ping could be executed successfully
    [Tags]     common  FB_BMC_COMM_TC_011_IPv6_Ping_Test  minerva
    [Timeout]  10 min 00 seconds
    Sub-Case  FB_BMC_COMM_TC_011_1  verify bmc ipv6 address
    Sub-Case  FB_BMC_COMM_TC_011_2  ping dhcp server with eth0
    Sub-Case  FB_BMC_COMM_TC_011_3  ping openbmc from dhcp server

FB_BMC_COMM_TC_012_IPv6_SSH_Test
    [Documentation]  This test verifies if SSH could be executed successfully
    [Tags]     common  FB_BMC_COMM_TC_012_IPv6_SSH_Test  minerva
    [Timeout]  10 min 00 seconds
    Sub-Case  FB_BMC_COMM_TC_012_1  verify bmc ipv6 address
    Sub-Case  FB_BMC_COMM_TC_012_2  ssh dhcp server from openbmc
    Sub-Case  FB_BMC_COMM_TC_012_3  ssh openbmc from dhcp server

FB_BMC_COMM_TC_013_Internal_USB_Network_Check 
    [Documentation]  This test checks the internal usb network between CPU and BMC
    [Tags]     common  FB_BMC_COMM_TC_013_Internal_USB_Network_Check  minerva
    [Timeout]  5 min 00 seconds
    Sub-Case  FB_BMC_COMM_TC_013_1  Check usb0 ipv6 address&mac&ping function
    Sub-Case  FB_BMC_COMM_TC_013_2  Using scp command to copy file from BMC to CPU by usb0 ipv6 new
    [Teardown]    clean up file on both bmc and cpu

FB_BMC_COMM_TC_014_OpenBMC_MAC_Address_Test 
    [Documentation]  This test checks the BMC MAC address
    [Tags]     common  FB_BMC_COMM_TC_014_OpenBMC_MAC_Address_Test  minerva
    [Timeout]  50 min 00 seconds
    [Setup]    prepare openbmc lite mac global variable  ${smb_eeprom_path}
    Sub-Case  FB_BMC_COMM_TC_014_1  Check OpenBMC MAC address
    Sub-Case  FB_BMC_COMM_TC_014_2  Use unidiag tool to Update OpenBMC MAC address minerva
    Sub-Case  FB_BMC_COMM_TC_014_3  Reset openbmc lite os to check mac address
    Sub-Case  FB_BMC_COMM_TC_014_4  Power cycle chassis lite to check mac address
    Sub-Case  FB_BMC_COMM_TC_014_5  Use unidiag tool to Update OpenBMC MAC address back to previous value minerva
    Sub-Case  FB_BMC_COMM_TC_014_6  Reset openbmc lite os to check mac address again
    [Teardown]  Run Keyword If Test Failed  restore eeprom lite and clean up files  chassis_eeprom  ${smb_bin_name}  ${smb_eeprom_path}  ${smb_eeprom_product_name}  ${disable_write_protection}  ${enable_write_protection}

FB_BMC_COMM_TC_015_Power_Control 
    [Documentation]  This test verifies BMC can correctly control the system power to different states: power on, power off, power cycle, reset
    [Tags]     common  FB_BMC_COMM_TC_015_Power_Control  minerva
    [Timeout]  40 min 00 seconds
    Sub-Case  FB_BMC_COMM_TC_015_1  chassis power cycle dut and check power status
    Sub-Case  FB_BMC_COMM_TC_015_2  run all the parameters of version utility lite
    Sub-Case  FB_BMC_COMM_TC_015_3  check power status and ping test
    Sub-Case  FB_BMC_COMM_TC_015_4  power off dut and ping test
    Sub-Case  FB_BMC_COMM_TC_015_5  power on dut and check the power status
    Sub-Case  FB_BMC_COMM_TC_015_6  ping cpu from bmc test
    Sub-Case  FB_BMC_COMM_TC_015_7  power reset cpu and check only cpu be reset
    [Teardown]  Run Keyword If Test Failed  set power on chassis

FB_BMC_COMM_TC_016_OpenBMC_Reset_Test 
    [Documentation]  This test verifies BMC can reboot successfully without any impact on COM-e
    [Tags]     common  FB_BMC_COMM_TC_016_OpenBMC_Reset_Test  minerva
    [Timeout]  30 min 00 seconds
    Sub-Case  FB_BMC_COMM_TC_016_1  check master openbmc and check com-e side
    [Teardown]  switch bmc flash to Master and change dir to default

FB_BMC_COMM_TC_017_SMB_FRU2_EEPROM_R/W_Test
    [Documentation]  This test verifies SMB EEPROM could be R/W successfully
    [Tags]     common  FB_BMC_COMM_TC_017_SMB_FRU2_EEPROM_R/W_Test  minerva
    [Timeout]  30 min 00 seconds
    [Setup]  prepare store eeprom lite  ${smb_eeprom_path}
    Sub-Case  FB_BMC_COMM_TC_017_1  run command to read smb eeprom minerva
    Sub-Case  FB_BMC_COMM_TC_017_2  run command to write and read smb eeprom minerva
    Sub-Case  FB_BMC_COMM_TC_017_3  reset bmc and read smb eeprom minerva
    Sub-Case  FB_BMC_COMM_TC_017_4  chassis power cycle and read smb eeprom minerva
    Sub-Case  FB_BMC_COMM_TC_017_5  run command to write and read smb eeprom with different data minerva
    Sub-Case  FB_BMC_COMM_TC_017_6  reset bmc and read smb eeprom with different data minerva
    [Teardown]  restore eeprom lite and clean up files  chassis_eeprom  ${smb_bin_name}  ${smb_eeprom_path}  ${smb_eeprom_product_name}  ${disable_write_protection}  ${enable_write_protection}

FB_BMC_COMM_TC_018_Restful_fruid_test 
    [Documentation]  This test verifies fru data can be read through Restful
    [Tags]     common  FB_BMC_COMM_TC_018_Restful_fruid_test  minerva
    [Timeout]  10 min 00 seconds
    [Setup]  set time delay  90
    Sub-Case  FB_BMC_COMM_TC_018_1  check ipv4 address for bmc and cpu
    Sub-Case  FB_BMC_COMM_TC_018_2  read restful fruid via ipv4 lite
    Sub-Case  FB_BMC_COMM_TC_018_3  check ipv6 address for bmc and cpu
    Sub-Case  FB_BMC_COMM_TC_018_4  read restful fruid via ipv6 lite
    Sub-Case  FB_BMC_COMM_TC_018_5  compare restful fruid with fru data dumped in bmc os lite

FB_BMC_COMM_TC_019_Restful_BMC_Test 
    [Documentation]  This test verifies BMC info can be read through Restful
    [Tags]     common  FB_BMC_COMM_TC_019_Restful_BMC_Test  minerva
    [Timeout]  10 min 00 seconds
    [Setup]  set time delay  90
    Sub-Case  FB_BMC_COMM_TC_019_1  check ipv6 address for bmc and cpu
    Sub-Case  FB_BMC_COMM_TC_019_2  read restful bmc info via ipv6
    Sub-Case  FB_BMC_COMM_TC_019_3  compare bmc info dumped in cpu os

FB_BMC_COMM_TC_020_Redfish_Endpoint_Test 
    [Documentation]  This test verifies BMC info can be read through Redfish
    [Tags]     common  FB_BMC_COMM_TC_020_Redfish_Endpoint_Test  minerva
    [Timeout]  10 minutes 00 seconds
    [Setup]   set time delay  5
    Sub-Case  FB_BMC_COMM_TC_020_1  read redfish chassis info
    Sub-Case  FB_BMC_COMM_TC_020_2  read redfish system info

FB_BMC_COMM_TC_021_weutil_Test 
    [Documentation]  This test verifies the utility could be executed successfully
    [Tags]     common  FB_BMC_COMM_TC_021_weutil_Test  minerva
    [Timeout]  10 min 00 seconds
    Sub-Case  FB_BMC_COMM_TC_021_1  run weutil command
    Sub-Case  FB_BMC_COMM_TC_021_2  check smb fru data match with eeprom tool minerva

FB_BMC_COMM_TC_022_Tftp_Client_Tool_Test
    [Documentation]  This test verifies the tftp tool could be executed successfully to download file
    [Tags]     common  FB_BMC_COMM_TC_022_Tftp_Client_Tool_Test  minerva
    [Timeout]  10 min 00 seconds
    [Setup]  check file size on tftp server
    Sub-Case  FB_BMC_COMM_TC_022_1  copy the image file from tftp server and check size
    [Teardown]  clean up file  DUT  ${tftp_file_test}

FB_BMC_COMM_TC_023_Get_Device_ID
    [Documentation]  This test verifies the generic OpenBMC info can be got correctly,
                     ...  including OpenBMC version, manufacture ID and product ID
    [Tags]     common  FB_BMC_COMM_TC_023_Get_Device_ID  minerva
    [Timeout]  40 min 00 seconds
    Sub-Case  FB_BMC_COMM_TC_023_1  run ipmi command "get device id" to get openbmc info in master openbmc
    # Sub-Case  FB_BMC_COMM_TC_023_2  run ipmi command "get device id" to get openbmc info in slave openbmc
    [Teardown]  switch bmc flash to Master

FB_BMC_COMM_TC_025_Get_Board_ID
    [Documentation]  This test verifies the command can response the correct board id information
    [Tags]     common  FB_BMC_COMM_TC_025_Get_Board_ID  minerva
    [Timeout]  2 min 00 seconds
    Sub-Case  FB_BMC_COMM_TC_25_1  get board name via command "wedge_board_type"

FB_BMC_COMM_TC_027_OpenBMC_Memory_Test
    [Documentation]  This test verifies OpenBMC Memory can be R/W without any error
    [Tags]     common  FB_BMC_COMM_TC_027_OpenBMC_Memory_Test  minerva
    [Timeout]  30 min 00 seconds
    [Setup]  prepare MEM_TEST images
    Sub-Case  FB_BMC_COMM_TC_027_1  get memory information lite
    Sub-Case  FB_BMC_COMM_TC_027_2  assign memory size to run memory rw test with tool memtester
    [Teardown]  clean memtest script and change dir

FB_BMC_COMM_TC_028_SOL_Test
    [Documentation]  This test verifies BMC can access COMe through SOL
    [Tags]     common  FB_BMC_COMM_TC_028_SOL_Test  minerva
    [Timeout]  10 min 00 seconds
    [Setup]    go to openbmc
    Sub-Case  FB_BMC_COMM_TC_028_1  run command to verify sol test

FB_BMC_COMM_TC_029_CPLD_Register_R/W_Test
    [Documentation]  This test verifies the SCM CPLD REG could be RW successfully
    [Tags]     common  FB_BMC_COMM_TC_029_CPLD_Register_R/W_Test  minerva
    [Timeout]  15 min 00 seconds
    Sub-Case  FB_BMC_COMM_TC_029_1  run command "wedge_power.sh status"
    Sub-Case  FB_BMC_COMM_TC_029_2  run command to read/write smb cpld reg to power off com-e
    Sub-Case  FB_BMC_COMM_TC_029_3  run command to read/write smb cpld reg to power on com-e
    [Teardown]  Run Keyword If Test Failed  set power on chassis

FB_BMC_COMM_TC_030_TPM_Test
    [Documentation]  This test verifies TPM test
    [Tags]     common  FB_BMC_COMM_TC_030_TPM_Test  minerva
    [Timeout]  30 min 00 seconds
    [Setup]  prepare images  TPM
    Sub-Case  FB_BMC_COMM_TC_030_1  run tpm script
    [Teardown]  clean tmp script and change dir

FB_BMC_COMM_TC_031_CIT_Test
    [Documentation]  This test verifies CIT Test
    [Tags]     common  FB_BMC_COMM_TC_031_CIT_Test  minerva
    [Timeout]  60 min 00 seconds
    [Setup]  prepare CIT scripts and check pem presence
    Sub-Case  FB_BMC_COMM_TC_031_1  install and run cit test minerva
    [Teardown]  clean cit script and change dir

FB_BMC_COMM_TC_040_COMe_Mac_Address_Check_Test
    [Documentation]  This test verifies COMe side mac address Test
    [Tags]     common  FB_BMC_COMM_TC_040_COMe_Mac_Address_Check_Test  minerva
    [Timeout]  5 min 00 seconds
    [Setup]    go to openbmc
    Sub-Case  FB_BMC_COMM_TC_040_1  check come side mac address
    [Teardown]  change dir

FB_BMC_TC_041_otp_util_Test
    [Documentation]  This test verifies otp util Test
    [Tags]     common  FB_BMC_TC_041_otp_util_Test  minerva
    [Timeout]  20 min 00 seconds
    [Setup]    switch bmc flash to Master
    Sub-Case  FB_BMC_TC_041_1  check bmc auto boot test
    [Teardown]  change dir


*** Keywords ***
Bmc Connect Device
    BmcConnect

Bmc Disconnect Device
    BmcDisconnect


