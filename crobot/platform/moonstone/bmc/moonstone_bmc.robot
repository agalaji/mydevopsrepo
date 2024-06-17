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
# Script       : BMC.robot                                                                                            #
# Date         : July 29, 2020                                                                                        #
# Author       : James Shi <jameshi@celestica.com>                                                                    #
# Description  : This script will validate BMC                                                                        #
#                                                                                                                     #
# Script Revision Details:                                                                                            #
#   Initial Draft for bmc testing                                                                                      #
#######################################################################################################################

*** Settings ***
Documentation       Tests to verify BMC functions described in the BMC function SPEC for the Moonstone project.

# Force Tags        BMC
Variables         MoonstoneBMCVariable.py
Library           ../MOONSTONECommonLib.py
Library           MoonstoneBMCLib.py
#Library           bios_menu_lib.py
Resource          MoonstoneBMCkeywords.robot
Resource          CommonResource.robot

Suite Setup       DIAG OS Connect 
Suite Teardown    DIAG OS Disconnect 
** Variables ***
# It is recommended to use <{ScriptName}|{FeatureName}|{DomainName}_Variable> file for variable declaration with help of
# setting table. This section should keep blank.
#In extreme case if script requires variable then it should be defined in this table with documentaiton tag

*** Test Cases ***
# *** comment ***

MOONSTONE_BMC_Device_Info_Check_Test
    [Documentation]  Test to verify BMC device info
    [Tags]  MOONSTONE_BMC_Device_Info_Check_Test  Moonstone  OPEN_BMC
    Step  1  check bmc version info  DUT
    Step  2  bmc reset  DUT  cold
    Step  3  check bmc version info  DUT
   

MOONSTONE_BMC_Lan_Communication_Test
    [Documentation]  To verify if the LAN interface can be configured through device.
    [Tags]     MOONSTONE_BMC_Lan_Communication_Test  smoke  Moonstone  OPEN_BMC
    Step  1  check_lan_print_info  DUT  exp_ip_addr=${mgmt_ip}  exp_ip_status=${dhcp_add}  exp_subnet_mask=${net_mask}
    Step  2  start ping bmc ip  DUT  ${mgmt_ip}
    Step  3  set power cycle  DUT
    Step  4  check ping bmc ip  DUT 
    Step  5  check_lan_print_info  DUT  exp_ip_addr=${mgmt_ip}  exp_ip_status=${dhcp_add}  exp_subnet_mask=${net_mask}
    Step  6  set_bmc_ip_status  DUT  static
    Step  7  set_bmc_ip_netmask  DUT  ipaddr=${set_bmc_ipaddr}  netmask=${set_bmc_netmask}
    Step  8  check_lan_print_info  DUT  exp_ip_addr=${set_bmc_ipaddr}  exp_subnet_mask=${set_bmc_netmask}  exp_ip_status=${static_add}
    Step  9  start ping bmc ip  DUT  ${set_bmc_ipaddr}
    Step  10  set power cycle  DUT
    Step  11  check ping bmc ip  DUT 
    Step  12  check_lan_print_info  DUT  exp_ip_addr=${set_bmc_ipaddr}  exp_subnet_mask=${set_bmc_netmask}  exp_ip_status=${static_add}
    Step  13  set_bmc_ip_status  DUT  static
    Step  14  set_bmc_ip_netmask  DUT  ipaddr=${set_bmc_ipaddr_2}  netmask=${set_bmc_netmask}
    Step  15  check_lan_print_info  DUT  exp_ip_addr=${set_bmc_ipaddr_2}  exp_subnet_mask=${set_bmc_netmask}  exp_ip_status=${static_add}
    Step  16  start ping bmc ip  DUT  ${set_bmc_ipaddr_2}
    Step  17  set power cycle  DUT
    Step  18  check ping bmc ip  DUT 
    Step  19  check_lan_print_info  DUT  exp_ip_addr=${set_bmc_ipaddr_2}  exp_subnet_mask=${set_bmc_netmask}  exp_ip_status=${static_add}
    Step  20  set_bmc_ip_status  DUT  dhcp
    Step  21  check_lan_print_info  DUT  exp_ip_addr=${mgmt_ip}  exp_ip_status=${dhcp_add}  exp_subnet_mask=${net_mask}
    Step  22  start ping bmc ip  DUT  ${mgmt_ip}
    Step  23  set power cycle  DUT
    Step  24  check ping bmc ip  DUT 
    Step  25  check_lan_print_info  DUT  exp_ip_addr=${mgmt_ip}  exp_ip_status=${dhcp_add}  exp_subnet_mask=${net_mask}
    [Teardown]  Run Keyword If Test Failed  set_bmc_ip_status  DUT  dhcp


