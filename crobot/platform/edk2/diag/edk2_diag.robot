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

*** Settings ***
Documentation   EDK2 common diagnostic suite
Resource        CommonKeywords.resource
Resource        GoogleDiagKeywords.resource
Library         GoogleDiagLib.py
Library         CommonLib.py
Library         ../EDK2CommonLib.py
Variables       GoogleDiagVariable.py


Suite Setup     DiagOS Connect Device
Suite Teardown  DiagOS Disconnect Device

*** Test Cases ***
DIAG_TC_001_xxxx
    [Documentation]  This test checks the Installing ONIE via Flashcp on ONIE
    [Tags]  DIAG_TC_001_xxxx  
    [Setup]  xxxx
    Step  1  check diag info
    Step  2  xxxx
    [Teardown]  xxxx

EDK2_DIAG_TC_01_Install_Diag_Package_Test
    [Documentation]  This test checks installation of Diag package
    [Tags]   EDK2_DIAG_TC_01_Install_Diag_Package_Test  edk2  test1
    Step  1  boot Into Sonics
    Step  2  fetch Image From Server  ${new_diag_image}
    Step  3  install Diag Package  ${new_diag_image}
    Step  4  power cycle test
    Step  4  check Basic Diag Functions
    Step  5  power cycle test
    Step  6  check Basic Diag Functions  final
    #[Teardown]  Run Keyword If Test Failed   power me up



EDK2_DIAG_TC_02_Update_Diag_Package_Test
    [Documentation]  This test checks updation of Diag package
    [Tags]   EDK2_DIAG_TC_02_Update_Diag_Package_Test  edk2  test2
    Step  1  boot Into Sonics
    Step  2  install Old Diag Version
    Step  3  power cycle test
    Step  3  check Diag Version  old
    Step  4  remove Old Diag
    Step  5  fetch Image From Server  ${new_diag_image}
    Step  6  install Diag Package  ${new_diag_image}
    Step  8  power cycle test
    Step  9  check Basic Diag Functions
    Step  10  power cycle test
    Step  11  check Basic Diag Functions  final


EDK2_DIAG_TC_05_FPGA_UPGRADE_TEST
    [Documentation]  This test checks basic fpga tests
    [Tags]   EDK2_DIAG_TC_05_FPGA_UPGRADE_TEST  edk2  test5
    [Setup]  power cycle test  
    Step  1  verify diag tool path
    Step  2  check fpga upper
    Step  3  check downgrade upgrade  OLD  DUT
    Step  4  check fpga upper
    Step  5  check downgrade upgrade  NEW   DUT
    Step  6  check help  ${upgrade}
    Step  7  check version  ${upgrade}  ${upgrade_version}
    Step  6  check other options
    Step  8  check sysinfo test
    


EDK2_DIAG_TC_07_CPU_Test
     [Documentation]  This test checks basic cpu tests
     [Tags]   EDK2_DIAG_TC_07_CPU_Test  edk2  test7
     Step  1  verify diag tool path
     Step  2  check help  ${cpu}
     Step  3  check list  ${cpu}
     Step  4  check version  ${cpu}  ${cpu_version}
     Step  5  check test  ${cpu}
     Step  6  check cpu stats
     Step  7  check cpu file operation

EDK2_DIAG_TC_08_I2C_Test
    [Documentation]  This test checks basic i2c tests
    [Tags]   EDK2_DIAG_TC_08_I2C_Test  edk2  test8
    Step  1  verify diag tool path
    Step  2  check help  ${i2c}
    Step  3  check list  ${i2c}
    Step  4  check version  ${i2c}  ${i2c_version}
    Step  5  check test  ${i2c}
    Step  6  verify i2c port  ${i2c}  ${i2cbus_port}
    Step  7  check i2c detect  DUT
    Step  8  Checki2cdevice  ${i2cdetectdevicelst}
    Step  9  Read i2c device via Diag command  ${i2c}  ${i2cdevice_data}
    Step  10  verify i2c detect  ${i2c}  ${i2cbus_device_data}



EDK2_DIAG_TC_09_FPGA_Test
    [Documentation]  This test checks basic fpga tests
    [Tags]   EDK2_DIAG_TC_09_FPGA_Test  edk2  test9
    [Setup]  power cycle test 
    Step  1  verify diag tool path
    Step  2  check help  ${fpga}
    Step  3  check list  ${fpga}
    Step  4  check version  ${fpga}  ${fpga_version}
    Step  5  check major minor
    Step  6  check test  ${fpga}
    Step  6  check fpga operations
    Step  7  check i2cdetect  DUT
    Step  8  check fpga sdk  DUT
    Step  10  check i2cdetect  DUT
    Step  9  change to admin



EDK2_DIAG_TC_10_PCI_Test
    [Documentation]  This test checks basic pci tests
    [Tags]   EDK2_DIAG_TC_10_PCI_Test  edk2  test10
    [Setup]  power cycle test 
    Step  1  verify diag tool path
    Step  2  check help  ${pci}
    Step  3  check list  ${pci}
    Step  4  check version  ${pci}  ${pci_version}
    Step  5  check lspci
    Step  6  check test  ${pci}
    Step  7  check pci file




EDK2_DIAG_TC_11_RTC_Test
     [Documentation]  This test checks basic pci tests
     [Tags]   EDK2_DIAG_TC_11_RTC_Test  edk2  test11
     [Setup]  power cycle test  
     Step  1  verify diag tool path
     Step  2  check rtc new
     Step  3  check help  ${rtc}
     Step  4  check list  ${rtc}
     Step  5  check version  ${rtc}  ${rtc_version}
     Step  6  check rtc stat
     Step  7  check rtc file
     Step  8  power cycle test 
     Step  9  verify diag tool path
     Step  10  check rtc new
     Step  11  check test  ${rtc}
     Step  12  check rtc operation
     Step  13  check rtc new


EDK2_DIAG_TC_12_Temp_Test
    [Documentation]  This test checks basic temp test sensors
    [Tags]   EDK2_DIAG_TC_12_Temp_Test   edk2  test12
    Step  1  verify diag tool path
    Step  2  check help  ${temp}
    Step  3  check temp list
    Step  4  check version  ${temp}  ${temp_version}
    Step  5  check temp read  ${temp}
    Step  6  check temp test  ${temp}


EDK2_DIAG_TC_13_PSU_Test
    [Documentation]  This test read voltage values
    [Tags]   EDK2_DIAG_TC_13_PSU_Test   edk2  test13
    Step  1  verify diag tool path
    Step  2  check help  ${psu}
    Step  3  check list  ${psu}
    Step  4  check version  ${psu}  ${psu_version}
    Step  5  check psu read  ${psu}
    Step  6  check psu test  ${psu}
    Step  7  check psu sensor and psu file


EDK2_DIAG_TC_14_COMe_CPLD_Test
    [Documentation]  This test check CPLD  dev and register on CPLD spec.
    [Tags]   EDK2_DIAG_TC_14_COMe_CPLD_Test   edk2  test14
    [Setup]  power cycle test 
    Step  1  verify diag tool path
    Step  2  check help  ${cpld}
    Step  3  check list  ${cpld}
    Step  4  check version  ${cpld}  ${cpld_version}
    Step  5  check cpld operations
    Step  6  check test  ${cpld}
    Step  7  recheck cpld scratch
    Step  8  change to admin


EDK2_DIAG_TC_15_Baseboard_CPLD_Test
    [Documentation]  This test read/write cpld registers
    [Tags]   EDK2_DIAG_TC_15_Baseboard_CPLD_Test   edk2  test15
    [Setup]  power cycle test 
    Step  1  verify diag tool path
    Step  2  check baseboard help
    Step  3  check baseboard list
    Step  4  check version  ${bb_cpld}  ${bb_cpld_version}
    Step  5  check baseboard dev test
    Step  6  verify diag tool path
    Step  7  check baseboard test
    step  8  change to admin