MOONSTONE_BMC_Lan_Configuration_Test
    [Documentation]  To verify if the LAN interface can be configured through server.
    [Tags]     MOONSTONE_BMC_Lan_Configuration_Test  smoke  Moonstone  OPEN_BMC
    Step  1  check_lan_print_info  DUT  exp_ip_addr=${mgmt_ip}  exp_ip_status=${dhcp_add}  exp_subnet_mask=${net_mask}
    Step  2  bmc reset  DUT  cold
    Step  3  check_lan_print_info  DUT  exp_ip_addr=${mgmt_ip}  exp_ip_status=${dhcp_add}  exp_subnet_mask=${net_mask}
    Step  4  set_bmc_ip_status  DUT  static
    Step  5  set_bmc_ip_netmask  DUT  ipaddr=${set_bmc_ipaddr}  netmask=${set_bmc_netmask}
    Step  6  check_lan_print_info  DUT  exp_ip_addr=${set_bmc_ipaddr}  exp_subnet_mask=${set_bmc_netmask}  exp_ip_status=${static_add}
    Step  7  bmc reset  DUT  cold
    Step  8  check_lan_print_info  DUT  exp_ip_addr=${set_bmc_ipaddr}  exp_subnet_mask=${set_bmc_netmask}  exp_ip_status=${static_add}
    Step  9  set_bmc_ip_status  DUT  static
    Step  10  set_bmc_ip_netmask  DUT  ipaddr=${set_bmc_ipaddr_2}  netmask=${set_bmc_netmask}
    Step  11  check_lan_print_info  DUT  exp_ip_addr=${set_bmc_ipaddr_2}  exp_subnet_mask=${set_bmc_netmask}  exp_ip_status=${static_add}
    Step  12  bmc reset  DUT  cold
    Step  13  check_lan_print_info  DUT  exp_ip_addr=${set_bmc_ipaddr_2}  exp_subnet_mask=${set_bmc_netmask}  exp_ip_status=${static_add}
    Step  14  set_bmc_ip_status  DUT  dhcp
    Step  15  check_lan_print_info  DUT  exp_ip_addr=${mgmt_ip}  exp_ip_status=${dhcp_add}  exp_subnet_mask=${net_mask}
    Step  16  bmc reset  DUT  cold
    Step  17  check_lan_print_info  DUT  exp_ip_addr=${mgmt_ip}  exp_ip_status=${dhcp_add}  exp_subnet_mask=${net_mask}
    [Teardown]  Run Keyword If Test Failed  set_bmc_ip_status  DUT  dhcp



MOONSTONE_BMC_KCS_Interface_Test
    [Documentation]  To verify KCS interfaces and communication via KCS from BMC to BIOS.
    [Tags]  MOONSTONE_BMC_KCS_Interface_Test  Moonstone  OPEN_BMC
    Step  1  set_modprobe  DUT
    Step  2  initialize_kcs_interface  DUT 
    Step  3  check_bmc_version_info  DUT
    Step  4  check_lan_print_info  DUT  exp_ip_addr=${mgmt_ip}  exp_ip_status=${dhcp_add}  exp_subnet_mask=${net_mask}  exp_mac_addr=${mac_addr}
    Step  5  clear_sel_list  DUT
    Step  6  boot_bios_through_ipmitool_raw  DUT


MOONSTONE_BMC_SSH_Login_Test
    [Documentation]  To verify ssh login of device
    [Tags]  MOONSTONE_BMC_SSH_Login_Test  Moonstone  OPEN_BMC
    Step  1  ssh_into_moonstone_device  DUT  ${mgmt_ip}  ${bmc_user}  ${bmc_pass}  ${bmc_prompt}
    [Teardown]  Run Keyword If Test Failed  exit_from_moonstone_device  DUT


MOONSTONE_BMC_Reset_Stress_Test
    [Documentation]  Test to Stress BMC Reset
    [Tags]  MOONSTONE_BMC_Reset_Stress_Test  Stress_Test  Moonstone  OPEN_BMC
    FOR    ${INDEX}    IN RANGE    1    11
          Step  1  check bmc version info  DUT
          Step  2  bmc reset  DUT  cold
          Step  3  check bmc version info  DUT
    END

MOONSTONE_BMC_Channel_Check
    [Documentation]  To verify the BMC channel info is correct
    [Tags]  MOONSTONE_BMC_Channel_Check  Moonstone  OPEN_BMC
    Step  1  check bmc channel info  DUT  0x00
    Step  2  check bmc channel info  DUT  0x01
    Step  3  check bmc channel info  DUT  0x0f
    Step  4  check server moonstone  DUT  ${scp_ip}  ${scp_username}  ${scp_password}  ${dhcp_prompt}
    Step  5  check bmc version info  DUT  lanplus=True
    Step  6  exit the server  DUT
    [Teardown]  Run Keyword If Test Failed  exit the server  DUT



MOONSTONE_BMC_Dependent_Image_Check
    [Documentation]  1.1.1 Dependent Image Check
    [Tags]     MOONSTONE_BMC_Dependent_Image_Check  Moonstone  OPEN_BMC
    Step  1  verify dependent image using diag


MOONSTONE_BMC_LAN_Interface_Stress_Test
    [Documentation]  Test to Stress LAN Interface
    [Tags]  MOONSTONE_BMC_LAN_Interface_Stress_Test  Stress_Test  Moonstone  OPEN_BMC
    Step  1  check server moonstone  DUT  ${scp_ip}  ${scp_username}  ${scp_password}  ${dhcp_prompt}
    Step  2  check lan interface stress test  DUT
    Step  3  exit the server  DUT
    [Teardown]  Run Keyword If Test Failed  exit the server  DUT


MOONSTONE_BMC_KCS_Interface_Stress_Test
    [Documentation]  Test to Stress KCS Interface
    [Tags]  MOONSTONE_BMC_KCS_Interface_Stress_Test  Stress_Test  Moonstone  OPEN_BMC
    Step  1  check kcs interface stress test  DUT
    [Teardown]  Run Keyword If Test Failed  exit the server  DUT


MOONSTONE_BMC_CHASSIS_POWER_TEST
    [Documentation]  To verify power chassis test using ipmitool
    [Tags]  MOONSTONE_BMC_CHASSIS_POWER_TEST  Moonstone  OPEN_BMC
    Step  1  check power chasis status  DUT  on
    Step  2  set power chasis  DUT  off
    Step  3  check power chasis status  DUT  off
    Step  4  set power chasis  DUT  on
    Step  5  check power chasis status  DUT  on
    Step  6  set power chasis  DUT  cycle
    Step  7  check power chasis status  DUT  on
    Step  8  set power chasis  DUT  reset
    Step  9  check power chasis status  DUT  on
    [Teardown]  Run Keyword If Test Failed  set power chasis  DUT  on

MOONSTONE_BMC_Online_Update_Test_BMC_Console
    [Documentation]  2.1.2  To verify online update of image through BMC Console
    [Tags]     MOONSTONE_BMC_Online_Update_Test_BMC_Console  Moonstone  OPEN_BMC
    Step  1  check server moonstone  DUT  ${scp_ip}  ${scp_username}  ${scp_password}  ${dhcp_prompt}
    Step  2  check_bmc_firmware_revision  DUT  ${moonstone_bmc_firmware_revision}  lanplus=True
    Step  3  update_primary_bmc  DUT  ${moonstone_bmc_old_img}
    Step  4  check_bmc_firmware_revision  DUT  ${moonstone_bmc_firmware_revision_old}  lanplus=True
    Step  5  update_primary_bmc  DUT  ${moonstone_bmc_new_img}
    Step  6  check_bmc_firmware_revision  DUT  ${moonstone_bmc_firmware_revision}  lanplus=True
    Step  7  exit the server  DUT
    [Teardown]  Run Keyword If Test Failed  exit the server  DUT
    

MOONSTONE_BMC_Online_Update_Stress_Test_BMC_Console
    [Documentation]  3.1.1  To verify bmc update stress test
    [Tags]     MOONSTONE_BMC_Online_Update_Stress_Test_BMC_Console  Stress_Test  Moonstone  OPEN_BMC
    FOR    ${INDEX}    IN RANGE    1    11
        Step  1  check server moonstone  DUT  ${scp_ip}  ${scp_username}  ${scp_password}  ${dhcp_prompt}
        Step  2  check_bmc_firmware_revision  DUT  ${moonstone_bmc_firmware_revision}  lanplus=True
        Step  3  update_primary_bmc  DUT  ${moonstone_bmc_old_img}
        Step  4  check_bmc_firmware_revision  DUT  ${moonstone_bmc_firmware_revision_old}  lanplus=True
        Step  5  update_primary_bmc  DUT  ${moonstone_bmc_new_img}
        Step  6  check_bmc_firmware_revision  DUT  ${moonstone_bmc_firmware_revision}  lanplus=True
        Step  7  exit the server  DUT
    END
    [Teardown]  Run Keyword If Test Failed  exit the server  DUT


# Commeting this as this is having open sw issue
# MOONSTONE_BMC_Bios_Update_Test_Via_BMC_Console
    # [Documentation]   2.14.3.3 To verify BIOS can be online updated successfully via BMC console
    # [Tags]   MOONSTONE_BMC_Bios_Update_Test_Via_BMC_Console  Moonstone  OPEN_BMC
    # Step  1  downgrade primary bios image through bmc console
    # Step  2  upgrade primary bios image through bmc console
    # [Teardown]  Run Keyword If Test Failed  switch cpu  DUT


*** Keywords ***
OS Connect Device
    ConnectESMB

OS Disconnect Device
    OSDisconnect