EDK2_DIAG_TC_44_Stressapp_test
    [Documentation]  This test check stresstapp
    [Tags]   EDK2_DIAG_TC_44_Stressapp_test   edk2  test44  stress
    Step  1  verify home path
    Step  2  check stress help
    Step  3  cover mfg issue


EDK2_DIAG_TC_21_Memory_SPD_Information_Test
    [Documentation]  This test send characters to serial port to return correct characters 
    [Tags]   EDK2_DIAG_TC_21_Memory_SPD_Information_Test   edk2  test21
    Step  1  verify admin path
    Step  2  show memory spd information

EDK2_DIAG_TC_28_Set_OSFP_Low_Power_Mode_And_High_Power_Mode 
    [Documentation]  This test checks the low and high power modes 
    [Tags]   EDK2_DIAG_TC_28_Set_OSFP_Low_Power_Mode_And_High_Power_Mode   edk2  test28
    Step  1  verify diag tool path
    Step  2  check qsfp help  
    Step  3  check qsfp list  
    Step  4  check low and high power mode
    Step  5  check qsfp test 



EDK2_DIAG_TC_30_Sys_info_Test
    [Documentation]  This test checks sys information
    [Tags]   EDK2_DIAG_TC_30_Sys_info_Test   edk2  test30
    Step  0  check basic
    Step  1  verify diag tool path
    Step  2  check sys help
    Step  3  check sys list
    Step  4  check baseboard list
    Step  5  check sys info test
    Step  6  check major minor
    Step  7  check software info



EDK2_DIAG_TC_19_EEPROM_Test
    [Documentation]  This test used to flash TLV EEPROM
    [Tags]   EDK2_DIAG_TC_19_EEPROM_Test    test19
    Step  1  verify diag tool path
   # Step  2  check help  ${eeprom}
   # Step  3  check list  ${eeprom}
   # Step  4  check version  ${eeprom}  ${eeprom_version}
   # Step  5  check Eeprom test
   # Step  6  check Eeprom dump
   # Step  7  check Eeprom read
   # Step  8  check Eeprom data
   # Step  9  remove Eeprom data
   # Step  10  write tlv info
    Step  11  program Eeprom
    Step  12  change to admin


EDK2_DIAG_TC_38_DDR_STRESS_TEST
    [Documentation]  This test checks ddr stress
    [Tags]  EDK2_DIAG_TC_38_DDR_STRESS_TEST  edk2  test38  stress
    Step  1  check ddr test   ${mem}  ${mem164}
    #Step  2  check ddr test  ${memory28}  ${mem28}  ;#Takes12 hrs to execute
    Step  2  change to admin



EDK2_DIAG_TC_33_CHECKING_TH4G_MODEL_TEST
    [Documentation]  This test checks cpu stress
    [Tags]   EDK2_DIAG_TC_33_CHECKING_TH4G_MODEL_TEST  edk2   test33
    Step  1  verify diag tool path
    Step  2  check th4 operations


EDK2_DIAG_TC_34_ALL_TEST
    [Documentation]  This test all tests of device.
    [Tags]   EDK2_DIAG_TC_34_ALL_TEST  edk2   test34
    Step  1  verify diag tool path
    Step  2  check help  ${all}
    Step  3  check list  ${all}
    Step  4  check all tests


EDK2_DIAG_TC_35_STRUCTURE_TEST
    [Documentation]  This test diag structure
    [Tags]   EDK2_DIAG_TC_35_STRUCTURE_TEST   edk2  test35
    [Setup]  verify diag tool path 
     Step  1  check structure
     Step  2  check diag operations


EDK2_DIAG_TC_37_CPU_STRESS_TEST
    [Documentation]  This test checks cpu stress
    [Tags]  EDK2_DIAG_TC_37_CPU_STRESS_TEST  edk2  test37  stress
    Step  1  check cpu stress




EDK2_DIAG_TC_23_MAC_Test
    [Documentation]  This test is used to read and write MAC Id
    [Tags]    EDK2_DIAG_TC_23_MAC_Test   edk2  test23
    Step  1  verify diag tool
    Step  2  read MAC Id
    Step  3  read all mac
    Step  4  write MAC Id  DUT
    Step  5  verify diag tool
    Step  6  get mac add
    Step  7  write new mac id  DUT
    Step  8  verify diag tool
    Step  9  get mac add
    Step  10  check fw version
    Step  11  downgrade i210 fw  DUT
    Step  12  upgrade i210 fw  DUT
    Step  13  get mac add
    Step  14  change to admin


EDK2_DIAG_TC_23_MAC_Test_MTP
    [Documentation]  This test is used to read and write MAC Id
    [Tags]    EDK2_DIAG_TC_23_MAC_Test_MTP   edk2  test23.1
    Step  1  verify diag tool
    Step  2  read MAC Id
    Step  3  read all mac
    Step  4  write MAC Id  DUT
    Step  5  verify diag tool
    Step  6  get mac add
    Step  7  write new mac id  DUT
    Step  8  verify diag tool
    Step  9  get mac add


EDK2_DIAG_TC_36_STORAGE_STRESS_TEST
    [Documentation]  This test checks storage stress
    [Tags]  EDK2_DIAG_TC_36_STORAGE_STRESS_TEST  edk2  test36  stress
    Step  1  check storage stress



EDK2_DIAG_TC_03_Coreboot_Upgrade_Test
    [Documentation]  This test checks upgrade of BIOS/Coreboot
    [Tags]   EDK2_DIAG_TC_03_Coreboot_Upgrade_Test  edk2  test3
    Step  1  boot Into Sonics
    Step  2  check Coreboot Version  new
    Step  3  change Bios version  ${upgrade_bios_old_cmd}  DUT
    Step  4  power cycle test
    Step  5  check Coreboot Version  old
    Step  6  change Bios version  ${upgrade_bios_new_cmd}  DUT
    Step  7  power cycle test
    Step  8  check Coreboot Version  new
    Step  9  check Other Options


EDK2_DIAG_TC_04_CPLD_Upgrade_Test
    [Documentation]  This test checks upgrade of CPLD
    [Tags]   EDK2_DIAG_TC_04_CPLD_Upgrade_Test  edk2  test4
    Step  1  boot Into Sonics
    Step  2  check come CPLD Version  new
    Step  3  check baseboard CPLD Version  new
    # Downgrade CPLD
    Step  4  change cpld version  come  old
    Step  5  power cycle test
    Step  6  check come CPLD Version  old
    Step  7  change cpld version  baseboard  old
    Step  8  power cycle test
    Step  9  check baseboard CPLD Version  old
    # Upgrade CPLD
    Step  10  change cpld version  come  new
    Step  11  power cycle test
    Step  12  check come CPLD Version  new
    Step  13  change cpld version  baseboard  new
    Step  14  power cycle test
    Step  15  check baseboard CPLD Version  new
    Step  16  check Other Options

test_me
   [Documentation]  This test checks storage stress
    [Tags]  tset_me  testme
    Step   1  check me  old
    [Teardown]  Run Keyword If Test Failed   scrap it


EDK2_TEST_TC_AC_Power_Cycling_Stress
   [Documentation]  This test checks basic scans
   [Tags]  EDK2_TEST_TC_AC_Power_Cycling_Stress  edk2  powerup
   FOR    ${INDEX}    IN RANGE    1   100
      Step  2  power me up
   END


*** Keywords ***
DiagOS Connect Device
    DiagOSConnect

DiagOS Disconnect Device
    DiagOSDisconnect
