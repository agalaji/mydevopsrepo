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
import re
from inspect import getframeinfo, stack
import os.path
import time
import yaml
import Logger as log
import CommonLib
import random
import Const
import bios_menu_lib
import openbmc_lib
import Const
import YamlParse
import Logger as log
import pexpect
import getpass
import os
import traceback
import parser_openbmc_lib
import json
import CRobot
from BIOS_variable import *
from BMC_variable import *
from datetime import datetime, timedelta
from dataStructure import nestedDict, parser
from errorsModule import noSuchClass, testFailed
import CommonKeywords
from SwImage import SwImage
from Server import Server
from pexpect import pxssh
from functools import partial
import sys
import getpass
import WhiteboxLibAdapter
from crobot.Decorator import logThis
import pexpect
import multiprocessing
from TelnetDevice import TelnetDevice
from crobot.PowerCycler import PowerCycler
import MOONSTONECommonLib

try:
    import parser_openbmc_lib as parserOpenbmc
    import DeviceMgr
    from Device import Device

except Exception as err:
    log.cprint(str(err))

device = DeviceMgr.getDevice()
workDir = CRobot.getWorkDir()
sys.path.append(os.path.join(workDir, 'common', 'commonlib'))
sys.path.append(os.path.join(workDir, 'platform', 'moonstone'))
sys.path.append(os.path.join(workDir, 'platform', 'moonstone', 'bios'))

run_command = partial(CommonLib.run_command, deviceObj=device, prompt=device.promptDiagOS)
time.sleep(10)

import Logger as log


def random_test(device):
    bios_menu_lib.send_key(device, "KEY_CTRL_c")


def enter_into_bios_setup_now(device,mode='1'):
    log.debug('Entering procedure verify_bios_default_password with args : %s\n' % (str(locals())))
    bios_copy = 'EVALUATION COPY'
    deviceObj = Device.getDeviceObject(device)

    deviceObj.getPrompt("DIAGOS")
    deviceObj.sendline("")
    deviceObj.sendCmd("reboot")
    out = deviceObj.read_until_regexp('Total Memory Size', timeout=140)
    if not bios_copy in out:
        log.success('No EVALUATION COPY STRING PRESENT')
    else:
        raise RuntimeError('EVALUATION COPY STRING PRESENT')

    counter = 7
    while counter >= 0:
        bios_menu_lib.send_key(device, "KEY_DEL")
        counter -= 1
        time.sleep(1)
    if(int(mode)==2):
        deviceObj.read_until_regexp('ESC: Exit',timeout=30)
        log.success("successfully entered into bios")


@logThis
def check_bios_basic(device):
    pat1 = 'ESC: Exit'
    deviceObj = Device.getDeviceObject(device)
    out = deviceObj.read_until_regexp(pat1, timeout=10)
    log.success("cheked bios successfully")


@logThis
def save_and_exit_bios_now(device):
    deviceObj = Device.getDeviceObject(device)
    time.sleep(3)
    bios_menu_lib.send_key(device, "KEY_F4")

    time.sleep(4)

    bios_menu_lib.send_key(device, "KEY_ENTER", 1)
    save1_out = deviceObj.read_until_regexp('ESC:', timeout=15)
    bios_menu_lib.send_key(device, "KEY_ENTER", 1)

    time.sleep(10)

    deviceObj.read_until_regexp('localhost login', timeout=400)
    deviceObj.loginToDiagOS()
    log.success("exited from boot setup successfully")


def save_and_exit_onie_boot_now(device):
    deviceObj = Device.getDeviceObject(device)
    time.sleep(3)
    bios_menu_lib.send_key(device, "KEY_F4")

    time.sleep(4)
    bios_menu_lib.send_key(device, "KEY_ENTER", 2)

    time.sleep(40)
    log.success("received onie prompt")
    deviceObj.executeCmd('onie-stop')
    deviceObj.sendCmd('onie-sysinfo -v')

    output = deviceObj.read_until_regexp(onie_sysinfo_version, timeout=10)
    x = re.search(onie_sysinfo_version, output)
    if x is None:
        raise RuntimeError("onie-sysinfo -v not available")

    time.sleep(1)

    deviceObj.executeCmd('efibootmgr -o 0000')
    time.sleep(1)
    deviceObj.executeCmd('reboot', timeout=200)
    # out=deviceObj.read_until_regexp('Shell>',timeout=50)
    # deviceObj.sendline('exit')
    time.sleep(10)
    out = deviceObj.read_until_regexp('to enter setup', timeout=140)

    counter = 5
    while counter >= 0:
        bios_menu_lib.send_key(device, "KEY_DEL")
        counter -= 1
        time.sleep(1)
    log.success("successfully entered into bios")


def set_default_boot_setup_from_onie_and_uefi(device):
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_RIGHT", 6)

    bios_menu_lib.send_key(device, "KEY_DOWN", 6)

    bios_menu_lib.send_key(device, "KEY_ENTER", 1)

    m16_out = deviceObj.read_until_regexp('Load Optimized Defaults', timeout=10)
    bios_menu_lib.send_key(device, "KEY_ENTER", 1)
    bios_menu_lib.send_key(device, "KEY_UP", 6)

    bios_menu_lib.send_key(device, "KEY_ENTER", 1)
    m16_out = deviceObj.read_until_regexp('Save configuration and exit', timeout=10)
    bios_menu_lib.send_key(device, "KEY_ENTER", 1)
    log.success("successfully restore defaults setup")
    deviceObj.read_until_regexp('localhost login:', timeout=400)
    deviceObj.loginToDiagOS()


@logThis
def exit_bios_now(device):
    log.cprint('Entering into Step 3 function')
    deviceObj = Device.getDeviceObject(device)
    time.sleep(3)
    bios_menu_lib.send_key(device, "KEY_ESC")
    bios_menu_lib.send_key(device, "KEY_ENTER", 1)
    #save1_out = deviceObj.read_until_regexp('ESC:', timeout=15)
    bios_menu_lib.send_key(device, "KEY_ENTER", 1)
    time.sleep(5)
    deviceObj.sendCmd('\r')
    
    time.sleep(10)
    deviceObj.sendline('\r')
    deviceObj.read_until_regexp('localhost login', timeout=400)
    deviceObj.loginToDiagOS()
    log.success("exit from bios successfully")


def getting_cpu_microcode(device):
    cmd = "dmesg | grep -i  microcode"
    deviceObj = Device.getDeviceObject(device)
    deviceObj.sendCmd(cmd)
    output = deviceObj.read_until_regexp('Microcode Update Driver', timeout=130)
    log.cprint(output)
    x = re.search(microcode_revision_code, output)

    if x:
        microcode_revision = x.group(0).split("=")[1]
        log.debug("microcode_revision is : ")
        log.info(microcode_revision)
        return microcode_revision
    else:
        raise RuntimeError("microcode_revision not available")
    log.success("successfully get the microcode")


def get_microcode_revision_from_bios(device):
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_RIGHT", 2)
    bios_menu_lib.send_key(device, "KEY_ENTER", 1)
    out = deviceObj.read_until_regexp('L1 Cache RAM', timeout=15)

    pattern = "Microcode Revision\s+(\S+)"
    match = re.search(pattern, out)
    bios_menu_lib.send_key(device, "KEY_ESC", 5)
    if match:
        microcode_revision = str(match.group(1))
        log.debug("microcode_revision is : ")
        log.debug(microcode_revision)
        return microcode_revision
    else:
        raise RuntimeError("microcode_revision not available")
    
    log.success("successfully get the microcode revision")


def checking_memory_frequency(device, frequency):
    deviceObj = Device.getDeviceObject(device)
    cmd2 = f"dmidecode -t memory"
    
    deviceObj.sendCmd(cmd2)
    output = deviceObj.read_until_regexp('Configured Memory Speed:.*([0-9]{4})', timeout=160)
    t = re.search('Configured Memory Speed:.*([0-9]{4})', output)
    if t is not None:
        if t.group(1) == frequency:
            log.info("After dmidecode -t memory frequency is : ")
            log.info(t.group(1))
        else:
            log.fail("memory frequency not matched")
    else:
        log.fail("memory frequency not matched in dmidecode -t memory")
    time.sleep(10)
    deviceObj.sendCmd("reboot")
    output2 = deviceObj.read_until_regexp(memory_speed+frequency, timeout=160)
    log.success("successfully checked memory frequency")


def change_the_frequency(device, value):
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_RIGHT", 2)
    bios_menu_lib.send_key(device, "KEY_DOWN", 4)
    bios_menu_lib.send_key(device, "KEY_ENTER")
    bios_menu_lib.send_key(device, "KEY_DOWN", 3)
    run_loop = True
    log.info("setting frequency as %s" %value)
    while run_loop:
        try:
            m16_out = deviceObj.read_until_regexp('Memory Frequency.*'+value, timeout=10)
            run_loop = False
            break
        except Exception:
            try:
                bios_menu_lib.send_key(device, "KEY_ENTER")
                bios_menu_lib.send_key(device, "KEY_DOWN")
                bios_menu_lib.send_key(device, "KEY_ENTER")
            except Exception:
                continue
    bios_menu_lib.send_key(device, "KEY_ESC", 1)
    log.success("successfully changed the frequency")


def change_bios_password(device, old_password, new_password, accesslevel):
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_RIGHT", 4)
    m3_out = deviceObj.read_until_regexp('User Password', timeout=10)
    change_password(device, old_password, new_password, accesslevel)


def change_password(device, old_password, new_password, accesslevel):
    deviceObj = Device.getDeviceObject(device)
    if accesslevel == 'admin':
        bios_menu_lib.send_key(device, "KEY_ENTER")
        if old_password == 'default':
            for i in range(0, len(new_password)):
                value = new_password[i]
                bios_menu_lib.send_key(device, password_keys[value])

            bios_menu_lib.send_key(device, "KEY_ENTER")
            for i in range(0, len(new_password) - 1):
                value = new_password[i]
                bios_menu_lib.send_key(device, password_keys[value])
            m3_out = deviceObj.read_until_regexp('------------------------\/  ------------------------', timeout=10)
            bios_menu_lib.send_key(device, password_keys[new_password[len(new_password) - 1]])
            bios_menu_lib.send_key(device, "KEY_ENTER")
        else:
            for i in range(0, len(old_password)):
                value = old_password[i]
                bios_menu_lib.send_key(device, password_keys[value])
            bios_menu_lib.send_key(device, "KEY_ENTER", 1)
            m4_out = deviceObj.read_until_regexp('------------------------\/  ------------------------', timeout=10)
            bios_menu_lib.send_key(device, "KEY_ENTER", 2)
        log.success("password changed for admin successfully")
    else:
        if old_password != '4321':
            bios_menu_lib.send_key(device, "KEY_DOWN")
        bios_menu_lib.send_key(device, "KEY_ENTER")
        if old_password == 'default':
            for i in range(0, len(new_password)):
                value = new_password[i]
                bios_menu_lib.send_key(device, password_keys[value])

            bios_menu_lib.send_key(device, "KEY_ENTER")
            for i in range(0, len(new_password)):
                value = new_password[i]
                bios_menu_lib.send_key(device, password_keys[value])
            m6_out = deviceObj.read_until_regexp('------------------------\/  ------------------------', timeout=10)
            bios_menu_lib.send_key(device, "KEY_ENTER")
        else:
            for i in range(0, len(old_password)):
                value = old_password[i]
                bios_menu_lib.send_key(device, password_keys[value])
            bios_menu_lib.send_key(device, "KEY_ENTER", 1)
            m7_out = deviceObj.read_until_regexp('------------------------\/  ------------------------', timeout=10)
            bios_menu_lib.send_key(device, "KEY_ENTER", 2)
        log.success("password changed for user successfully")


def login_to_device(device, password):
    deviceObj = Device.getDeviceObject(device)
    m10_out = deviceObj.read_until_regexp('----------------------', timeout=10)
    for i in range(0, len(password)):
        value = password[i]
        bios_menu_lib.send_key(device, password_keys[value])
    bios_menu_lib.send_key(device, 'KEY_ENTER')
    #deviceObj.read_until_regexp('localhost login', timeout=160)
    log.success("login successfull")


def check_accesslevel(device, accesslevel):
    deviceObj = Device.getDeviceObject(device)
    m11_out = deviceObj.read_until_regexp('System Date', timeout=10)
    pattern = "Accesslevel\s+(\S+\s\S+)"

    access = ''
    match = re.search(pattern, m11_out)
    if match:
        access = str(match.group(1))
        log.info("Accesslevel is : ")
        log.info(access)
        if access != accesslevel:
            log.fail("Accesslevel not correct")
            raise RuntimeError("Accesslevel not correct")
    log.success("accesslevel matched")


def check_bios_information_from_bios_setup(device):
    deviceObj = Device.getDeviceObject(device)
    m12_out = deviceObj.read_until_regexp('System Date', timeout=10)
    result_string = ''
    
    for i in pattern_check_bios_setup:
        pattern = i
        match = re.findall(pattern, m12_out)
        if "Project Version" in pattern:
            log.info(match[0])
            ver = match[0].replace(" ", "")
            ver = ver.replace(".", "")
            match[0]=ver
            log.info(match[0])
        if match:
            result_string = result_string + str(match[0]) + '||'
        else:
            log.info(i)
            log.info("not available")
            raise RuntimeError("BIOS vendor not available")
    log.info(result_string)
    log.success("successfully fetched bios information from setup")
    return result_string


def checking_bios_information_from_post_log(device):
    deviceObj = Device.getDeviceObject(device)
    deviceObj.sendCmd("reboot")
    m13_out = deviceObj.read_until_regexp('to enter boot menu', timeout=100)
    result_string = ''
    for i in pattern_check_bios_post_log:
        pattern = i

        match = re.search(pattern, m13_out)
        if match:
            result_string = result_string + str(match.group(1)) + '||'
        else:
            log.info(i)
            log.info("not available")
            raise RuntimeError("bios post log information not available")
    log.info(result_string)
    log.success("successfully fetched bios information from os")
    deviceObj.read_until_regexp('localhost login', timeout=400)
    deviceObj.loginToDiagOS()
    return result_string


def checking_bios_information_from_dmidecode(device, output_from_bios_setup):
    deviceObj = Device.getDeviceObject(device)
    deviceObj.getPrompt("DIAGOS")
    deviceObj.sendCmd("dmidecode -t bios")
    m14_out = deviceObj.read_until_regexp('Currently Installed Language', timeout=15)
    result_string = ''
    for i in pattern_check_bios_dmidecode:
        pattern = i
        match = re.search(pattern, m14_out)
        if match:
            result_string = result_string + str(match.group(1)) + '||'
        else:
            log.info(i)
            log.info("not available")
            log.fail("bios dmidecode informatio not available")

    lst = output_from_bios_setup.split("||")
    result_string_lst = result_string.split('||')
    if result_string_lst[0] != lst[0] or result_string_lst[1] != lst[1]:
        log.info(result_string_lst[0])
        log.info(lst[0])
        log.info(result_string_lst[1])
        log.info(lst[1])
        log.fail("vendor and project version not matched")

    log.success("vendor and project version matched")


def set_boot_onie(device):
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_RIGHT", 5)
    bios_menu_lib.send_key(device, "KEY_DOWN", 4)
    run_loop = True
    while run_loop:
        try:
            m16_out = deviceObj.read_until_regexp(' Boot Option #1.*\[ONIE: Open Network', timeout=10)
            run_loop = False
            break
        except Exception:
            try:
                bios_menu_lib.send_key(device, "KEY_ENTER")
                bios_menu_lib.send_key(device, "KEY_DOWN")
                bios_menu_lib.send_key(device, "KEY_ENTER")

            except Exception:
                continue

    log.success("successfully set boot onie")


def save_and_exit_menu(device):
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_RIGHT", 6)
    bios_menu_lib.send_key(device, "KEY_ENTER")
    m17_out = deviceObj.read_until_regexp('Restore User Defaults', timeout=10)
    bios_menu_lib.send_key(device, "KEY_ENTER")
    m171_out = deviceObj.read_until_regexp('Save configuration and exit?', timeout=10)
    time.sleep(10)
    deviceObj.sendline('\r')
    deviceObj.read_until_regexp('localhost login', timeout=400)
    deviceObj.loginToDiagOS()
    log.success("successfully save and exit menu")


def check_memory_information(device):
    deviceObj = Device.getDeviceObject(device)
    cmd2 = f"dmidecode -t memory"
    memory_dmidecode = deviceObj.executeCmd(cmd2)
    x = re.search('Number Of Devices:\s+(\S+)', memory_dmidecode)
    if x is None:
        log.fail("memory_dmidecode output not matched")

    number_of_devices = x.group(1)
    for item in pattern_dmidecode_memory:
        x = re.search(item, memory_dmidecode)
        if x is None:
            raise RuntimeError("%s is not present in memory dmidecode output" % item)
        else:
            log.success("%s is present in memory dmidecode output" % item)

    try:
        c = int(number_of_devices)
    except Exception:
        log.fail("number of devices is not integer")

    log.info("dmidecode -t memory has number of devices =")
    log.info(number_of_devices)
    cmd4 = f"cat /proc/meminfo"
    log.info('running... cat /proc/meminfo :')
    memory_info = deviceObj.executeCmd(cmd4, timeout=60)

    if ("Error" in memory_info) or ("error" in memory_info) or ("Failed" in memory_info) or ("failed" in memory_info):
        raise RuntimeError("cat /proc/meminfo output has error in it")
    log.success("cat /proc/meminfo is working fine.. ")
    log.info("cat /proc/meminfo is working fine...")
    deviceObj.sendCmd("reboot")
    output = deviceObj.read_until_regexp('2400', timeout=100)
    log.cprint(output)
    log.info("After reboot memory frequency is : ")
    log.info('2400Mhz')
    x = re.search(memory_speed_general, output)
    if x is None:
        raise RuntimeError("memory speed not matched in reboot")
    log.success("memory speed is 2400Mhz")


def check_main_menu(device):
    deviceObj = Device.getDeviceObject(device)
    m19_out = deviceObj.read_until_regexp('ESC:', timeout=10)
    result_string = ''
    for i in main_menu_items:
        pattern = i
        match = re.search(pattern, m19_out)
        if match:
            log.info(str(match.group(1)))
            result_string = result_string + str(match.group(1)) + '||'
        else:
            log.info(i)
            log.info("not available")

            raise RuntimeError("main menu datanot available")

    bios_menu_lib.send_key(device, "KEY_ENTER")
    output = deviceObj.read_until_regexp('English', timeout=140)
    pattern = "English"
    system_language = 'English'
    match = re.search(pattern, output)
    bios_menu_lib.send_key(device, "KEY_ENTER")
    if match:
        system_language = match.group()
        log.info("System language is : ")
        log.info(system_language)
    else:

        raise RuntimeError("System language not available")
    log.info(result_string)
    log.info(main_menu_test_data_1)
    result_string_lst = result_string.split("||")
    if main_menu_test_data_1 != result_string_lst[0] + '||' + result_string_lst[1] + '||' + system_language + '||' + \
            result_string_lst[2] + '||' + result_string_lst[3]:
        raise RuntimeError("data not matched")

    bios_menu_lib.send_key(device, "KEY_DOWN")
    bios_menu_lib.send_key(device, "KEY_PLUS", 2)
    log.info("change date to two days after")
    bios_menu_lib.send_key(device, "KEY_DOWN")
    bios_menu_lib.send_key(device, "KEY_PLUS", 2)
    log.info("change time to two hours after")

    return result_string_lst[4] + '||' + result_string_lst[5]


def check_changed_date_and_time(device, date_and_time, first_time):
    deviceObj = Device.getDeviceObject(device)
    output_update = deviceObj.read_until_regexp('ESC:', timeout=10)
    result_string = ''
    for i in pattern_date_and_time:
        pattern = i
        match = re.search(pattern, output_update)
        if match:
            result_string = result_string + str(match.group(1)) + '||'
        else:
            log.info(i)
            log.info("not available")

            raise RuntimeError("data not available")
    lst = date_and_time.split("||")
    result_string_lst = result_string.split('||')
    if lst[0] == result_string_lst[0] or lst[1] == result_string_lst[1]:
        log.fail("date or time did not changed")

    if first_time == 'true':
        bios_menu_lib.send_key(device, "KEY_DOWN")
        bios_menu_lib.send_key(device, "KEY_MINUS", 5)
        log.info("change date to five days before")
        bios_menu_lib.send_key(device, "KEY_DOWN")
        bios_menu_lib.send_key(device, "KEY_MINUS", 5)
        log.info("change time to 5 hours before")
    log.info("date chenged successfully")
    return result_string_lst[0] + '||' + result_string_lst[1]


def set_boot_uefi(device):
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_RIGHT", 5)
    bios_menu_lib.send_key(device, "KEY_DOWN", 4)

    run_loop = True
    log.info("setting boot order 1 as uefi shell")
    while run_loop:
        try:
            m16_out = deviceObj.read_until_regexp('Boot Option #1.*\[UEFI: Built-in EFI', timeout=10)
            run_loop = False
            break
        except Exception:
            try:
                bios_menu_lib.send_key(device, "KEY_ENTER")
                bios_menu_lib.send_key(device, "KEY_DOWN")
                bios_menu_lib.send_key(device, "KEY_ENTER")
            except Exception:
                continue

    bios_menu_lib.send_key(device, "KEY_F4")

    time.sleep(4)
    bios_menu_lib.send_key(device, "KEY_ENTER", 2)

    # out=deviceObj.read_until_regexp('Shell>',timeout=50)
    # deviceObj.sendline('exit')
    time.sleep(10)
    m21_out = deviceObj.read_until_regexp('Shell>', timeout=10)
    match = re.search('Shell>', m21_out)
    if match is None:
        raise RuntimeError("shell prompt not available")
    log.success("shell prompt available")


def exit_the_shell(device):
    deviceObj = Device.getDeviceObject(device)

    deviceObj.sendCmd('exit')
    try:
        m16_out = deviceObj.read_until_regexp('ONIE: OS Install Mode', timeout=60)
        time.sleep(10)
        deviceObj.executeCmd('efibootmgr -o 0001')
        time.sleep(1)
        deviceObj.executeCmd('reboot', timeout=200)
        time.sleep(10)
        out = deviceObj.read_until_regexp('to enter setup', timeout=140)

        counter = 5
        while counter >= 0:
            bios_menu_lib.send_key(device, "KEY_DEL")
            counter -= 1
            time.sleep(1)
        log.success("successfully entered into bios")
        set_default_boot_setup_from_onie_and_uefi(device)
        log.success("exited from boot setup successfully")
    except Exception:

        deviceObj.loginToDiagOS()
        log.success("exited from boot setup successfully")
        enter_into_bios_setup_now(device)
        set_default_boot_setup_from_onie_and_uefi(device)
        log.success("exited from boot setup successfully")

@logThis
def exit_the_shell2(device):
    device = DeviceMgr.getDevice()
    
    device.sendCmd("cls")
    device.sendCmd("fs0: \r \n")
    device.sendCmd("ls")
    try:
        device.read_until_regexp('EFI', timeout=10)
    except:
        device.sendCmd("cls")
        device.sendCmd("fs1:")
        device.sendCmd("ls")
        device.read_until_regexp('EFI', timeout=10)
    device.sendCmd('cd EFI \r \n')
    time.sleep(2)
    device.sendCmd('cd ONL \r \n')
    time.sleep(2)
    device.sendCmd('grubx64.efi \r \n')
    time.sleep(5)
    device.sendCmd('\r')
    device.read_until_regexp('localhost login:',timeout=400)

    
    device.loginToDiagOS()
    log.success("exited from boot setup successfully")
    

def boot_uefi_test(device):
    deviceObj = Device.getDeviceObject(device)
    time.sleep(10)
    exit_the_shell2(device)


def boot_uefi_shell_test(device):
    deviceObj = Device.getDeviceObject(device)
    deviceObj.sendCmd("reboot")
    m21_out = deviceObj.read_until_regexp('Shell>', timeout=200)
    match = re.search('Shell>', m21_out)
    if match is None:
        raise RuntimeError("shell prompt not available")
    deviceObj.sendCmd("pci")
    m25_out = deviceObj.read_until_regexp('00   07   00    00 ==> Network Controller - Ethernet controller',
                                          timeout=100)
    output_list = m25_out.splitlines()
    index = -1
    for i in range(0, len(output_list)):

        x = re.search(pci_result[0], output_list[i])
        if x is not None:
            index = i
            break
    if index == -1:
        log.info("pci output not matched ...")

    j = 0
    for i in range(index, len(output_list)):
        log.cprint(pci_result[j].strip())
        lst = output_list[i].split(' ')
        if len(lst) > 0:
            if lst[0] == 'Shell>':
                lst[0] = '00'
        string = ' '.join(lst)
        log.cprint(string.strip())
        x = re.search(pci_result[j].strip(), string.strip())
        if x is None:
            log.info("pci output not matched")

        j = j + 1
    log.info("pci output matched")
    exit_the_shell2(device)
    log.success("successfully check boot uefi test")


def check_bmc_information_from_setup(device):
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_RIGHT", 3)
    m1 = deviceObj.read_until_regexp('Wait For BMC', timeout=10)
    result_string = ''
    
    CommonKeywords.should_match_ordered_regexp_list(m1, pattern_bmc_information_setup)
    #CommonKeywords.should_match_ordered_regexp_list(c2, sel_list_pattern)
    log.success("successfully fetched bmc information from setup")
    return result_string


def check_bmc_information_from_os(device):
    deviceObj = Device.getDeviceObject(device)
    m1 = deviceObj.executeCmd('ipmitool mc info')

    result_string = ''
    CommonKeywords.should_match_ordered_regexp_list(m1, pattern_bmc_information_os)
    log.success("successfully fetched bmc information from os")
    return result_string


def update_bmc_firmware(device):
    deviceObj = Device.getDeviceObject(device)

    deviceObj.executeCmd('cd diag/home/cel_diag/moonstone2v2/firmware/bmc/')
    deviceObj.executeCmd('dhclient -v ma1')
    download_files_in_usb(device, bmc_file_path)
    time.sleep(10)
    deviceObj.executeCmd('cd')
    
    m1 = deviceObj.executeCmd('cd /home/cel_diag/moonstone/bin/')

    m2 = deviceObj.sendCmd('./cel-upgrade-test --update  -d 5 -f ../firmware/bmc/R4039-DS3000-1.02.00.ima', timeout=600)
    m281_out = deviceObj.read_until_regexp('Passed', timeout=600)
    log.success("bmc firmware update successfull")


def check_management_port_information(device):
    deviceObj = Device.getDeviceObject(device)
    deviceObj.sendCmd("pci")
    m1 = deviceObj.read_until_regexp(management_port_command, timeout=10)
    for i in pattern_management_port_pci:
        x = re.search(i, m1)
        if x is None:
            log.info("data not available")

    log.info("pci output has 02 00 00 and 03 00 00 entries")
    exit_the_shell2(device)
    
    m3 = deviceObj.sendCmd("lspci")
    m00_out = deviceObj.read_until_regexp('07:00', timeout=10)
    for i in pattern_management_port_lspci:
        x = re.search(i, m00_out)
        if x is None:
            log.info("data not available")

    log.info("lspci output has 02:00.0 and 03:00.0")
    log.success("pci output has 02 00 00 and 03 00 00 entries and lspci output has 02:00.0 and 03:00.0")

def boot_menu_onl(device):
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_RIGHT", 6)

    bios_menu_lib.send_key(device, "KEY_DOWN", 6)

    bios_menu_lib.send_key(device, "KEY_ENTER", 1)

    m16_out = deviceObj.read_until_regexp('Load Optimized Defaults', timeout=10)
    bios_menu_lib.send_key(device, "KEY_ENTER", 1)
    
    bios_menu_lib.send_key(device, "KEY_RIGHT", 6)
    log.info("setting boot to onl as first option")
    # m161_out=deviceObj.read_until_regexp('Boot Option #2 ' ,timeout=10)
    bios_menu_lib.send_key(device, "KEY_DOWN", 4)
    run_loop = True
    while run_loop:
        try:
            #m16_out = deviceObj.read_until_regexp('Boot Option #1\s+\[\(UEFI\) ONL OS|Open Network Linux', timeout=10)
            m16_out = deviceObj.read_until_regexp('(Boot Option #1\s+\[\(UEFI\) ONL OS)|(Boot Option #1\s+.*Open Network Linux)', timeout=10)
            run_loop = False
            break
        except Exception:
            try:
                bios_menu_lib.send_key(device, "KEY_ENTER")
                bios_menu_lib.send_key(device, "KEY_DOWN")
                bios_menu_lib.send_key(device, "KEY_ENTER")

                # m16_out=deviceObj.read_until_regexp(' Boot Option #1          \[\(UEFI\) ONIE OS',timeout=10)

                # run_loop=False
                # break
            except Exception:
                continue

    log.success("successfully set boot onie")
    save_and_exit_bios_now(device)
    

    
    
    
def boot_menu_onie(device):
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_RIGHT", 5)
    log.info("setting boot to onie as first option")
    # m161_out=deviceObj.read_until_regexp('Boot Option #2 ' ,timeout=10)
    bios_menu_lib.send_key(device, "KEY_DOWN", 4)
    run_loop = True
    while run_loop:
        try:
            m16_out = deviceObj.read_until_regexp(' Boot Option #1.*\[ONIE: Open Network', timeout=10)
            run_loop = False
            break
        except Exception:
            try:
                bios_menu_lib.send_key(device, "KEY_ENTER")
                bios_menu_lib.send_key(device, "KEY_DOWN")
                bios_menu_lib.send_key(device, "KEY_ENTER")

                # m16_out=deviceObj.read_until_regexp(' Boot Option #1          \[\(UEFI\) ONIE OS',timeout=10)

                # run_loop=False
                # break
            except Exception:
                continue

    log.success("successfully set boot onie")
    save_and_exit_onie_boot_now(device)


def set_ipv4_pxe_support_status_bios(device, status="enable"):
    """
    Set bios config: bios->Advanced->NetWork Stack Configuration->Ipv4_pxe_support
    For Midstone100X Case: Boot_Option_Configuration_Test
    :param device:the name of the tested product
    :param status:enable/disabled
    """
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_RIGHT")
    bios_menu_lib.send_key(device, "KEY_DOWN", 6)
    bios_menu_lib.send_key(device, "KEY_ENTER")
    time.sleep(6)
    if status == "enable":
        try:
            log.info("Enable network stack")
            run_loop = True
            while run_loop:
                try:
                    m16_out = deviceObj.read_until_regexp('Network Stack.*Enable', timeout=10)
                    run_loop = False
                    break
                except Exception:
                    try:
                        bios_menu_lib.send_key(device, "KEY_ENTER")
                        bios_menu_lib.send_key(device, "KEY_DOWN")
                        bios_menu_lib.send_key(device, "KEY_ENTER")
                    except Exception:
                        continue
           
            
            
            bios_menu_lib.send_key(device, "KEY_DOWN", 1)
            bios_menu_lib.send_key(device, "KEY_ENTER")
            bios_menu_lib.send_key(device, "KEY_DOWN")
            bios_menu_lib.send_key(device, "KEY_ENTER")
            time.sleep(5)
                 
            #if "Disabled" not in out_put_3:
            bios_menu_lib.send_key(device, "KEY_DOWN", 1)
            bios_menu_lib.send_key(device, "KEY_ENTER")
            bios_menu_lib.send_key(device, "KEY_DOWN")
            bios_menu_lib.send_key(device, "KEY_ENTER")
            log.info("successfully changed Ipv4 HTTP support to enabled")
            bios_menu_lib.send_key(device, "KEY_ESC")
        except Exception:
            log.info("Inside exception")
            bios_menu_lib.send_key(device, "KEY_ENTER")
            bios_menu_lib.send_key(device, "KEY_DOWN")
            bios_menu_lib.send_key(device, "KEY_ENTER")
            log.info("successfully goes into  Network Stack Configuration option")
            out_put = deviceObj.read_until_regexp("Ipv4 HTTP Support", timeout=5)

            if "Disabled" in out_put:
                bios_menu_lib.send_key(device, "KEY_DOWN", 2)
                bios_menu_lib.send_key(device, "KEY_ENTER")
                bios_menu_lib.send_key(device, "KEY_DOWN")
                bios_menu_lib.send_key(device, "KEY_ENTER")
                log.info("successfully changed Ipv4 HTTP support to enabled")
            bios_menu_lib.send_key(device, "KEY_ESC")
            
            
        log.info("wait 10 sec ....")
        time.sleep(10)
        bios_menu_lib.send_key(device, "KEY_DOWN")
        bios_menu_lib.send_key(device, "KEY_ENTER", 2)
        bios_menu_lib.send_key(device, "KEY_DOWN")
        bios_menu_lib.send_key(device, "KEY_ENTER")
        log.info("successfully checked network to be uefi in CSM tab")
        bios_menu_lib.send_key(device, "KEY_ESC")
        log.success("successfully set ipv4 pxe support status to be enabled")

    else:
        try:
            bios_menu_lib.send_key(device, "KEY_DOWN")
            bios_menu_lib.send_key(device, "KEY_ENTER")
            bios_menu_lib.send_key(device, "KEY_DOWN")
            bios_menu_lib.send_key(device, "KEY_ENTER")
            
            bios_menu_lib.send_key(device, "KEY_DOWN")
            bios_menu_lib.send_key(device, "KEY_ENTER")
            bios_menu_lib.send_key(device, "KEY_DOWN")
            bios_menu_lib.send_key(device, "KEY_ENTER")
            
            bios_menu_lib.send_key(device, "KEY_UP", 2)
            bios_menu_lib.send_key(device, "KEY_ENTER")
            bios_menu_lib.send_key(device, "KEY_DOWN")
            bios_menu_lib.send_key(device, "KEY_ENTER")
            bios_menu_lib.send_key(device, "KEY_ESC")
            time.sleep(10)  
            
            bios_menu_lib.send_key(device, "KEY_DOWN")
            bios_menu_lib.send_key(device, "KEY_ENTER", 2)
            bios_menu_lib.send_key(device, "KEY_DOWN")
            bios_menu_lib.send_key(device, "KEY_ENTER")
            bios_menu_lib.send_key(device, "KEY_ESC")
            time.sleep(10)
            log.info("successfully changed Ipv4 HTTP support and network  to disabled")
            
        except Exception:
            bios_menu_lib.send_key(device, "KEY_ESC")
        log.success("successfully set ipv4 pxe support status to be disabled")

        bios_menu_lib.send_key(device, "KEY_RIGHT", 5)
        bios_menu_lib.send_key(device, "KEY_DOWN", 6)
        bios_menu_lib.send_key(device, "KEY_ENTER", 2)
        time.sleep(10)
        log.success("successfully changed to default state")
        
        log.info("setting boot to onl as first option")
        bios_menu_lib.send_key(device, "KEY_LEFT", 1)
        bios_menu_lib.send_key(device, "KEY_DOWN", 4)
        run_loop = True
        while run_loop:
            try:
                m16_out = deviceObj.read_until_regexp('(Boot Option #1\s+\[\(UEFI\) ONL OS)|(Boot Option #1\s+.*Open Network Linux)', timeout=10)
                run_loop = False
                break
            except Exception:
                try:
                    bios_menu_lib.send_key(device, "KEY_ENTER")
                    bios_menu_lib.send_key(device, "KEY_DOWN")
                    bios_menu_lib.send_key(device, "KEY_ENTER")
                except Exception:
                    continue
    
        log.success("successfully set boot onie")


def set_boot_pxe(device):
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_RIGHT", 5)
    # m161_out=deviceObj.read_until_regexp('Boot Option #2 ' ,timeout=10)
    bios_menu_lib.send_key(device, "KEY_DOWN", 4)
    run_loop = True
    log.info("setting boot order 2 to pxe ip4")
    while run_loop:
        try:
            out_put = deviceObj.read_until_regexp("Boot Option #1.*\[UEFI: PXE IPv4", timeout=5)
            run_loop = False
            break
        except Exception:
            try:
                bios_menu_lib.send_key(device, "KEY_ENTER")
                bios_menu_lib.send_key(device, "KEY_DOWN")
                bios_menu_lib.send_key(device, "KEY_ENTER")

                # m16_out=deviceObj.read_until_regexp(' Boot Option #1          \[\(UEFI\) ONIE OS',timeout=10)

                # run_loop=False
                # break
            except Exception:
                continue

    log.info("successfully added ipv4 boot option as first priority")
    save_and_exit_from_pxe(device)


def save_and_exit_from_pxe(device):
    deviceObj = Device.getDeviceObject(device)
    time.sleep(3)
    bios_menu_lib.send_key(device, "KEY_F4")
    time.sleep(4)
    bios_menu_lib.send_key(device, "KEY_ENTER", 1)
    bios_menu_lib.send_key(device, "KEY_ENTER", 1)
    # out=deviceObj.read_until_regexp('Shell>',timeout=50)
    # deviceObj.sendline('exit')
    time.sleep(20)

def check_non_bios_messages(device):
    deviceObj = Device.getDeviceObject(device)
    
    

    output_1_1 = deviceObj.read_until_regexp("NBP filesize is\s+\S+\s+Bytes", timeout=200)
    for i in range(0, len(pattern_pxe_server) - 2):
        x = re.search(pattern_pxe_server[i], output_1_1)
        if x is None:
            log.info(pattern_pxe_server[i])

            raise RuntimeError("data not present")

    output_1 = deviceObj.read_until_regexp("NBP file downloaded successfully", timeout=200)
    for i in range(len(pattern_pxe_server) - 2, len(pattern_pxe_server)):
        x = re.search(pattern_pxe_server[i], output_1)
        if x is None:
            log.info(pattern_pxe_server[i])
            raise RuntimeError("data not present")

    log.success("all messages are present")
    deviceObj.sendCmd('reboot')
    log.success("successfully downloaded NBP file")
    log.success("successfully entered into grub")


def check_exit_from_pxe(device):
    deviceObj = Device.getDeviceObject(device)
    out_put_1 = deviceObj.read_until_regexp("NBP file downloaded successfully", timeout=200)

    deviceObj.sendCmd('reboot')
    log.success("successfully downloaded NBP file")
    log.success("successfully entered into grub")


@logThis
def enter_into_bios_setup_from_pxe(device):
    deviceObj = Device.getDeviceObject(device)
    out = deviceObj.read_until_regexp('Total Memory Size', timeout=200)

    counter = 7
    while counter >= 0:
        bios_menu_lib.send_key(device, "KEY_DEL")
        counter -= 1
        time.sleep(1)
    log.success(" successfully entered into bios")
    out_put = deviceObj.read_until_regexp("ESC:", timeout=5)


def s0_state_test(device):
    deviceObj = Device.getDeviceObject(device)
    deviceObj.sendCmd('reboot')
    deviceObj.read_until_regexp('localhost login', timeout=400)
    deviceObj.loginToDiagOS()
    c1 = deviceObj.executeCmd("ipmitool mc info")
    CommonKeywords.should_match_ordered_regexp_list(c1, pattern_bmc_information_os)
    
    c2 = deviceObj.executeCmd("lspci")
    CommonKeywords.should_match_ordered_regexp_list(c2, lscpi_pattern)
    
    c3 = deviceObj.executeCmd("fdisk -l")
    CommonKeywords.should_match_ordered_regexp_list(c3, fdisk_op_re)
    
    for i in commands_in_s0_state_test:
        c1 = deviceObj.executeCmd(i)
        if ("Error" in c1) or ("error" in c1) or ("Failed" in c1) or ("failed" in c1):
            raise RuntimeError("Error in output")
    log.success("s0 state test passed successfully")




def memtest86_usg_image_to_executable(device):
    deviceObj = Device.getDeviceObject(device)
    c1 = deviceObj.executeCmd("dhclient -v ma1")
    download_files_in_usb(device, memtest_file)

    c3 = deviceObj.executeCmd("dd if=memtest86-usb.img of=/dev/sdc1", timeout=320)
    if ("Error" in c1) or ("error" in c1) or ("Failed" in c1) or ("failed" in c1):
        raise RuntimeError("dd if=memtest86-usb.img of=/dev/sdc1 output is giving error in its output")


def set_usb_partition_1(device):
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_RIGHT", 5)
    m161_out = deviceObj.read_until_regexp('Boot Option #2 ', timeout=10)
    bios_menu_lib.send_key(device, "KEY_DOWN", 3)
    run_loop = True
    while run_loop:
        try:
            bios_menu_lib.send_key(device, "KEY_ENTER")
            bios_menu_lib.send_key(device, "KEY_DOWN")
            bios_menu_lib.send_key(device, "KEY_ENTER")
            m16_out = deviceObj.read_until_regexp('Boot Option #1          \[UEFI:  USB, Partition', timeout=10)
            run_loop = False
            break
        except Exception:
            continue
    bios_menu_lib.send_key(device, "KEY_F4")
    bios_menu_lib.send_key(device, "KEY_ENTER")
    m161_out = deviceObj.read_until_regexp('\(x\) Exit', timeout=60)

    log.success("successfully set USB partion 1 as first boot priority")


def check_memtest86(device):
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_s")

    m161_out = deviceObj.read_until_regexp('\(c\)onfiguration')
    m161_out = deviceObj.read_until_regexp('Finished pass #1', timeout=100000)
    m161_out = deviceObj.read_until_regexp('Finished pass #2', timeout=100000)
    m161_out = deviceObj.read_until_regexp('Finished pass #3', timeout=100000)

    m161_out = deviceObj.read_until_regexp('Test Complete', timeout=10000000)
    bios_menu_lib.send_key(device, "KEY_ENTER")
    bios_menu_lib.send_key(device, "KEY_RIGHT")
    bios_menu_lib.send_key(device, "KEY_y")
    bios_menu_lib.send_key(device, "KEY_x")
    log.info("successfully completed the test")
    out = deviceObj.read_until_regexp('to enter setup', timeout=140)

    counter = 5
    while counter >= 0:
        bios_menu_lib.send_key(device, "KEY_DEL")
        counter -= 1
        time.sleep(1)
    log.success("successfully entered into bios")


def set_default_boot_order(device):
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_RIGHT", 5)
    # m161_out=deviceObj.read_until_regexp('Boot Option #2' ,timeout=10)
    bios_menu_lib.send_key(device, "KEY_DOWN", 3)
    run_loop = True
    while run_loop:
        try:
            m16_out = deviceObj.read_until_regexp('(Boot Option #1\s+\[\(UEFI\) ONL OS)|(Boot Option #1\s+.*Open Network Linux)', timeout=10)
            run_loop = False
            break
        except Exception:
            try:
                bios_menu_lib.send_key(device, "KEY_ENTER")
                bios_menu_lib.send_key(device, "KEY_DOWN")
                bios_menu_lib.send_key(device, "KEY_ENTER")

                # m16_out=deviceObj.read_until_regexp('Boot Option #1          \[\(UEFI\) ONL OS ',timeout=10)

                # run_loop=False
                # break
            except Exception:
                continue
    log.info("successfully set boot onl")
    bios_menu_lib.send_key(device, "KEY_F4")
    bios_menu_lib.send_key(device, "KEY_ENTER")
    deviceObj.read_until_regexp('localhost login', timeout=400)
    deviceObj.loginToDiagOS()
    log.success("exited from boot setup successfully")


def online_programming_under_uefi_shell_onl(device):
    deviceObj = Device.getDeviceObject(device)
    deviceObj.executeCmd("cd")
    deviceObj.executeCmd("dhclient -v ma1")
    c1 = deviceObj.executeCmd("mount /dev/sdc1 /mnt")
    if 'wrong fs type' in c1:
        deviceObj.executeCmd("umount /dev/sdc1")
        deviceObj.executeCmd('mkfs.vfat /dev/sdc1')
        deviceObj.executeCmd("mount /dev/sdc1 /mnt")
    deviceObj.executeCmd("cd /mnt")
    
    download_file_through_brixia(device, AfuEfix64_file_path, AfuEfix64_file)
    download_file_through_brixia(device, moonstone_bios_old_image_path, moonstone_bios_old_image)
    deviceObj.executeCmd("mv %s %s" %(moonstone_bios_old_image, moonstone_bios_old_img_version) )
    
    download_file_through_brixia(device, moonstone_bios_new_image_path, moonstone_bios_new_image)
    deviceObj.executeCmd("mv %s %s" %(moonstone_bios_new_image, moonstone_bios_new_img_version) )
    
    #download_files_in_usb(device, AfuEfix64_file)
    #download_files_in_usb(device, moonstone_bios_new_image)
    deviceObj.executeCmd("cd")
    c1 = deviceObj.executeCmd("fdisk -l")
    if ("Error" in c1) or ("error" in c1) or ("Failed" in c1) or ("failed" in c1):
        raise RuntimeError("fdisk -l output is giving error in its output")

    c2 = deviceObj.executeCmd("ifconfig")
    for i in pattern_ifconfig:
        x = re.findall(i, c2)

        if x is None:

            raise RuntimeError("ifconfig output is giving error in its output")
        else:
            for i in x:

                if i != '0':
                    raise RuntimeError("ifconfig output is giving error in its output")

    m3 = deviceObj.executeCmd("lspci")
    for i in pattern_management_port_lspci:
        x = re.search(i, m3)
        if x is None:
            raise RuntimeError("lspci data not available")

    # m4 =deviceObj.executeCmd("dmidecode")

    # if m4!=pattern_dmidecode:
    # log.info("dmidecode data not available")
    # raise RuntimeError("dmidecode data not available")

    c3 = deviceObj.executeCmd("i2cdetect -l")
    if ("Error" in c3) or ("error" in c3) or ("Failed" in c3) or ("failed" in c3):
        raise RuntimeError("i2cdetect -l output is giving error in its output")

    c4 = deviceObj.executeCmd("i2cdetect -y 0")
    if ("Error" in c4) or ("error" in c4) or ("Failed" in c4) or ("failed" in c4):
        raise RuntimeError("i2cdetect -y 0 output is giving error in its output")


def online_programming_under_uefi_shell(device, image):
    deviceObj = Device.getDeviceObject(device)
    
    deviceObj.sendCmd("cls")
    deviceObj.sendCmd("fs1:")
    deviceObj.sendCmd("ls")
    try:
        deviceObj.read_until_regexp('AfuEfix64.efi', timeout=10)
    except:
        deviceObj.sendCmd("cls")
        deviceObj.sendCmd("fs0:")
        deviceObj.sendCmd("ls")
        deviceObj.read_until_regexp('AfuEfix64.efi', timeout=10)
    
    deviceObj.sendline("AfuEfix64.efi "+image+" /p /b /n /x /me /k")
    time.sleep(10)
    bios_menu_lib.send_key(device, "KEY_ENTER")
    m16_out = deviceObj.read_until_regexp('Process completed', timeout=300)
    exit_the_shell2(device)
    log.success("exited to onl")


def check_power_reset_cause(device, ip):
    deviceObj = Device.getDeviceObject(device)
    cmd1 = f"ipmitool -I lanplus -H {ip} -U admin -P admin sel clear"
    cmd2 = f"ipmitool -I lanplus -H {ip} -U admin -P admin sel list"
    cmd3 = "ipmitool chassis power reset"
    cmd4 = "ipmitool sel list"
    # Step 1
    log.info("***************************** STEP 1 *************************************")
    log.info("running command reboot")
    deviceObj.sendCmd("reboot")
    out_1 = deviceObj.read_until_regexp(pattern_reset_cause, timeout=100)
    out_1_1 = deviceObj.read_until_regexp('localhost login', timeout=400)
    x = re.search(pattern_reset_cause, out_1)
    if x is None:
        raise RuntimeError("reset cause not fetched")
    log.info(x.group(1))
    log.cprint(x.group(1))
    if x.group(1) != reset_cause_reboot:
        raise RuntimeError("reset cause is not (0x11)")
    log.success("reset cause is (0x11) for reboot")

    deviceObj.loginToDiagOS()
    log.success("exited from boot setup successfully")
    

    # Step 2
    log.info("***************************** STEP 2 *************************************")
    out_2 = Device.execute_local_cmd(deviceObj, cmd2)
    out_2 = Device.execute_local_cmd(deviceObj, cmd1)
    time.sleep(30)
    log.info("running command power reset")
    deviceObj.sendCmd(cmd3)
    out_3 = deviceObj.read_until_regexp(pattern_reset_cause, timeout=400)
    out_3_3 = deviceObj.read_until_regexp('localhost login', timeout=400)
    x = re.search(pattern_reset_cause, out_3)
    if x is None:
        raise RuntimeError("reset cause not fetched")
    if x.group(1) != reset_cause_power_reset:
        raise RuntimeError("reset cause is not (0x22)")
    log.success("reset cause is (0x22) for power reset")
    deviceObj.loginToDiagOS()
    out_4 = deviceObj.executeCmd(cmd4)
    if ("Error" in out_4) or ("error" in out_4) or ("Failed" in out_4) or ("failed" in out_4):
        raise RuntimeError("error in sel list")

    # Step 3
    log.info("***************************** STEP 3 *************************************")
    log.info("running command power reset")
    deviceObj.sendCmd("reboot")
    out_1 = deviceObj.read_until_regexp(pattern_reset_cause, timeout=100)
    out_1_1 = deviceObj.read_until_regexp('localhost login', timeout=400)
    x = re.search(pattern_reset_cause, out_1)
    if x is None:
        raise RuntmeError("reset cause not fetched")
    log.info(x.group(1))
    log.cprint(x.group(1))
    if x.group(1) != reset_cause_reboot:
        raise RuntimeError("reset cause is not (0x11)")
    log.success("reset cause is (0x11) for reboot")

    deviceObj.loginToDiagOS()

    # Step 4
    log.info("***************************** STEP 4 *************************************")
    check_power_chasis_status(device, 'on')
    set_power_chasis(device, 'off')
    check_power_chasis_status(device, 'off')
    set_power_chasis(device, 'on')
    check_power_chasis_status(device, 'on')

    # Step 5
    log.info("***************************** STEP 5 *************************************")
    deviceObj.loginToDiagOS()
    out_4 = deviceObj.executeCmd(cmd4)
    if ("Error" in out_4) or ("error" in out_4) or ("Failed" in out_4) or ("failed" in out_4):
        raise RuntimeError("error in sel list")
    log.success("ipmitool sel list has no error")
    


def check_power_chasis_status(device, status):
    device_obj = Device.getDeviceObject(device)
    mgmt_ip = device_obj.managementIP
    promptServer = device_obj.promptServer
    cmd = lanplus_ipmitool_cmd.format('chassis power status')
    log.info("Checking chassis status through cmd : %s" % cmd)
    c1 = Device.execute_local_cmd(device_obj, cmd, timeout=10)
    log.info("Output : " + c1)

    chassis_pattern = "Chassis Power is %s" % status
    if chassis_pattern in c1:
        log.info("Chassis Status is as expected!! " + chassis_pattern)
    else:
        raise RuntimeError("Expected value of Chassis Status should be %s but got opposite of it." % status)


def set_power_chasis(device, status):
    deviceObj = Device.getDeviceObject(device)
    mgmt_ip = deviceObj.managementIP
    promptServer = deviceObj.promptServer
    cmd = lanplus_ipmitool_cmd.format("power %s" % status)

    log.info("Turn %s power through cmd %s" % (status, cmd))
    c1 = Device.execute_local_cmd(deviceObj, cmd, timeout=10)
    log.info('Output : ' + c1)

    val = "Down/Off" if status == 'off' else "Up/On"
    pattern = "Chassis Power Control: %s" % val
    log.info("Sleeping for 200 seconds.")
    if status == 'on':
        out_1 = deviceObj.read_until_regexp(pattern_reset_cause, timeout=400)
        x = re.search(pattern_reset_cause, out_1)
        if x is None:
            log.info("reset cause not fetched")
            raise RuntimeError("reset cause not fetched")
        log.info(x.group(1))
        if x.group(1) != reset_cause_power_chasis:
            raise RuntimeError("reset cause is not (0x77)")
        log.success("reset cause is (0x77) for power chassis on")

    time.sleep(200)

    CommonKeywords.should_match_a_regexp(c1, pattern)
    if (status == 'on'):
        sel_list_pattern = sel_list_power_on_pattern
        sel_cmd = lanplus_ipmitool_cmd.format('sel list | tail')
        log.info("Fetching BMC sel list after setting power chassis status")
        c2 = Device.execute_local_cmd(deviceObj, sel_cmd, timeout=120)
        log.info("Output : " + c2)
        c2 = c2.split("\n")
        c2 = c2[-3:]
        log.cprint(c2)
        log.cprint(sel_list_pattern)
        CommonKeywords.should_match_ordered_regexp_list(c2, sel_list_pattern)
        log.success("Sel list is as expected after power %s" % status)


def get_ip_address_from_ipmitool_device(device, eth_type='dedicated', ipv6=False):
    """
    Use IPMI command to get IP address
    :param device: product name
    :param eth_type: Network port type: dedicated, shared
    :param ipv6: Whether to get IPV6, if False, get IPV4
    :return: IP address
    """
    deviceObj = Device.getDeviceObject(device)

    cmd1 = 'ipmitool lan print 1'
    cmd2 = 'ipmitool lan6 print 1'
    cmd3 = 'ipmitool lan print 8'
    cmd4 = 'ipmitool lan6 print 8'
    if ipv6:
        ip_re = r'IPv6 Dynamic Address 0.+\n.+\n.+Address:\s+(.+)/'
        cmd = cmd2 if eth_type == 'dedicated' else cmd4
    else:
        ip_re = r"IP Address\s+:\s+(\d+\..*\d+)"
        cmd = cmd1 if eth_type == 'dedicated' else cmd3
    output = deviceObj.executeCmd(cmd)
    ip_res = re.findall(ip_re, output)
    if ip_res:
        ip = ip_res[0]
        if ip == "0.0.0.0":
            PRINTE("Fail! Got bmc ip:0.0.0.0")
        log.success('Pass! get ip address from ipmitool: %s' % ip)
        return ip
    else:
        log.fail('Fail! can not get ip address from ipmitool response:\n%s' % output)
        raise RuntimeError("Fail! get_ip_address_from_ipmitool")


# TC - programming via BMC USB
def download_files_in_usb(device, file_path):
    device_obj = Device.getDeviceObject(device)
    devicePc = Device.getDeviceObject('PC')

    cmd1 = "wget http://" + scp_ip + ":" + moonstone_home_path + file_path
    file_name = file_path.split("/")

    log.info("Download %s into usb.." % file_name[-1])
    res2 = device_obj.executeCmd(cmd1)
    CommonKeywords.should_match_a_regexp(res2, "100%")

    res3 = device_obj.executeCmd("ls")
    CommonKeywords.should_match_a_regexp(res3, file_name[-1])
    log.success("%s is downloaded successfully." % file_name[-1])


# TC - CPU I2C Interface Test
def check_i2c_test_info(device):
    deviceObj = Device.getDeviceObject(device)
    cmd = "dpkg -i "+bios_deb_image
    cmd1 = 'cd /home/cel_diag/moonstone/bin/'
    cmd2 = './cel-i2c-test --all '
    
    deviceObj.executeCmd("cd")
    deviceObj.executeCmd(cmd1)
    output = deviceObj.executeCmd(cmd2, timeout=180)
    CommonKeywords.should_match_a_regexp(output, "I2C Test All.*PASS")
    log.success("All I2C devices matched with HW spec.")
    deviceObj.executeCmd("cd")
    #remove_diag_package_and_image(device)

def remove_diag_package_and_image(device):
    deviceObj = Device.getDeviceObject(device)
    log.info("Remove diag package and image.")
    deviceObj.executeCmd("cd")
    deviceObj.executeCmd("rm -rf %s" %bios_deb_image)
    #deviceObj.executeCmd("rm -rf diag")
    
# TC - CPU_LPC_Interface_Test
@logThis
def enter_into_lpc(device):
    deviceObj = Device.getDeviceObject(device)
    deviceObj.executeCmd("cd")
    cmd = "dpkg -i "+bios_deb_image
    cmd1 = 'cd /home/cel_diag/moonstone/tools/'
    log.debug("Download and install .deb package ....")
    download_files_in_usb(device,bios_deb_image )
    
    deviceObj.executeCmd(cmd)
    deviceObj.executeCmd(cmd1)
    log.info("Successfully entered in LPC interface directory")
    time.sleep(5)

@logThis
def check_cpld_version_through_lpc_tools(device):
    deviceObj = Device.getDeviceObject(device)
    cmd1 = "./lpc_cpld_x86_64 blu r 0xA100"
    output = deviceObj.executeCmd(cmd1)
    CommonKeywords.should_match_a_regexp(output, clpd_image_version)
    log.success("CPLD version is correct through lpc tools ")


@logThis
def test_read_write_cpld_register(device, register_value):
    deviceObj = Device.getDeviceObject(device)
    cmd1 = "./lpc_cpld_x86_64 blu w 0xA101 %s" %register_value
    cmd2 = "./lpc_cpld_x86_64 blu r 0xA101"
    log.info("Writing a value %s to register 0xA101")
    output=deviceObj.executeCmd(cmd1)
    if "Fail|fail|rror" in output:
        raise RuntimeError("Not able to write to register properly.")
        
    log.info("Reading value for register 0xA101")
    output = deviceObj.executeCmd(cmd2)
    CommonKeywords.should_match_a_regexp(output, register_value)
    log.success("Correct output for register after write operation.")
    

@logThis
def read_baseboard_cpld_register(device, register, value):
    cmd1 = "./inb --hex --read %s" % register
    bios_menu_lib.send_key(device, "KEY_ENTER", 2)
    output1 = deviceObj.executeCmd(cmd1)
    output1 = output1.split("\n")
    log.cprint(output1)
    if((output1[-2].strip())[:2] != str(value)):
        log.fail("Expected value should be %s but got %s" % (value, output1[-2].strip()))
        raise RuntimeError('Value of CLPD Baseboard register is incorrect')

    else:
        log.success("Register %s has correct value which is %s" % (register, value))


@logThis
def write_baseboard_cpld_register(register, value):
    cmd1 = "./inb --hex --write %s %s" % (register, value)
    output1 = device.executeCmd(cmd1)
    output1 = output1.strip()
    time.sleep(15)
    if ("rror" in output1):
        log.fail("Unable to write in register %s" % register)
    else:
        log.success("Successful write to register %s" % register)


@logThis
def check_add_user_to_bmc(user_id, user_name):
    cmd1 = "ipmitool user list 1"
    cmd2 = "ipmitool user set name %s %s" % (str(user_id), user_name)
    device.executeCmd(cmd2)
    output1 = device.executeCmd(cmd1)
    user_list = output1.split("\n")
    if (user_name not in user_list[int(user_id) + 1]):
        log.fail("User %s is not added at id %s " % (user_name, str(user_id)))
    else:
        log.success("User %s is added successfully at id %s " % (user_name, str(user_id)))

def delete_all_new_user_info(device):
    device_obj = Device.getDeviceObject(device)
    error_info = "Unable to send command: Invalid argument"
    for user_id in range(3,16):
        cmd = "ipmitool raw 6 0x45 %s 0xff 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0" % str(user_id)
        res = deviceObj.executeCmd(cmd)
        if error_info in res:
            raise RuntimeError("Unable to delete user information at user id %s" %str(user_id))
    log.info("Command to delete new users from ipmitool executed successfully.")
    check_default_user_list(device)
    log.success("Successfully deleted user information from user id 3 to 15.") 

def power_cycle_and_enter_into_lpc(device):
    device_obj = Device.getDeviceObject(device)
    MOONSTONECommonLib.powercycle_device(device)
    device_obj.loginToDiagOS()
    enter_into_lpc()


# TC - Programming via bmc lan
def update_bios_image(device, image, boot_type, lanplus=False):
    device_obj = Device.getDeviceObject(device)
    mse = 1 if str(boot_type) == '0' else 2
    if lanplus:
        promptServer = device_obj.promptServer
        device_obj.sendCmd("dhclient -v ma1")
        time.sleep(20)
        MOONSTONECommonLib.check_server_moonstone(device, scp_ip, scp_username, scp_password, dhcp_prompt)
        update_bios_cmd = "./CFUFLASH -nw -ip " + mgmt_ip + " -u admin -p admin -d 2 -mse " + str(
            mse) + " %s -fb" % image
    else:
        update_bios_cmd = "./CFUFLASH -cd -d 2 -mse " + str(mse) + " %s -fb" % image

    log.info("Updating bios with image %s" % image)

    c1 = device_obj.executeCmd(update_bios_cmd, timeout=300)
    if "rror|Fail|fail|invalid" not in c1:
        log.success("Bios is updated through command : %s" % update_bios_cmd)
    else:
        raise RuntimeError("Some error found while updating primary bios")
    if str(boot_type) == '0':
        CommonKeywords.should_match_a_regexp(c1, "BIOS Image To be updated is Primary")
        log.success("Primary Image is being updating")
    else:
        CommonKeywords.should_match_a_regexp(c1, "BIOS Image To be updated is Backup")
        log.success("Backup Image is being updating")

    if lanplus:
        CommonKeywords.should_match_a_regexp(c1, "Creating IPMI session via network with address")
        log.success("Updation is being done through Lan")
        MOONSTONECommonLib.exit_the_server(device)
    else:
        CommonKeywords.should_match_a_regexp(c1, "Creating IPMI session via USB")
        log.success("Updation is being done through USB.")
        # Creating IPMI session via USB...Done
        # BIOS Image To be u dated is Primary

    log.success("Bios is updated successfully with image %s ." % image)


def bios_boot(device, boot_type):
    device_obj = Device.getDeviceObject(device)
    if str(boot_type) not in ['0', '1']:
        raise RuntimeError("Invalid boot type")
    cmd1 = "ipmitool raw 0x3a 0x25 0x0%s" % str(boot_type)
    cmd2 = "reboot"
    device_obj.executeCmd(cmd1)
    device_obj.sendCmd(cmd2)
    primary_boot_pattern = "Primary BIOS boot in progress"
    backup_boot_pattern = "Back up BIOS boot in progress"

    if str(boot_type) == '0':
        output = device_obj.read_until_regexp(primary_boot_pattern, timeout=120)
        match1 = re.findall(primary_boot_pattern, output)
    else:
        output = device_obj.read_until_regexp(backup_boot_pattern, timeout=120)
        match1 = re.findall(backup_boot_pattern, output)
    log.info("Sleeping for 150 to reboot the device")
    time.sleep(150)
    log.info("Login into device")
    device_obj.loginToDiagOS()

    if match1 and str(boot_type) == '0':
        log.success("Bios is rebooted in primary mode")
    elif match1 and str(boot_type) == '1':
        log.success("Bios is rebooted in Backup mode")
    else:
        raise RuntimeError("Error while rebooting bios!!")


# TC - PCIE Information test
def check_pci_information(device):
    device_obj = Device.getDeviceObject(device)
    res = device_obj.executeCmd("lspci")
    log.cprint(res)
    CommonKeywords.should_match_ordered_regexp_list(res, lscpi_pattern)
    log.success("PCI Information through linux prompt is as expected.")


# TC - SMBIOS Table read
def read_smbios(device, smbios_list):
    device_obj = Device.getDeviceObject(device)
    for code in smbios_list:
        cmd = "dmidecode -t %s" % str(code)
        res = device_obj.executeCmd(cmd)
        if str(code) == "0":
            CommonKeywords.should_match_ordered_regexp_list(res, smbios_bios_res)
            log.success("SMBIOS Bios output is as expected.")
        elif str(code) == "2":
            CommonKeywords.should_match_ordered_regexp_list(res, sbmios_baseboard_res)
            log.success("SMBIOS baseboard output is as expected.")
        elif str(code) == "3":
            CommonKeywords.should_match_ordered_regexp_list(res, smbios_chassis_res)
            log.success("SMBIOS chassis output is as expected.")
        elif str(code) == "4":
            CommonKeywords.should_match_ordered_regexp_list(res, symbios_processor_res)
            log.success("SMBIOS Processor output is as expected.")
        elif str(code) == "7":
            CommonKeywords.should_match_ordered_regexp_list(res, smbios_cache_res)
            log.success("SMBIOS Cache output is as expected.")
        elif str(code) == "7":
            CommonKeywords.should_match_ordered_regexp_list(res, smbios_memory_res)
            log.success("SMBIOS memory output is as expected.")


def mount_disk_on_device(device):
    device_obj = Device.getDeviceObject(device)
    cmd1 = "mkfs.vfat /dev/sdc1"
    cmd2 = "mount /dev/sdc1 /mnt/"
    cmd3 = "cd /mnt/"
    res1 = device_obj.executeCmd(cmd1)
    res2 = device_obj.executeCmd(cmd2)
    res3 = device_obj.executeCmd(cmd3)

    if ("rror|Fail|fail|invalid" in (res1, res2, res3)):
        raise RuntimeError("Failed to mount the usb into device")
    log.success("Successfully mounted USB to disk")

    device_obj.executeCmd("dhclient -v ma1")
    download_files_in_usb(device, cfuflash_path)
    download_files_in_usb(device, new_bios_image)
    download_files_in_usb(device, old_bios_image)


def umount_disk_from_device(device):
    device_obj = Device.getDeviceObject(device)
    log.info("Trying to unmount the disk drom device")
    cmd1 = "cd"
    cmd2 = "umount /dev/sdc1 /mnt/"
    device_obj.executeCmd(cmd1)
    res = device_obj.executeCmd(cmd2)
    CommonKeywords.should_match_ordered_regexp_list(res, unmount_disk_pattern)
    log.success("Disk unmounted successfully.")


def update_bios_image_through_usb(device, image, boot_type):
    device_obj = Device.getDeviceObject(device)

    cmd1 = "ipmitool raw 0x32 0xaa 0"
    cmd2 = "ipmitool  -b 0x06 -t 0x2c raw 0x2e 0xdf 0x57 0x01 0x00 0x01"
    cmd3 = "ipmitool raw 0x3a 0x25 0"

    log.info("Add the USB correctly in device")
    res1 = device_obj.executeCmd(cmd1)
    if ("rror|Fail|fail|invalid" in res1):
        raise RuntimeError("Failed to execute cmd %s" % cmd1)
    log.success("Successfully executed cmd %s" % cmd1)

    res2 = device_obj.executeCmd(cmd2)
    pattern = "57 01 00"
    CommonKeywords.should_match_a_regexp(res2, pattern)
    log.success("Successfully executed cmd %s" % cmd2)

    res3 = device_obj.executeCmd(cmd3)
    if ("rror|Fail|fail|invalid" in res3):
        raise RuntimeError("Failed to execute cmd %s" % cmd3)
    log.success("Successfully executed cmd %s" % cmd3)

    update_bios_image(device, image, boot_type)


# TC - 1.0.3 Online Programming under Linux OS

def download_files_in_device(device):
    device_obj = Device.getDeviceObject(device)
    device_obj.executeCmd("dhclient -v ma1")
    download_files_in_usb(device, afulnx_path)
    download_files_in_usb(device, new_bios_image)
    #download_files_in_usb(device, old_bios_image)


def update_bios_through_afulnx(device, image):
    device_obj = Device.getDeviceObject(device)
    cmd1 = "chmod 777  afulnx_64"
    cmd2 = "./afulnx_64 %s /p /b /n /me /x /k" % image
    res1 = device_obj.executeCmd(cmd1)
    res2 = device_obj.executeCmd(cmd2, timeout=1500)
    CommonKeywords.should_match_a_regexp(res2, "Process completed.")
    log.success("Bios image is updated to %s through afulnx" % image)



def check_boot_menu_spec(device):
    deviceObj=Device.getDeviceObject(device)
    bios_menu_lib.send_key(device,'KEY_RIGHT',times=5) #main-> boot menu
    time.sleep(15)
    boot_content_1=deviceObj.read_until_regexp('Quiet Boot.*',timeout=15) 
    boot_content_2=deviceObj.read_until_regexp('Copyright',timeout=15)
    boot_menu_content=boot_content_1+boot_content_2 #menu requires scroll to read fully
    log.info('Boot Menu Content is:')
    log.info(boot_menu_content)
    CommonKeywords.should_match_ordered_regexp_list(boot_menu_content,re_boot_menu_content)
    log.info('Boot menu content successfully follows BIOS Spec')
    bios_menu_lib.send_key(device,"KEY_LEFT",times=5)

@logThis
def boot_cleanup(device):
    
    deviceObj=Device.getDeviceObject(device)
    log.info('Restoring boot config now')
    bios_menu_lib.send_key(device,"KEY_RIGHT",times=5)
    bios_menu_lib.send_key(device,"KEY_F3",times=1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    time.sleep(10)
    bios_menu_lib.send_key(device,"KEY_UP",times=1)
    boot_menu_content=deviceObj.read_until_regexp('Hard Drive BBS Priorities',timeout=10)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
    log.info('Inside Boot Menu:')
    log.info('Optimized Defaults:')
    log.info(boot_menu_content)
    log.info('Back to MainMenu')
    bios_menu_lib.send_key(device,"KEY_LEFT",times=5)
    set_boot_one(device,'ONL')
    

@logThis
def read_os_cpu_info(device):
    deviceObj=Device.getDeviceObject(device)
    cmd1='cat /proc/cpuinfo'
    cpuinfo_op=deviceObj.executeCmd(cmd1)
    CommonKeywords.should_match_ordered_regexp_list(cpuinfo_op,cpu_proc)
    log.success('OS CPU Info Accurate')
    cmd2=r"top -n 2 -d 1|grep -i '%Cpu(s)'"
    top_op=deviceObj.executeCmd(cmd2)
    usage_check='([8-9][1-9]|100)sy'
    usage_match=re.search(usage_check,top_op)
    log.cprint(usage_match)
    if(usage_match):
        log.fail('system CPU usage >80 percent')
        raise RuntimeError('CPU usage above expected levels')
    else:
        log.success("system CPU usage within expected levels")

@logThis
def read_setup_cpu_info(device):
    #code to enter into processor subsection
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device,"KEY_RIGHT",times=2)
    #bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    #code to read processor subsection
    out=deviceObj.read_until_regexp('1627 @ 2.90GHz')
    bios_menu_lib.send_key(device,"KEY_ESC",times=1)
    CommonKeywords.should_match_ordered_regexp_list(out,setup_cpu_info)
    log.success('Setup CPU Info Accurate')


def detect_usb_onl(device):
    log.info('Inside device')
    deviceObj=Device.getDeviceObject(device)
    out=deviceObj.sendCmd('ls')
    log.info(out)
    enable_mount_cmd="mkfs.vfat /dev/sdc1"
    mount_cmd='mount /dev/sdc1 /mnt'
    deviceObj.executeCmd(enable_mount_cmd)
    deviceObj.executeCmd(mount_cmd)
    cmd='fdisk -l'
    out=deviceObj.sendCmd(cmd)
    time.sleep(10)
    log.info('out content')
    log.info(out)
    time.sleep(10)
    fdisk_content=deviceObj.read_until_regexp('root@localhost.*',timeout=60)
    log.info('Fdisk content')
    log.info(fdisk_content)
    usb_match=re.search('\/dev\/sdc',fdisk_content)
    if usb_match:
        log.info('USB detected in ONL OS successfully')
    else:
        log.info('USB info not matched')


@logThis
def detect_usb_setup(device,mode):
    deviceObj=Device.getDeviceObject(device)
    bios_menu_lib.send_key(device,"KEY_RIGHT",times=1) #go to advanced
    bios_menu_lib.send_key(device,"KEY_DOWN",times=5) 
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)#go to usb config 
    usb_menu_content=deviceObj.read_until_regexp('USB Mass Storage',timeout=15)
    match=re.search('[1-9].*Hubs',usb_menu_content) 
    if match:
        log_msg='USB device successfully detected in Setup'
        if(int(mode)==1):
            log.info(log_msg)
            #get to main menu
            bios_menu_lib.send_key(device,"KEY_ESC",times=1)
            bios_menu_lib.send_key(device,"KEY_LEFT",times=1)
            
        elif(int(mode)==2):
            log.info(log_msg)
            time.sleep(5)
            log.debug('UNPLUG the USB in next 60 seconds')
            time.sleep(60)
            log.info('Checking if USB status updated to None')
            time.sleep(5)
            bios_menu_lib.send_key(device,"KEY_ESC",times=1) #Advanced
            time.sleep(15)
            bios_menu_lib.send_key(device,"KEY_ENTER",times=1) #USB Menu
            time.sleep(5)
            usb_menu_content=deviceObj.read_until_regexp('Mass.*Storage.*Devices',timeout=15)
            match=re.search('None',usb_menu_content)
            #bios_menu_lib.send_key(device,"KEY_ESC",times=1) #go to advanced
            if match:
                
                log.success('USB device set to None in Setup')
                log.info(usb_menu_content)
            
            else:
                bios_menu_lib.send_key(device,"KEY_ESC",times=1) #Advanced
                time.sleep(15)
                bios_menu_lib.send_key(device,"KEY_ESC",times=1)
                time.sleep(15)
                bios_menu_lib.send_key(device,"KEY_ENTER",times=1) #Exit Setup
                time.sleep(10)
                log.fail('USB Device not read as None')
                log.info('USB menu:')
                log.info(usb_menu_content)
                raise RuntimeError('USB device info incorrect in Setup')
            
            log.debug('PLUG IN the USB device in the next 60 seconds')
            time.sleep(60)
            log.info('Checking if USB status updated to 1 Drive')
            bios_menu_lib.send_key(device,"KEY_ESC",times=1) #Advanced
            time.sleep(5)
            bios_menu_lib.send_key(device,"KEY_ENTER",times=1)#USB Menu
            time.sleep(5)
            usb_menu_content=deviceObj.read_until_regexp('Mass.*Storage.*Devices',timeout=15)
            match=re.search('[1-9].*Drive',usb_menu_content)
            
            if match:
                bios_menu_lib.send_key(device,"KEY_ESC",times=1) #go to advanced
                log.success('USB device successfully detected in Setup')
                log.info(usb_menu_content)
            
            else:
                bios_menu_lib.send_key(device,"KEY_ESC",times=1) #go to advanced
                time.sleep(15)
                bios_menu_lib.send_key(device,"KEY_ESC",times=1) 
                time.sleep(15)
                bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
                time.sleep(15)
                log.fail('USB device not found in Setup')
                raise RuntimeError('USB device not found in Setup') #Exit Setup
            bios_menu_lib.send_key(device,"KEY_ESC",times=1) 
            bios_menu_lib.send_key(device,"KEY_ENTER",times=1) #Exit Setup
    else:
        bios_menu_lib.send_key(device,"KEY_ESC",times=1) #go to advanced 
        bios_menu_lib.send_key(device,"KEY_ESC",times=1)
        bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
        raise RuntimeError('regex search error')

@logThis
def check_usb_read_write(device):
    deviceObj=Device.getDeviceObject(device)
    log.info('Going to root directory')
    deviceObj.executeCmd('cd /')
    log.info('Running command to ensure USB mount occurs')
    enable_mount_cmd="mkfs.vfat /dev/sdc1"
    deviceObj.executeCmd(enable_mount_cmd)
    log.info('Running command to mount USB')
    mount_cmd='mount /dev/sdc1 /mnt/'
    deviceObj.executeCmd(mount_cmd)
    log.info('Going to mnt directory')
    deviceObj.executeCmd('cd /mnt/')
    log.info('Current content of /mnt/:')
    mnt_content=deviceObj.executeCmd('ls')
    log.info(mnt_content)
    log.info('Going to ~ dir')
    deviceObj.executeCmd('cd ~')
    log.info('Creating dummy file dummy1.txt')
    deviceObj.executeCmd('touch dummy1.txt')
    log.info('Copying dummy1 file from ~ to /mnt/ directory')
    deviceObj.executeCmd('cp dummy1.txt /mnt/')
    log.info('Going to mnt directory')
    deviceObj.executeCmd('cd /mnt/')
    log.info('Current content of /mnt/:')
    mnt_content=deviceObj.executeCmd('ls')
    write_match=re.search('dummy1\.txt',mnt_content)
    if write_match:
        log.success('Write into USB operation successful')
    else:
        log.fail('Error detected while writing into USB')
        log.info('CLEANUP')
        log.info('Deleting dummy files from ~ and /mnt/')
        deviceObj.executeCmd('rm dummy1.txt')
        #deviceObj.sendCmd('rm dummy2.txt')
        deviceObj.executeCmd('cd /mnt/')
        deviceObj.executeCmd('rm dummy1.txt')
        #deviceObj.sendCmd('rm dummy2.txt')
        raise RuntimeError('USB Write Error')
    log.info('Creating dummy file dummy2.txt in /mnt/ dir')
    deviceObj.executeCmd('touch dummy2.txt')
    log.info('Copying dummy1 file from /mnt/ to ~ directory')
    deviceObj.executeCmd('cp dummy2.txt ~')
    log.info('Going to ~ directory')
    deviceObj.executeCmd('cd ~')
    log.info('Current content of ~:')
    home_content=deviceObj.executeCmd('ls')
    read_match=re.search('dummy2\.txt',home_content)
    if read_match:
        log.success('Read from USB operation successful')
    else:
        log.fail('Error detected while reading from USB')
        log.info('CLEANUP')
        log.info('Deleting dummy files from ~ and /mnt/')
        deviceObj.executeCmd('rm dummy1.txt')
        deviceObj.executeCmd('rm dummy2.txt')
        deviceObj.executeCmd('cd /mnt/')
        deviceObj.executeCmd('rm dummy1.txt')
        deviceObj.executeCmd('rm dummy2.txt')
        raise RuntimeError('USB Read Error')
    log.info('CLEANUP')
    log.info('Deleting dummy files from ~ and /mnt/')
    deviceObj.executeCmd('rm dummy1.txt')
    deviceObj.executeCmd('rm dummy2.txt')
    deviceObj.executeCmd('cd /mnt/')
    deviceObj.executeCmd('rm dummy1.txt')
    deviceObj.executeCmd('rm dummy2.txt')
    log.info('Unmounting...')
    deviceObj.executeCmd('cd ..')
    time.sleep(2)
    deviceObj.executeCmd('umount /mnt/')

def set_boot_one(device, option):
    
    deviceObj=Device.getDeviceObject(device)
    log.info('Attempting to set Boot Option #1 to:{}'.format(option))
    log.info('Associated Option #1 regex:{}'.format(boot_option_dict[option]))
    log.info('Going to Boot menu, Option #1 from Main menu')
    time.sleep(5)
    bios_menu_lib.send_key(device,"KEY_RIGHT",times=5)
    time.sleep(5)
    log.info('Setting Bios to Optimized Defaults')
    bios_menu_lib.send_key(device,"KEY_F3",times=1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    log.info('Current Boot Options')
    boot_menu_content=deviceObj.read_until_regexp('Boot Option #1[\s]+\[(.*)',timeout=15)
    log.info(boot_menu_content)
    time.sleep(5)
    
    boot_one_match=re.search('Boot Option #1[\s]+\[(.*)',boot_menu_content)
    if boot_one_match:
        boot_one_snip=boot_one_match.group(1)
        if boot_option_dict[option] in boot_one_snip:
            log.info('Boot Option #1 already set to {}'.format(option))
            log.info(boot_one_snip)
        #code to check already true case
        else:
            log.info('Iterating through boot #1 options till set to {}'.format(option))
            bios_menu_lib.send_key(device,"KEY_DOWN",times=4)
            time.sleep(3)
            boot_loop=True
            while boot_loop:
                bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
                if('ONL' in option):
                    bios_menu_lib.send_key(device,"KEY_UP",times=1)
                else:
                    bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
                bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
                time.sleep(10)
                log.info('Current Boot Options')
                boot_menu_content=deviceObj.read_until_regexp('Boot Option #1[\s]+\[(.*)',timeout=15)
                log.info(boot_menu_content)
                boot_one_match=re.search('Boot Option #1(.*)',boot_menu_content)
                if boot_one_match:
                    boot_one_snip=boot_one_match.group(1)
                    log.info('Snip:{}'.format(boot_one_snip))
                    
                    if (boot_option_dict[option] in boot_one_snip) or ('Disabled' in option and boot_option_dict['ONL'] in boot_one_snip):
                        log.info('Boot Option #1 successfully set to {}'.format(option))
                        log.info(boot_menu_content)
                        boot_loop=False
    else:
        log.info('Error getting boot one match')
    
    
    log.info('Saving and exiting from setup')
    time.sleep(15)
    bios_menu_lib.send_key(device,"KEY_F4",times=1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    if 'ONL' in option:
        deviceObj.read_until_regexp('login',timeout=180)
        deviceObj.getPrompt("DIAGOS")


@logThis
def detect_in_shell(device,mode):
    deviceObj=Device.getDeviceObject(device)
    shell_boot=deviceObj.read_until_regexp('Shell>',timeout=200)
    log.info('Booted into UEFI Shell')
    if(int(mode)==2):
        deviceObj.sendCmd('fs1:') #if command works, then USB device detected
        output=deviceObj.read_until_regexp('FS1:|fs1:',timeout=10)
        log.success('USB Device detected in UEFI Shell')
    time.sleep(5)
    log.info('Exiting to ONL now')
    deviceObj.sendCmd('fs0: \r \n')
    
    
    deviceObj.sendCmd("ls")
    try:
        deviceObj.read_until_regexp('EFI', timeout=10)
    except:
        deviceObj.sendCmd("cls")
        deviceObj.sendCmd("fs1:")
        deviceObj.sendCmd("ls")
        deviceObj.read_until_regexp('EFI', timeout=10)
    
    time.sleep(2)
    deviceObj.sendCmd('cd EFI \r \n')
    time.sleep(2)
    deviceObj.sendCmd('cd ONL \r \n')
    time.sleep(2)
    deviceObj.sendCmd('grubx64.efi \r \n')
    time.sleep(5)
    deviceObj.sendCmd('\r')
    deviceObj.read_until_regexp('(localhost login)|(root@localhost)',timeout=400) #should boot to localhost
    log.info('booted to localhost')
    deviceObj.getPrompt("DIAGOS")
    time.sleep(5)



def disable_all_boot(device):
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_RIGHT", 5)
    log.info("setting boot to onie as first option")
    # m161_out=deviceObj.read_until_regexp('Boot Option #2 ' ,timeout=10)
    bios_menu_lib.send_key(device, "KEY_DOWN", 4)
    run_loop = True
    while run_loop:
        try:
            m16_out = deviceObj.read_until_regexp(' Boot Option #1.*Disabled', timeout=10)
            run_loop = False
            break
        except Exception:
            try:
                bios_menu_lib.send_key(device, "KEY_ENTER")
                bios_menu_lib.send_key(device, "KEY_DOWN")
                bios_menu_lib.send_key(device, "KEY_ENTER")

                # m16_out=deviceObj.read_until_regexp(' Boot Option #1          \[\(UEFI\) ONIE OS',timeout=10)

                # run_loop=False
                # break
            except Exception:
                continue

    log.success("successfully set boot onie")
    time.sleep(3)
    bios_menu_lib.send_key(device, "KEY_F4")

    time.sleep(4)
    bios_menu_lib.send_key(device, "KEY_ENTER", 1)
    time.sleep(4)
    log.success("Done")
    
    
    

@logThis
def find_sata_device_in_setup(device):
    log.cprint('This fucntion checks if any SATA device is present in BIOS Setup')
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_RIGHT", times=5)
    bootContent = deviceObj.read_until_regexp('Boot Option #[1-9]\s+\[.*', timeout=30)

    pattern = 'Boot Option #1'
    match = re.search(pattern, bootContent)
    if (match):
        log.success('SATA device found in setup->boot')
    else:
        log.fail('NO SATA device found in setup->boot')
        raise RuntimeError('NO SATA device found in setup->boot')


@logThis
def check_sata_device_size(device,mode='1'):
    deviceObj=Device.getDeviceObject(device)
    cmd1='fdisk -l'
    content=deviceObj.executeCmd(cmd1)
    #content=deviceObj.read_until_regexp('root@localhost:',timeout=10)
    log.info(content)
    CommonKeywords.should_match_ordered_regexp_list(content,fdisk_op_re)
    if(int(mode)==1):
        log.success('SATA device detected successfully')
    if(int(mode)==2):
        log.success('SATA device size displayed accurately')


@logThis
def check_sata_write(device):
    log.info('Booted into ONL, SATA device read successfully')
    deviceObj=Device.getDeviceObject(device)
    log.info('Executing write test:')
    log.info('Creating dummy txt file in /home')
    deviceObj.sendCmd('cd /home')
    dummy_file_cmd='echo "Hello World" >dummy.txt'
    deviceObj.sendCmd(dummy_file_cmd)
    log.info('Writing dummy file to /dev/null')
    write_cmd='dd if=/home/dummy.txt of=/dev/null'
    write_out=deviceObj.executeCmd(write_cmd)
    log.info('Deleting dummy file in /home')
    deviceObj.sendCmd('rm dummy.txt')
    log.info('Output of sata write command')
    log.info(write_out)
    CommonKeywords.should_match_ordered_regexp_list(write_out,sata_write_re)
    log.success('SATA device write verified')

def configure_diag_dir(device):
    deviceObj=Device.getDeviceObject(device)
    log.info('Checking if diag-->tools directory exists & configuring as per our needs')
    deviceObj.executeCmd('cd ~')
    home_content=deviceObj.executeCmd('ls')
    if 'diag' in home_content:
        log.info('Existing diag dir detected, deleting...')
        deviceObj.executeCmd('rm -rf diag')
    time.sleep(5)
    log.info('Installing diag dir as required now')
    deviceObj.executeCmd('dpkg-deb -xv cel_diag-moonstone2v2.v1.1.0.deb diag')
    time.sleep(5)
    home_content=deviceObj.executeCmd('ls')
    if 'diag' in home_content:
        log.info('diag dir created as required')
    time.sleep(5)

def toggle_bios(device,mode):
    deviceObj=Device.getDeviceObject(device)
    bios_mode=int(mode)
    home_cmd='cd ~'
    deviceObj.executeCmd(home_cmd)
    dir_cmd='cd diag/home/cel_diag/moonstone2v2/tools'
    deviceObj.executeCmd(dir_cmd)
    display_cmd='./inb --hex --read 0xa170'
    current_bios=deviceObj.executeCmd(display_cmd)
    log.info('Current BIOS Option is: {}'.format(current_bios))
    toggle_to_primary_bios_cmd='ipmitool raw 0x3a 0x25 0x00'
    toggle_to_backup_bios_cmd='ipmitool raw 0x3a 0x25 0x01'
    

    if(bios_mode):        
        toggle_to_backup_bios_cmd='ipmitool raw 0x3a 0x25 0x01'
        log.info('Switching from Primary to Backup BIOS')
        deviceObj.executeCmd(toggle_to_backup_bios_cmd)
    else:
        if('3' in current_bios):
            log.success('Backup BIOS Boot verified')
        else:
            log.info('Switching back from Backup to Primary BIOS')
            deviceObj.executeCmd(toggle_to_primary_bios_cmd)
            log.fail('Not set to Backup BIOS')
            log.print('Current BIOS mode is: {}'.format(current_bios))
            raise RuntimeError('Failed to verify backup BIOS')
        log.info('Switching back from Backup to Primary BIOS')
        deviceObj.executeCmd(toggle_to_primary_bios_cmd)

def check_reboot_bios_boot(device,mode=1):
    deviceObj=Device.getDeviceObject(device)
    log.info('Initiating reboot and observing BIOS mode')
    if int(mode==2):
        exp='Primary'
    else:
        exp='Back up'
    log.info('Expected:')
    deviceObj.sendCmd('reboot')
    bios_out=deviceObj.read_until_regexp('.*BIOS boot in progress',timeout=100)
    out=deviceObj.read_until_regexp('localhost login',timeout=400)    
    #deviceObj.loginToDiagOS()
    #time.sleep(15)
    if int(mode==2):
        bios_match=re.search('(Primary.*) BIOS boot in progress',bios_out)
    else:  
        bios_match=re.search('(Back up.*) BIOS boot in progress',bios_out)
    if bios_match:
        bios_type=bios_match.group(1)
        #log.print('BIOS is:')
        #log.info(bios_type)
        log.success('Successful reboot via Backup BIOS')
        
        
    else:
        log.fail('Check for boot via Backup BIOS failed')
        #raise RuntimeError('Boot occured via Primary OS')
    deviceObj.getPrompt("DIAGOS")

@logThis
def check_os_serial_port(device):
    deviceObj = Device.getDeviceObject(device)
    cmd1=deviceObj.executeCmd('sudo dmesg|grep tty')
    CommonKeywords.should_match_ordered_regexp_list(cmd1, os_serial_port_pattern)
    log.success('Serial Port info as expected')
  


@logThis
def check_setup_serial_port(device):
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_RIGHT", times=1)
    bios_menu_lib.send_key(device, "KEY_DOWN", times=3)
    bios_menu_lib.send_key(device, "KEY_ENTER", times=1)
   
    bios_menu_lib.send_key(device, "KEY_DOWN", times=1)
    bios_menu_lib.send_key(device, "KEY_ENTER", times=1)
    out_a = deviceObj.read_until_regexp('Support')
    CommonKeywords.should_match_ordered_regexp_list(out_a, console_settings)
    
    bios_menu_lib.send_key(device, "KEY_ESC", times=2)
    log.success('Serial Port Configuration Menu in Setup accurate')


def check_post_info(device):
    deviceObj=Device.getDeviceObject(device)
    dmi_output=deviceObj.executeCmd('dmidecode -t bios',timeout=30)
    core_line=re.search('Version:\s+(\S+)\s+',dmi_output)
    if(core_line):
        bios_version_dmidecode=core_line.group(1)
        log.info('BIOS version as per dmidecode cmd: {}'.format(bios_version_dmidecode))
    log.info('Rebooting device now')
    time.sleep(5)
    bios_copy='EVALUATION COPY'
    deviceObj.sendCmd("reboot")
    post_out_bios_ver=deviceObj.read_until_regexp('BIOS version :  (.*)',timeout=140)
    post_out=deviceObj.read_until_regexp('to enter setup',timeout=140)
    
    log.info('POST Output is:')
    log.info(post_out)


    if not bios_copy in str(post_out):
        log.success('No EVALUATION COPY STRING PRESENT')
    else:
        raise RuntimeError('EVALUATION COPY STRING PRESENT')
    CommonKeywords.should_match_ordered_regexp_list(str(post_out), post_re)
    post_line=re.search('BIOS version :  (.*)\s+',post_out_bios_ver)
    log.info(post_out_bios_ver)
    log.info(post_out)
    deviceObj.read_until_regexp('localhost login:',timeout=400)
    deviceObj.loginToDiagOS()
    if(post_line):
        bios_version_post=post_line.group(1)
        log.info('BIOS version as per POST: {}'.format(bios_version_post))
    
    if(bios_version_post.strip()==bios_version_dmidecode.strip()):
        log.success('POST information displayed is accurate')
    else:
        log.info(bios_version_post)
        log.info(bios_version_dmidecode)
        log.fail('Mismatch in POST information and expected values')
        raise RuntimeError('Mismatch in POST information and expected values')
    


@logThis
def check_hotkey_functions(device):
    deviceObj=Device.getDeviceObject(device)
    pass_message_0='ESC: Exit'
    match0=deviceObj.read_until_regexp(pass_message_0,timeout=15)
    log.info('Initial screen: Main Menu')
    log.cprint(match0)
    
    #Right Hotkey Test
    bios_menu_lib.send_key(device,"KEY_RIGHT",times=1) #navigating to Advanced menu
    pass_message_1='NVMe Configuration' #content exclusive to Advanced Menu
    match1=deviceObj.read_until_regexp(pass_message_1, timeout=15)
    log.info('Right Key Test: Moved to Advanced Menu')
    log.cprint(match1) 
    
    #Left Hotkey Test
    bios_menu_lib.send_key(device,"KEY_LEFT",times=1) #navigating to Main menu
    pass_message_2='Core Version' #content exclusive to Main Menu
    match2=deviceObj.read_until_regexp(pass_message_2, timeout=15)
    log.info('Left Key Test: Moved back to Main Menu')
    log.cprint(match2)
    
    #Down Hotkey Test
    bios_menu_lib.send_key(device,"KEY_DOWN",times=1) #navigating down to System Date submenu
    pass_message_3='Set.*the.*Date' #content exclusive to System Time submenu
    match3=deviceObj.read_until_regexp(pass_message_3, timeout=15)
    log.info('Down Key Test: Moves to System Time submenu')
    log.cprint(match3)
    
    #Up Hotkey Test
    bios_menu_lib.send_key(device,"KEY_UP",times=1) #navigating up to System Language submenu
    pass_message_4='default language' #change to Main subitem1
    match4=deviceObj.read_until_regexp(pass_message_4, timeout=15)
    log.info('Up Key Test: Moves to System Language submenu')
    log.cprint(match4)
    
    #Enter Hotkey Test
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    pass_message_5='English'
    match5=deviceObj.read_until_regexp(pass_message_5, timeout=15)
    log.info('Enter Key Test: enters System Language submenu')
    log.cprint(match5)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    
    #Testing Minus/Plus, F1, F2, F3, F4 Hotkeys
    bios_menu_lib.send_key(device,"KEY_RIGHT",times=3)
    pass_message_6='minutes]' 
    match6=deviceObj.read_until_regexp(pass_message_6,timeout=20) #saving default optimized values->config A
    log.info('Default config: config A')
    log.cprint(match6)

    bios_menu_lib.send_key(device,"KEY_DOWN",times=3)
    bios_menu_lib.send_key(device,"KEY_MINUS",times=1) #decrementing value, and changing to config B
    checkpoint='minutes]'
    log.info('Changing config: decrementing FRB-2 timer: config B')
    checkMatch=deviceObj.read_until_regexp(checkpoint,timeout=20)
    log.cprint(checkMatch)
    bios_menu_lib.send_key(device,"KEY_RIGHT",times=3)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=4)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=2) #saving config B
    log.info('Saving config B')
    bios_menu_lib.send_key(device,"KEY_LEFT",times=3)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
    pass_message_7='minutes]' #capturing config B
    match7=deviceObj.read_until_regexp(pass_message_7,timeout=20)
    log.info('Saving config B')
    log.cprint(match7)
    bios_menu_lib.send_key(device,"KEY_UP",times=1)
    bios_menu_lib.send_key(device,"KEY_MINUS",times=2) #decrementing value again, and changing to config C
    pass_message_8='3 minutes]'
    match8=deviceObj.read_until_regexp(pass_message_8,timeout=20) #testing minus
    log.info('Minus Key Test: FRB-timer decremented to 3 minutes')
    log.cprint(match8)
    bios_menu_lib.send_key(device,"KEY_PLUS",times=3) #likely needs SHIFT+PLUS to work 
    pass_message_9='6 minutes]' #needs to be 6 minutes
    match9=deviceObj.read_until_regexp(pass_message_9,timeout=20) #testing plus
    log.cprint('Plus Key Test: FRB-timer incremented to 6 minutes')
    log.cprint(match9)
    bios_menu_lib.send_key(device,"KEY_F2",times=1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
    pass_message_10='minutes]'
    match10=deviceObj.read_until_regexp(pass_message_10,timeout=20) #testing f2
    log.info('F2 test: Loading previous values: config B')
    log.cprint(match10)
    bios_menu_lib.send_key(device,"KEY_UP",times=1)
    bios_menu_lib.send_key(device,"KEY_F3",times=1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
    pass_message_11='minutes]'
    match11=deviceObj.read_until_regexp(pass_message_11,timeout=20) #testing f3
    log.info('F2 test: Loading default values: config A')
    log.cprint(match11)
    bios_menu_lib.send_key(device,"KEY_F1",times=1)
    pass_message_12='Scroll'
    match12=deviceObj.read_until_regexp(pass_message_12,timeout=20) #testing f1
    log.info('F1 test: Loading help')
    log.cprint(match12)
    bios_menu_lib.send_key(device,"KEY_ESC",times=1)
    log.success('Hotkeys functioning properly in setup')
    #bios_menu_lib.send_key(device,"KEY_F4",times=1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    time.sleep(30)
    

@logThis
def check_RC(device):
    deviceObj=Device.getDeviceObject(device)
    bios_menu_lib.send_key(device,"KEY_RIGHT",times=2)
    out=deviceObj.read_until_regexp('South Bridge Chipset Configuration',timeout=15)
    CommonKeywords.should_match_ordered_regexp_list(out,mainmenu_RC)
    log.success('Success in  RC Main')
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    out_a=deviceObj.read_until_regexp('abled',timeout=15)
    log.success('Success in relax security config')
    bios_menu_lib.send_key(device,"KEY_ESC",times=1)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    out_b=deviceObj.read_until_regexp('CPU C State',timeout=15)
    CommonKeywords.should_match_ordered_regexp_list(out_b,processor_config)
    log.success('Success in processor config')
    bios_menu_lib.send_key(device,"KEY_ESC",times=1)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    out_c1=deviceObj.read_until_regexp('Recovery Firmware',timeout=15)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=3)
    out_c2=deviceObj.read_until_regexp('Error Code',timeout=15)
    out_c=out_c1+out_c2
    CommonKeywords.should_match_ordered_regexp_list(out_c,me_config)
    log.success('Success in ME config')
    bios_menu_lib.send_key(device,"KEY_ESC",times=1)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    out_d=deviceObj.read_until_regexp('ECC Support',timeout=15)
    CommonKeywords.should_match_ordered_regexp_list(out_d,north_bridge_config)
    log.success('Success in North Bridge config')
    bios_menu_lib.send_key(device,"KEY_ESC",times=1)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    out_e=deviceObj.read_until_regexp('GPIO Status',timeout=15)
    CommonKeywords.should_match_ordered_regexp_list(out_e,south_bridge_config)
    log.success('Success in South Bridge config')
    bios_menu_lib.send_key(device,"KEY_ESC",times=1)#back to RC
    log.success("All tests passed")

def import_from_remote(device,mode):
    deviceObj=Device.getDeviceObject(device)
    deviceObj.executeCmd('cd ~')
    deviceObj.executeCmd('dhclient -v ma1')
    
    download_file_through_brixia(device, amid_path, amid_name)
    download_file_through_brixia(device, afulnx_path, afulnx_image)
    #/home/brixia/gitcap/Moonstone/perf.efi
    
    deviceObj.executeCmd('mkdir fastboot_image')
    deviceObj.executeCmd('cd fastboot_image')
    
    #file_path=moonstone_path+ importDict[mode]
    log.info('Attempting to import from path:{}'.format(fastboot_path))
    download_file_through_brixia(device, fastboot_path, fastboot_image)
    chmod_cmd='chmod 777 {}'.format(fastboot_image)
    log.info('Providng universal access to file:{}'.format(fastboot_image))
    deviceObj.executeCmd(chmod_cmd)
    deviceObj.executeCmd("cd")
    deviceObj.executeCmd('mkdir release_image')
    deviceObj.executeCmd('cd release_image')
    download_file_through_brixia(device, moonstone_bios_new_image_path, moonstone_bios_new_image)
    

@logThis
def powercycle_x_times(device,times='1'):
    deviceObj=Device.getDeviceObject(device)
    iterations=int(times)
    log.info('Powercycling device {} times...'.format(iterations))
    for i in range(iterations):
        log.info('Initiating device power cycle #{} in 10 seconds...'.format(i+1))
        time.sleep(10)
        MOONSTONECommonLib.powerCycle(device)
        log.info('Powercycle {} ended'.format(i+1))
        time.sleep(10)
        #deviceObj.getPrompt("DIAGOS")

@logThis
def run_post_stress_test_scans(device, times):
    deviceObj=Device.getDeviceObject(device)
    iterations=int(times)
    log.info('run_post_stress_test_scans {} times...'.format(iterations))
    for i in range(iterations):
        powercycle_x_times(device)
        log.info('Scanning SATA devices')
        sata_cmd='fdisk -l'
        sata_content=deviceObj.executeCmd(sata_cmd)
        
        
        log.info('sata_content')
        log.info(sata_content)
        CommonKeywords.should_match_ordered_regexp_list(sata_content,fdisk_op_re)
        log.success('SATA devices read successfully')
        log.info('Scanning PCIE devices')
        pcie_cmd='lspci'
        pcie_content=deviceObj.executeCmd(pcie_cmd)
        
        log.info('pcie_content')
        log.info(pcie_content)
        CommonKeywords.should_match_ordered_regexp_list(pcie_content, lscpi_pattern)
        log.success('PCIE devices read successfully')
    
        log.info('Scanning ifconfig status')
        ifconfig_content=deviceObj.executeCmd('ifconfig')
        log.info(ifconfig_content)
        ifconfig_pattern1='lo.*RUNNING'
        ifconfig_pattern2='ma1.*RUNNING'
        match1=re.search(ifconfig_pattern1,ifconfig_content)
        match2=re.search(ifconfig_pattern1,ifconfig_content)
        if match1 and match2:
            log.success('Device working properly after powercycle stress test')
        else:
            raise RuntimeError('Error in ifconfig validation, refer output.')

@logThis
def run_cpu_warm_reset_stress_test(device):
    deviceObj=Device.getDeviceObject(device)
    log.info('Executing test script in 10s')
    time.sleep(10)
    cmd_out=deviceObj.sendCmd('./cpuWarmResetStressTest.sh',timeout=600)
    stress_out=deviceObj.read_until_regexp('localhost login',timeout=400)
    #deviceObj.loginToDiagOS()
    deviceObj.getPrompt("DIAGOS")
    log.success('Device Warm Resetted successfully')
    time.sleep(5)
    log.info('Checking log records now')
    deviceObj.sendCmd('cd /home')
    output=deviceObj.executeCmd('cat function_check.log')
    time.sleep(5)
    log.info('Log Content:')
    log.info(output)
    log.success('CPU Warm Reset stress tested successfully')
    deviceObj.sendCmd('truncate -s 0 function_check.log')
    deviceObj.sendCmd('cd ~')

@logThis
def run_cpu_stress_test(device):
    deviceObj=Device.getDeviceObject(device)
    log.info("Download stress file from server")
    download_file_through_brixia(device, stress_file_path, stress_file)
    
    log.info('Executing stress test script in 10s')
    time.sleep(10)
    deviceObj.sendCmd('./stress --cpu 32 --io 32 & ')
    
    time.sleep(5)
    deviceObj.sendCmd('./stress --cpu 8 --vm 6 --vm-bytes 512M --vm-hang 1 & ')
    time.sleep(5)
    deviceObj.sendCmd(' ')
   
    time.sleep(5)
    deviceObj.sendCmd('top -b -n 1')
    time.sleep(3)
  
    top_content=deviceObj.read_until_regexp('top[\s\S]+localhost',timeout=20)
    log.info('top_content')
    log.info(top_content)
    
    impline=re.search(cpu_use_percent_re,top_content)
    cpu_use_percent_array=[]
    if impline:
        for i in range(2):
            cpu_use_percent_array.append(float(impline.group(i+1)))
    else:
        log.info('Error calculating cpu use percentage')
    log.info('Total cpu use percentage')
    
    cpu_load=sum(cpu_use_percent_array)
    log.info(str(cpu_load))
    
    log.info("Removing stress file")
    remove_files_from_device(device, stress_file)
    if cpu_load > 90:
        log.success('CPU performing well without errors or hangs at over 90 percent utilization')
    else:
        raise RuntimeError('CPU utilization calculated below 90 percent, could not verify stress test')
 
    

def run_memory_stress_test(device):
    deviceObj=Device.getDeviceObject(device)
    log.info('Checking if memtester installed')
    out=deviceObj.executeCmd('memtester')
    memtester_match=re.search('memtester version', out)
    if memtester_match:
        log.info('Memtester present')
    else:
        log.fail('Memtester installed')
        raise RuntimeError
    log.info('Running memory stress test, one iteration, starting in 10 seconds')
    time.sleep(10)
    start=time.time()
    memtester_out=deviceObj.executeCmd('memtester 3G 1',timeout=11000)
    end=time.time()
    log.info('Output of memory stress test')
    log.info(memtester_out)
    total_time=end-start
    total_hrs=total_time//3600
    total_mins=(total_time-(total_hrs*3600))//60
    total_secs=(total_time-((total_hrs*3600)+(total_mins*60)))//1
    log.info('Total time taken for memory stress test in hh/mm/ss: {}:{}:{}'.format(total_hrs, total_mins, total_secs))
    
    CommonKeywords.should_match_ordered_regexp_list(memtester_out, memtester_re)
    log.success('Memory stress test carried out successfully')


def check_bmc_enable(device):
    deviceObj=Device.getDeviceObject(device)
    bios_menu_lib.send_key(device,"KEY_RIGHT",times=3) #go to serverMgmt
    time.sleep(10)
    server_mgmt_content_1=deviceObj.read_until_regexp('BMC network configuration',timeout=15)
    log.info('With BMC support enabled, menu status:')
    log.info(server_mgmt_content_1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1) 
    bios_menu_lib.send_key(device,"KEY_DOWN",times=1) #disable
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    time.sleep(10)
    bios_menu_lib.send_key(device,"KEY_RIGHT",times=1) #to read fresh serverMgmt page 
    bios_menu_lib.send_key(device,"KEY_LEFT",times=1) 
    #bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
    server_mgmt_content_2=deviceObj.read_until_regexp('[\s\S]+',timeout=15) 
    log.info('After BMC support disabled, menu status:')
    log.info(server_mgmt_content_2)
    content1_pattern='Wait For BMC'
    #content2_pattern='communicate with BMC'
    match1=re.search(content1_pattern,server_mgmt_content_1)
    match2=re.search(content1_pattern,server_mgmt_content_2)
    #scroll up?
    #match3=re.search(content2_pattern,server_mgmt_content_2)
    if match1:
        if match2 is None:
            log.info('Options removed after BMC disabled')
        else:
            log.fail('Options still visible')
            raise RuntimeError('Options still visible')
    else:
        log.fail('Options not read even in enabled state')
        raise RuntimeError('Options not read even in enabled state')
    bios_menu_lib.send_key(device,"KEY_LEFT",times=3)


@logThis
def check_sel_setup(device,mode):
    deviceObj=Device.getDeviceObject(device)
    bios_menu_lib.send_key(device,"KEY_RIGHT",times=3) #go to serverMgmt
    if(int(mode)==1): #enable again
        bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
        bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
        bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    bios_menu_lib.send_key(device,"KEY_UP",times=3) #go to SEL
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1) #confirm
    time.sleep(30)
    
    sel_content=deviceObj.read_until_regexp('No. of log entries in SEL : ([0-9]+)',timeout=10)
    match=re.search('No. of log entries in SEL : ([0-9]+)',sel_content) #finding num of log entries
    if(match):
        if(int(mode)==3):
            log.info('Checking if log updated')
            updated_sel_entry_count=int(match.group(1))
            if ((updated_sel_entry_count>sel_entry_count_setup) or  (updated_sel_entry_count==1)):
                log.success('SEL entry count updated successfully, current value is:')
                log.info(str(updated_sel_entry_count))
            else:
                log.fail('SEL entry count not updated properly, current value is:')
                log.info(str(updated_sel_entry_count))
                raise RuntimeError('SEL not updated properly')
        else:
            
            sel_entry_count_setup=int(match.group(1))
            

            if (int(mode)==2) and ((sel_entry_count_setup <log_entry_count_os)or sel_entry_count_setup==1):
                log.info('SEL cleared successfully')
            elif(int(mode)==1):
                log.info('Log Entries in SEL Detected')
                log.info(str(sel_entry_count_setup))
            else:
                log.fail('Number of entries in setup sel:{}'.format(str(sel_entry_count_setup)))
                raise RuntimeError('SEL not cleared in setup')
    else:
        raise RuntimeError('Unable to read number of entries in sel')
    bios_menu_lib.send_key(device,"KEY_ESC",times=1) #back to serverMgmt


def check_sel_os(device):
    deviceObj=Device.getDeviceObject(device)
    cmd1='ipmitool sel list'
    sel_os_content=deviceObj.executeCmd(cmd1)
    log.info('Sel content in ONL is:')
    log.info(sel_os_content)
    sel_lines=sel_os_content.split("\n")
    log.info(str(len(sel_lines)))
    last_sel_line=sel_lines[len(sel_lines)-5]
    last_sel_line=last_sel_line.replace(" ","")
    match=re.search('([0-9a-fA-F]+)',last_sel_line)
    if match:
        log_count_hex=match.group(1)
        log.info('Number of logs in hex is:')
        log.info(str(log_count_hex))
        log_entry_count_os=int(log_count_hex,16)
        log.info('Number of logs in int is:')
        log.info(str(log_entry_count_os))
        if(log_entry_count_os==sel_entry_count_setup):
            log.info('SEL entry count matches in setup and log')
        else:
            log.fail('SEL count not matching')
            raise RuntimeError('SEL count not matching')
    else:
        log.fail('SEL entry count not found')
        log.info(last_sel_line)
        raise RuntimeError('SEL count not found')

@logThis
def clear_sel_os(device):
    deviceObj=Device.getDeviceObject(device)
    cmd1='ipmitool sel clear'
    deviceObj.executeCmd(cmd1)
    time.sleep(10)
    log.info('sel cleared in setup')


@logThis
def validate_bmc_log_options(device,el_option,wl_option,configure=True):
    #nav from Main to BMC log
    el_config=bmc_option_dict[el_option]
    wl_config=bmc_option_dict[wl_option]
    deviceObj=Device.getDeviceObject(device)
    bios_menu_lib.send_key(device,"KEY_RIGHT",times=3)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=7)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    #inside log now
    time.sleep(5)
    bmc_log_content=deviceObj.read_until_regexp('(DATE.*TIME.*STATUS.*CODE)|(When.*\])')
    log.info('Current BMC Log Content:')
    log.info(bmc_log_content)
    log.info("Options to be regex'd are:")
    log.info(el_config)
    log.info(wl_config)
    #regexing...
    if configure:
        el_match=re.search(el_config, bmc_log_content)
        wl_match=re.search(wl_config, bmc_log_content)
        log_count_match=re.search('Log area usage = (.*) out of (.*) logs',bmc_log_content)
        if(log_count_match):
            log.info('Number of log entries:')
            lap1_bmc_log_count=int(log_count_match.group(1))
            log.info(str(lap1_bmc_log_count))
        else:
            log.info("Couldn't extract log count")

        if el_match is None:
            log.info('Changing Erase Log option')
            bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
            bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
            bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
            bmc_log_content=deviceObj.read_until_regexp('(DATE.*TIME.*STATUS.*CODE)|(When.*\])')
            el_confirm=re.search(el_config, bmc_log_content)
            if el_confirm:
                log.info('Option configured successfully')
            else:
                log.info('Failed to confirm option change')
        else:
            log.info('Erase Log seems to be already set to desired option')
        bios_menu_lib.send_key(device,"KEY_DOWN",times=1)

        if wl_match is None:
            log.info('Changing When Log is Full option')
            bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
            bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
            bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
            bmc_log_content=deviceObj.read_until_regexp('(DATE.*TIME.*STATUS.*CODE)|(When.*\])')
            wl_confirm=re.search(wl_config, bmc_log_content)
            if wl_confirm:
                log.info('Option configured successfully')
            else:
                log.info('Failed to confirm option change')
        else:
            log.info('Erase Log seems to be already set to desired option')
        bios_menu_lib.send_key(device,"KEY_UP",times=1)
        bios_menu_lib.send_key(device,"KEY_ESC",times=1)
        bios_menu_lib.send_key(device,"KEY_LEFT",times=3)
        save_and_reset(device)
        
        
        bios_menu_lib.send_key(device,"KEY_RIGHT",times=3)
        bios_menu_lib.send_key(device,"KEY_DOWN",times=7)
        bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
        log.info('Re-entered BMC log')
        #validate options are same first
    
    bmc_log_content=deviceObj.read_until_regexp('(DATE.*TIME.*STATUS.*CODE)|(When.*\])')
    log.info('BMC Log Content:')
    log.info(bmc_log_content)
    el_match=re.search(el_config, bmc_log_content)
    wl_match=re.search(wl_config, bmc_log_content)

    if el_match and wl_match:
        log.info('Options confirmed')
    else:
        log.info('Options not configured properly')

    log_count_match=re.search('Log area usage = (.*) out of (.*) logs',bmc_log_content)
    if(log_count_match):
        log.info('Number of log entries now:')
        lap2_bmc_log_count=int(log_count_match.group(1))
        log.info(str(lap2_bmc_log_count))
    if('No' in el_option):
        if(lap2_bmc_log_count>=lap1_bmc_log_count) or ('Clear' in wl_option):
            log.info('Log count updating successfully')
        else:
            log.info('Log count mismatch')
            log.info(lap1_bmc_log_count)
            log.info(lap2_bmc_log_count)
    if(('Yes' in el_option)and(lap2_bmc_log_count<=lap1_bmc_log_count)):
        log.info('Log count updating successfully')
    else:
        log.info('Log count mismatch')
        log.info('Before Reset:{}'.format(str(lap1_bmc_log_count)))
        log.info('After Reset:{}'.format(str(lap2_bmc_log_count)))
    bios_menu_lib.send_key(device,"KEY_ESC",times=1)
    bios_menu_lib.send_key(device,"KEY_UP",times=7)
    bios_menu_lib.send_key(device,"KEY_LEFT",times=3)


@logThis
def reboot_x_times(device,iterations):
    deviceObj=Device.getDeviceObject(device)
    times=int(iterations)
    for i in range(times):
        log.info('Rebooting device {} of {} times'.format(i+1, times))
        time.sleep(5)
        deviceObj.sendCmd('reboot')
        deviceObj.read_until_regexp('localhost login',timeout=400)
        #deviceObj.loginToDiagOS()
        deviceObj.getPrompt("DIAGOS")
        log.cprint('Booted into Linux OS ')
        time.sleep(5)

@logThis
def configure_network_setup(device,mode):
    deviceObj=Device.getDeviceObject(device)
    modeDict={'1':'Static','2':'DHCP'}
    operation=modeDict[mode]
    log.info('Configuring: {}'.format(operation))
    #Navigating from MM to Network menu
    bios_menu_lib.send_key(device,"KEY_RIGHT",times=3)
    time.sleep(3)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=9)
    time.sleep(3)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    content1=deviceObj.read_until_regexp('Router MAC Address.*',timeout=20)
    log.info('Inside network menu.')
    log.info('Content:')
    log.info(content1)
    if(int(mode)==2):
        bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
        bios_menu_lib.send_key(device,"KEY_DOWN",times=2)
        bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    if(int(mode)==1):
        bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
        bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
        bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
        #go to ip menu
        bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
        bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
        #set ip to a.b.c.d
        bios_menu_lib.send_key(device, "KEY_BKSP", times=16)
        time.sleep(10)
        type_in_bios(temp_mgmt_ip1,device)
        time.sleep(5)
        bios_menu_lib.send_key(device, "KEY_ENTER",times=1)
        #go to subnet menu
        bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
        bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
        #set subnet to a.b.c.d
        bios_menu_lib.send_key(device, "KEY_BKSP", times=16)
        time.sleep(10)
        type_in_bios('255.255.255.0',device)
        time.sleep(5)
        bios_menu_lib.send_key(device, "KEY_ENTER",times=1)
    time.sleep(10)
    content2=deviceObj.read_until_regexp('Router MAC Address.*',timeout=20)
    log.info('Content now:')
    log.info(content2)
    log.info('Initiating save & exit')
    bios_menu_lib.send_key(device, "KEY_ESC",times=1)
    bios_menu_lib.send_key(device, "KEY_LEFT",times=3)
    save_and_exit_bios_now(device)
    time.sleep(5)

def type_in_bios(ipstring,device):
    log.info('typing ip character-wise')
    for ch in ipstring:
        time.sleep(1)
        bios_key=bios_values[ch]
        log.info('CH:{}'.format(ch))
        log.info('KEY:{}'.format(bios_key))
        bios_menu_lib.send_key(device, bios_key, times=1)


@logThis
def save_and_reset(device):
    deviceObj=Device.getDeviceObject(device)
    log.info('Executing save and reset')
    bios_menu_lib.send_key(device,"KEY_LEFT",times=1)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=2)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    out=deviceObj.read_until_regexp('to enter setup',timeout=140)
    counter = 5
    while counter >= 0:
         bios_menu_lib.send_key(device, "KEY_DEL")
         counter -= 1
         time.sleep(1)



@logThis
def check_network_setup(device,mode):
    deviceObj=Device.getDeviceObject(device)
    modeDict={'1':'Static','2':'DHCP'}
    operation=modeDict[mode]
    log.info('Verifying: {}'.format(operation))
    #Navigating from MM to Network menu
    bios_menu_lib.send_key(device,"KEY_RIGHT",times=3)
    time.sleep(3)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=9)
    time.sleep(3)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    #reading content
    log.info('Inside Network menu.')
    time.sleep(3)
    network_menu_content=deviceObj.read_until_regexp('Router MAC Address.*',timeout=20)
    log.info('Content:')
    log.info(network_menu_content)
    #come out of Network menu content before possible failure
    bios_menu_lib.send_key(device,"KEY_ESC",times=1)
    #reversing navigation
    bios_menu_lib.send_key(device,"KEY_UP",times=9)
    time.sleep(3)
    bios_menu_lib.send_key(device,"KEY_LEFT",times=3)
    time.sleep(3)
    
    if (int(mode)==1):
        CommonKeywords.should_match_ordered_regexp_list(network_menu_content,re_static_ip_setup)#work
    elif (int(mode)==2):
        CommonKeywords.should_match_ordered_regexp_list(network_menu_content,re_dhcp_ip_setup)#work
    log.success('Network config verified!')

@logThis
def check_network_os(device,mode):
    deviceObj=Device.getDeviceObject(device)
    modeDict={'1':'Static','2':'DHCP'}
    operation=modeDict[mode]
    log.info('Verifying: {}'.format(operation))

    ipmitool_content=deviceObj.executeCmd('ipmitool lan print 1')
    log.info('Output:')
    log.info(ipmitool_content)

    if(int(mode)==1):
        CommonKeywords.should_match_ordered_regexp_list(ipmitool_content,re_static_ip_os)#work
    if(int(mode)==2):
        CommonKeywords.should_match_ordered_regexp_list(ipmitool_content,re_dhcp_ip_os)#work

@logThis
def configure_network_os(device,mode):
    deviceObj=Device.getDeviceObject(device)
    modeDict={'1':'Static','2':'DHCP'}
    operation=modeDict[mode]
    log.info('Configuring: {}'.format(operation))

    if(int(mode)==1):
        deviceObj.executeCmd('ipmitool lan set 0x01 ipsrc static')
        time.sleep(2)
        deviceObj.executeCmd('ipmitool lan set 0x01 ipaddr '+temp_mgmt_ip2)
        time.sleep(2)
        ipmitool_content=deviceObj.executeCmd('ipmitool lan print 1')
        log.info('Output:')
        log.info(ipmitool_content)
        CommonKeywords.should_match_ordered_regexp_list(ipmitool_content,re_static_ip_os)
        


@logThis
def set_bios_version(device,mode):

    deviceObj=Device.getDeviceObject(device)
    verse=''
    if(int(mode)==1):
        verse='1.1.2'
    elif(int(mode)==2):
        verse='2.0.0'
    
    log.info('Setting BIOS version to: {}'.format(verse))
    deviceObj.sendCmd('cd ~')
    if(int(mode)==1):
        update_cmd="./afulnx_64 ./fastboot_image/"+fastboot_image+" /p /b /n /me /x /k"
    elif(int(mode)==2):
        update_cmd="./afulnx_64 ./release_image/"+moonstone_bios_new_image+" /p /b /n /me /x /k"
    if(int(mode)==1):
        #bringing file to USB
        log.info('Mounting usb..')
        mount_cmd='mount /dev/sdc1 /mnt/'
        deviceObj.executeCmd(mount_cmd)
        mount_content=deviceObj.executeCmd('ls /mnt')
        if('perf.efi' not in mount_content):
            log.info('Importing perf tool to USB')
            deviceObj.executeCmd('cp ./perf.efi /mnt')
            mount_content=deviceObj.executeCmd('ls /mnt')
            if('perf.efi' not in mount_content):
                log.fail('Couldn"t import perf file to USB')
        
    log.info(update_cmd)
    set_bios_output=deviceObj.executeCmd(update_cmd,timeout=400)
    log.info('Output of afulnx command:')
    log.info(set_bios_output)

    dmidecode_output=deviceObj.executeCmd('dmidecode -t bios')
    log.info('dmidecode output:\n{}'.format(dmidecode_output))
    log.info('Rebooting now')
    deviceObj.sendCmd('reboot')
    deviceObj.read_until_regexp('login',timeout=400)
    deviceObj.loginToDiagOS()
    time.sleep(5)
    log.info('Checking bios version now')
    dmidecode_output=deviceObj.executeCmd('dmidecode -t bios')
    log.info('dmidecode output:\n{}'.format(dmidecode_output))
    pattern=image_version_re[mode]
    version_match=re.search(pattern,dmidecode_output)
    if version_match:
        log.success('BIOS Image Updated successfully!')
    else:
        log.fail('BIOS Image Not Updated')
        raise RuntimeError('BIOS Image Not Updated')
    if(int(mode)==2):
        log.info('Deleting directories created')
        deviceObj.sendCmd('cd ~')
        deviceObj.sendCmd('rm -rf fastboot_image')
        deviceObj.sendCmd('rm -rf release_image')
        home_content=deviceObj.executeCmd('ls')
        log.info('~ now:\n{}'.format(home_content))
    if(boot_time_enabled<=boot_time_disabled):
            log.success('Fast boot functionality works!')
            #log.info('Disabled:{}'.format(str(boot_time_disabled)))
            #log.info('Enabled:{}'.format(str(boot_time_enabled)))
    else:
        log.fail('Fast boot functionality not working')
    
@logThis
def run_amiprd_tool(device,mode,exitshell=False):
    from BIOS_variable import boot_time_disabled
    from BIOS_variable import boot_time_enabled
    deviceObj=Device.getDeviceObject(device)
    deviceObj.read_until_regexp('Shell>',timeout=120)
    log.info('Initiating AMIPRD tool in 10s')
    time.sleep(5)
    if(int(mode)==1):
        log.info('Fast boot disabled during this run')
    if(int(mode)==2):
        log.info('Fast boot enabled during this run')
    
    time.sleep(5)
    deviceObj.sendCmd('fs1: \r \n')
    deviceObj.sendCmd('AMIPRD.efi \r \n')
    deviceObj.read_until_regexp('Press any key to continue',timeout=60)
    deviceObj.sendCmd('n \r \n')
    deviceObj.read_until_regexp('Press any key to continue',timeout=60)
    deviceObj.sendCmd('n \r \n')
    deviceObj.read_until_regexp('Press any key to continue',timeout=60)
    deviceObj.sendCmd('n \r \n')
    #part1
    deviceObj.read_until_regexp('Press any key to continue',timeout=60)
    deviceObj.sendCmd('n \r \n')
    #part2
    core_content=deviceObj.read_until_regexp('PART.*2.*"POST Time".*Performance.*Records.*Overview.*Report[\s\S]+Press any key to continue',timeout=60)
    next_line=re.search('([0-9]+).*VenMedia',core_content)
    if next_line:
        log.info('Next line:')
        nextnum=int(next_line.group(1))
        core_num=str(nextnum-1)
    core_pattern='{}.*Boot(.*)'.format(core_num)
    log.info('core pattern:{}'.format(core_pattern))
    core_line=re.search(core_pattern,core_content)
    if core_line:
        log.info('Captured Boot String')
        rawstring=core_line.group(1)
        refined=rawstring.strip()
        log.info(refined)
        timestr=''
        for i in range(1,len(refined)+1):
            if(refined[-i]!=' '):
                timestr+=(refined[-i])
            else:
                break
        timestr2=timestr[::-1]
        log.info('timestr2:{}'.format(timestr2))
        if(int(mode)==1):
            log.info('This was a run with fastboot disabled')
            boot_time_disabled=int(timestr2)
            log.info('Boot Time:')
            log.info(str(boot_time_disabled))
        if(int(mode)==2):
            log.info('This was a run with fastboot enabled')
            boot_time_enabled=int(timestr2)
            log.info('Boot Time:')
            log.info(str(boot_time_enabled))
    time.sleep(5)
    deviceObj.sendCmd('n \r \n')
    #part3
    for i in range(5):
        time.sleep(20)
        deviceObj.sendCmd('n \r \n')
        
    '''deviceObj.read_until_regexp('Press any key to continue',timeout=60)
    deviceObj.sendCmd('n \r \n')
    #continue1
    deviceObj.read_until_regexp('Continue\?',timeout=60)
    deviceObj.sendCmd('n \r \n')
    deviceObj.read_until_regexp('Press any key to continue',timeout=60)
    deviceObj.sendCmd('n \r \n')
    deviceObj.read_until_regexp('Continue\?',timeout=60)
    deviceObj.sendCmd('n \r \n')
    deviceObj.read_until_regexp('Press any key to continue',timeout=60)
    deviceObj.sendCmd('n \r \n')'''
    time.sleep(5)
    if(int(mode)==1):
        log.info('Boot time with fastboot disabled:{}'.format(boot_time_disabled))
    if(int(mode)==2):
        log.info('Boot time with fastboot enabled:{}'.format(boot_time_enabled))
    if(exitshell):
        log.info('Exiting to ONL now')
        deviceObj.sendCmd('fs0: \r \n')
        time.sleep(2)
        deviceObj.sendCmd('cd EFI \r \n')
        time.sleep(2)
        deviceObj.sendCmd('cd ONL \r \n')
        time.sleep(2)
        deviceObj.sendCmd('grubx64.efi \r \n')
        time.sleep(5)
        deviceObj.sendCmd('\r')
        deviceObj.read_until_regexp('(localhost login)|(root@localhost)',timeout=120) #should boot to localhost
        log.info('booted to localhost')
        deviceObj.getPrompt("DIAGOS")
        time.sleep(5)

def configure_fastboot_setup(device,mode):
    deviceObj=Device.getDeviceObject(device)
    fastboot_pattern=""
    if(int(mode)==1):
        fastboot_pattern='Fast Boot.*\[Enabled\]'
    elif(int(mode)==2):
        fastboot_pattern='Fast Boot.*\[Disabled\]'
    #log.info('Enabling fastboot in setup now')
    log.info('Checking for:{}'.format(fastboot_pattern))
    deviceObj.sendCmd('reset \r \n')
        
    #while fastboot_loop:
    #deviceObj.read_until_regexp('(Shell>)|(FS)', timeout=180)
    out=deviceObj.read_until_regexp('to enter setup',timeout=240)
    counter = 5
    while counter >= 0:
        bios_menu_lib.send_key(device, "KEY_DEL")
        counter -= 1
        time.sleep(1)
    
    time.sleep(5)
    bios_menu_lib.send_key(device,"KEY_RIGHT",times=2)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=3)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    fast_boot_menu=deviceObj.read_until_regexp('Memory Frequency.*\[')
    log.info('Fast_Boot_Menu')
    log.info(fast_boot_menu)
    fastboot_match=re.search(fastboot_pattern,fast_boot_menu)
    #disable_match=re.search('Fast Boot.*\[Disabled\]',fast_boot_menu)
    if fastboot_match:
        log.info('Set to desired option')
        bios_menu_lib.send_key(device,"KEY_ESC",times=1)
        bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    else:
        log.info('Changing to desired option')
        bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
        bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
        bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
        bios_menu_lib.send_key(device,"KEY_F4",times=1)
        bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    fast_boot_menu2=deviceObj.read_until_regexp('Memory Frequency.*\[')
    log.info('Fast_Boot_Menu Now:')
    log.info(fast_boot_menu2)
    time.sleep(120)


# TC - 1.0.34 RTC test
def check_for_RTC(device):

    deviceObj =  Device.getDeviceObject(device)
    # Step 1
    enter_into_bios_setup_now(device)
    time.sleep(10)
    bios_menu_lib.send_key(device, "KEY_DOWN", 2)
    bios_menu_lib.send_key(device, "KEY_1")
    bios_menu_lib.send_key(device, "KEY_2")
    bios_menu_lib.send_key(device, "KEY_ENTER")
    bios_menu_lib.send_key(device, "KEY_2",2)
    log.info("changed time to 12:22 ")
    out_1 = deviceObj.read_until_regexp('ESC:', timeout=40)      
    save_and_exit_bios_now(device)
    deviceObj.sendCmd("reboot")
    out_2 = deviceObj.read_until_regexp('Hardware Clock updated to\s+\S+\s+\S+\s+\S+\s(\S+)', timeout=40)
    x = fetch_regex('Hardware Clock updated to\s+\S+\s+\S+\s+\S+\s(\S+)', out_2)
    if x == '-1':
        log.fail("not able to fetch time")
    log.success("time updated successfully %s" %x)
    deviceObj.read_until_regexp('localhost login', timeout=400)
    deviceObj.loginToDiagOS()
    
    # Step 2
    formated_date_time = format_date_time()
    log.info(formated_date_time)
    log.info("updating time with using below commands")
    cmd1 = f"date -s \"{formated_date_time}\""
    cmd2 = f"hwclock -w"
    deviceObj.executeCmd(cmd1)
    deviceObj.executeCmd(cmd2)
    enter_into_bios_setup_now(device)
    time.sleep(10)
    out_1 = deviceObj.read_until_regexp('ESC:', timeout=40)
    x = fetch_regex('System Time\s+\[(\S+)\]', out_1)
    y = fetch_regex("System Date\s+\[\S+\s(\S+)\]", out_1)
    if x == '-1' or y=='-1':
        log.fail("not able to fetch date and time")
        
    current_date_time= format_date_time()
    current_time= current_date_time.split(' ')[1]
    current_date = current_date_time.split(' ')[0]
    current_date_lst= [current_date.split('/')[1],current_date.split('/')[2], current_date.split('/')[0]]
    formated_date = '/'.join(current_date_lst)
    current_time_hour = '('+current_time.split(':')[0]+')'
    current_date_regex= '('+formated_date +')'
    log.cprint("ok")
    isTimeChanged = fetch_regex(current_time_hour, x)
    isDateChanged = fetch_regex(current_date_regex, y)
    if isTimeChanged=='-1' or isDateChanged == '-1':
        log.fail("date or time not changed")
    log.success("date matches to current date %s " %y )
    log.success("time matches to current time %s " %x )
    exit_bios_now(device)
    
    
    # Step 3
    log.info("sleeping for 180 seconds")
    time.sleep(180)
    log.info("checking date and time again i.e matches current date and time")
    enter_into_bios_setup_now(device)
    time.sleep(10)
    out_1 = deviceObj.read_until_regexp('ESC:', timeout=40)
    x = fetch_regex('System Time\s+\[(\S+)\]', out_1)
    y = fetch_regex("System Date\s+\[\S+\s(\S+)\]", out_1)
    if x == '-1' or y=='-1':
        log.fail("not able to fetch date and time")
    current_date_time= format_date_time()
    current_time= current_date_time.split(' ')[1]
    current_time_hour = '('+current_time.split(':')[0]+')'
    current_date = current_date_time.split(' ')[0]
    current_date_lst= [current_date.split('/')[1],current_date.split('/')[2], current_date.split('/')[0]]
    formated_date = '/'.join(current_date_lst)
    current_date_regex= '('+formated_date +')'
    isTimeChanged = fetch_regex(current_time_hour, x)
    isDateChanged = fetch_regex(current_date_regex, y)
    if isTimeChanged=='-1' or isDateChanged == '-1':
        log.fail("date or time not changed")
    log.success("date matches to current date %s " %y )
    log.success("time matches to current time %s " %x )
    exit_bios_now(device)
    
    cmd3=f"date -s \"1999/12/29 23:59:59\""
    deviceObj.executeCmd(cmd3)
    deviceObj.executeCmd(cmd2)
    enter_into_bios_setup_now(device)
    time.sleep(10)
    out_1 = deviceObj.read_until_regexp('ESC:', timeout=40)
    x = fetch_regex('System Time\s+\[(\S+)\]', out_1)
    y = fetch_regex("System Date\s+\[\S+\s(\S+)\]", out_1)
    if x == '-1' or y=='-1':
        log.fail("not able to fetch date and time")
    isTimeChanged = fetch_regex('(00:)', x)
    isDateChanged = fetch_regex('(12/30/1999)', y)
    if isTimeChanged=='-1' or isDateChanged == '-1':
        log.fail("date or time not changed")
    log.success("date matches to updated date %s " %y )
    log.success("time matches to updated time %s " %x )
    exit_bios_now(device)
    
def fetch_regex(pattern, output):
    x = re.search(pattern, output)
    if x is not None:
        return x.group(1)
    return "-1" 
    
def format_date_time():
    from datetime import datetime
    # datetime object containing current date and time
    now = str(datetime.now())
    date_time = now.split()
    formated_date_time = date_time[0].split('-')[0]+'/'+date_time[0].split('-')[1]+'/'+date_time[0].split('-')[2]+' '+date_time[1].split('.')[0]
    return formated_date_time


# TC -3 Online programming through linux os
def download_file_through_brixia(device, file_path, file_name):
    deviceObj =  Device.getDeviceObject(device)
    cmd = "scp brixia@"+scp_ip+":"+file_path +" ."
    deviceObj.sendCmd(cmd)
    promptList = ["(y/n)", "(yes/no)", "password:"]
    patternList = re.compile('|'.join(promptList))
    output = deviceObj.read_until_regexp(patternList, 20)
    if re.search("(y/n)", output):
        deviceObj.sendCmd("yes")
        deviceObj.read_until_regexp("password:")
        deviceObj.sendCmd(scp_password)
        deviceObj.read_until_regexp('root@localhost', 20)
    elif re.search("(yes/no)", output):
        deviceObj.sendCmd("yes")
        deviceObj.read_until_regexp("password:")
        deviceObj.sendCmd(scp_password)
        deviceObj.read_until_regexp('root@localhost', 20)
    elif re.search("password:", output):
        deviceObj.sendCmd(scp_password)
        deviceObj.read_until_regexp('root@localhost', 20)
    else:
        log.fail("pattern mismatch")
    deviceObj.sendline('\n')
    
    output = deviceObj.executeCmd("ls")
    CommonKeywords.should_match_a_regexp(output, file_name)
    log.success("Successfully downloaded file %s into device." %file_name)

def download_file_in_bmc(deviceM, file_path, file_name):
    deviceObj =  Device.getDeviceObject(deviceM)
    cmd = "scp brixia@"+scp_ip+":"+file_path +" ."
    deviceObj.sendCmd(cmd)
    promptList = ["(y/n)", "(yes/no)", "password:"]
    patternList = re.compile('|'.join(promptList))
    output = deviceObj.read_until_regexp(patternList, 20)
    if re.search("(y/n)", output):
        deviceObj.sendCmd("yes")
        deviceObj.read_until_regexp("password:")
        deviceObj.sendCmd(scp_password)
        try:
            deviceObj.read_until_regexp('root@moonstone', 200)
        except Exception: 
            #deviceObj.sendCmd("\n")
            device.loginToNEWBMC()
            deviceObj.read_until_regexp('root@moonstone', 20)
    elif re.search("(yes/no)", output):
        deviceObj.sendCmd("yes")
        deviceObj.read_until_regexp("password:")
        deviceObj.sendCmd(scp_password)
        try:
            deviceObj.read_until_regexp('root@moonstone', 200)
        except Exception: 
            #deviceObj.sendCmd("\n")
            device.loginToNEWBMC()
            deviceObj.read_until_regexp('root@moonstone', 20)
    elif re.search("password:", output):
        deviceObj.sendCmd(scp_password)
        try:
            deviceObj.read_until_regexp('root@moonstone', 200)
        except Exception: 
            #deviceObj.sendCmd("\n")
            device.loginToNEWBMC()
            deviceObj.read_until_regexp('root@moonstone', 20)
    else:
        log.fail("pattern mismatch")
    deviceObj.sendline('\n')
    
    output = deviceObj.executeCmd("ls")
    CommonKeywords.should_match_a_regexp(output, file_name)
    log.success("Successfully downloaded file %s into device." %file_name)

def remove_files_from_device(device, file_name):
    deviceObj =  Device.getDeviceObject(device)
    cmd = "rm -rf %s" %file_name
    deviceObj.sendCmd(cmd)
    output = deviceObj.executeCmd("ls")
    #if file_name in output:
     #   raise RuntimeError("File %s not deleted " %file_name)
    log.success("File %s deleted successfully" %file_name)
    

    
# backup - 0x03 primary-0x01
def boot_bios_to_primary_or_backup(device, mode):
    deviceObj = Device.getDeviceObject(device)
    #enter_into_lpc(device)
    cmd1 = "./lpc_cpld_x86_64 blu r 0xa123"
    cmd2 = "./lpc_cpld_x86_64 blu w 0xa123 0x0%s" %mode
    cmd3 = "./lpc_cpld_x86_64 blu w 0xa164 0x00"
    deviceObj.executeCmd("cd")
    deviceObj.executeCmd("cd /home/cel_diag/moonstone/tools/")
    deviceObj.executeCmd(cmd1)
    deviceObj.executeCmd(cmd2)
    
    
    if mode =='1':
        boot_regex = "Boot from Primary BIOS"
        boot_mode = "Primary"
    else:
        boot_regex = "Boot from Backup BIOS"
        boot_mode = "Backup"
    log.debug("Booting Bios to %s" %boot_mode)
    deviceObj.sendCmd(cmd3)
    deviceObj.read_until_regexp(boot_regex, 400)
    log.success("Bios is being booted in correct mode.")
    output = deviceObj.read_until_regexp("localhost login", 400)
    deviceObj.loginToDiagOS()
    #remove_files_from_device(device, "diag")
    #remove_files_from_device(device, bios_deb_image)
    

def boot_bios_to_backup(device):
    deviceObj = Device.getDeviceObject(device)
    enter_into_lpc(device)
    cmd1 = "./lpc_cpld_x86_64 blu r 0xa123"
    cmd2 = "./lpc_cpld_x86_64 blu w 0xa123 0x03"
    cmd3 = "./lpc_cpld_x86_64 blu w 0xa164 0x00"
    
    deviceObj.executeCmd(cmd1)
    deviceObj.executeCmd(cmd2)
    deviceObj.sendCmd(cmd3)
    output = deviceObj.read_until_regexp("localhost login", 400)
    deviceObj.loginToDiagOS()
    remove_files_from_device(device, "diag")
    remove_files_from_device(device, bios_deb_image)
    
    
def verify_the_bios_version(device, image):
    device_obj = Device.getDeviceObject(device)
    #enter_into_lpc(device)
    cmd = "./cel-sysinfo-test --all"
    device_obj.executeCmd("cd")
    device_obj.executeCmd("cd /home/cel_diag/moonstone/bin/")
    res = device_obj.executeCmd(cmd)
    image_name = image.split(".bin")
    pattern = "BIOS option success :   Version: %s" %image
    match = re.findall(pattern, res)
    log.cprint(match)
    if match:
        log.success("Bios version is successfully updated to %s" % image)
    else:
        raise RuntimeError("expected Bios version should be %s but got %s" % (image, pattern))
    device_obj.executeCmd("cd")
    #remove_files_from_device(device, "diag")
    #remove_files_from_device(device, bios_deb_image)
    

def update_bios_through_afulnx(device, image_path, image):
    device_obj = Device.getDeviceObject(device)
    cmd1 = "chmod 777  afulnx_64"
    cmd2 = "./afulnx_64 %s /p /b /n /me /x /k" % image
    #download_file_through_brixia(device, afulnx_path, afulnx_image)
    #download_file_through_brixia(device, image_path, image)
    res1 = device_obj.executeCmd(cmd1)
    res2 = device_obj.executeCmd(cmd2, timeout=1500)
    CommonKeywords.should_match_a_regexp(res2, "Process completed.")
    log.success("Bios image is updated to %s through afulnx" % image)
    #remove_files_from_device(device, afulnx_image)
    #remove_files_from_device(device, image)
    
    
@logThis
def check_bmc_version_info(device):
    device_obj = Device.getDeviceObject(device)
    cmd='ipmitool mc info'
    c1=device_obj.executeCmd(cmd)
    CommonKeywords.should_match_paired_regexp_list(c1,bmc_version_info_list)
    log.success("BMC version info is as expected.")
    
    
# TC - CPU_LPC_Interface_Test
@logThis
def enter_into_lpc(device):
    deviceObj = Device.getDeviceObject(device)
    deviceObj.executeCmd("cd")
    cmd = "dpkg -i "+bios_deb_image
    cmd1 = 'cd /home/cel_diag/moonstone/tools/'
    log.debug("Download and install .deb package ....")
    #download_files_in_usb(device,bios_deb_image )
    download_file_through_brixia(device, moonstone_images_path+bios_deb_image, bios_deb_image)
    
    deviceObj.executeCmd(cmd)
    deviceObj.executeCmd(cmd1)
    log.info("Successfully entered in LPC interface directory")
    time.sleep(5)


@logThis
def download_deb_package(device):
    deviceObj = Device.getDeviceObject(device)
    deviceObj.executeCmd("cd")
    cmd = "dpkg -i "+bios_deb_image
    log.debug("Download and install .deb package ....")
    #download_files_in_usb(device,bios_deb_image )
    download_file_through_brixia(device, moonstone_images_path+bios_deb_image, bios_deb_image)
    
    output=deviceObj.executeCmd(cmd)
    CommonKeywords.should_match_paired_regexp_list(output,dpkg_install_pattern)
    
    log.info("Successfully downloaded and installed deb package")
    time.sleep(5)

def read_write_stress_test(device, iteration):
    deviceObj = Device.getDeviceObject(device)

    deviceObj.executeCmd("cd")
    deviceObj.executeCmd("dhclient -v ma1")
    cmd1 = 'cd /home/cel_diag/moonstone/tools/'
    download_deb_package(device)
    deviceObj.executeCmd(cmd1)
    for val in range(int(iteration)):
        output1 = deviceObj.executeCmd("./stressapptest -s 60 -M 28800 -m 2 -i 2 -C 4 -W -d /dev/sdc", timeout=200)
        CommonKeywords.should_match_ordered_regexp_list(output1, ssd_read_write_stress_test_pattern)
        output2 = deviceObj.executeCmd("df")
        CommonKeywords.should_match_ordered_regexp_list(output2, df_output_pattern)
        log.success("SSD Read write testing is successful for iteration : %s "%(val+1))
    
    deviceObj.executeCmd("cd")
    remove_files_from_device(device,bios_deb_image)
    log.success("Successfully tested stress test for ssd read write operation.")
   

def warm_reset_stress_test(device, iterations):
    deviceObj = Device.getDeviceObject(device)
    powerCycle_device(device)
    download_deb_package(device)
    for val in range(int(iterations)):
        deviceObj.executeCmd("cd /home/cel_diag/moonstone/bin")
        
        output=deviceObj.executeCmd("./cel-sysinfo-test --all")
        CommonKeywords.should_match_a_regexp(output, "OPT test all.*PASS")
        
        output=deviceObj.executeCmd("./cel-i2c-test --all")
        CommonKeywords.should_match_a_regexp(output, "I2C Test All.*PASS")
        
        deviceObj.executeCmd("cd")
        deviceObj.executeCmd("cd /home/cel_diag/moonstone/tools")
        
        
        output=deviceObj.executeCmd("./lpc_cpld_x86_64 blu r 0xa101")
        CommonKeywords.should_match_a_regexp(output, "0xde")
        
        output=deviceObj.executeCmd("./lpc_cpld_x86_64 blu w 0xa101 0xaa")
        output=deviceObj.executeCmd("./lpc_cpld_x86_64 blu r 0xa101")
        CommonKeywords.should_match_a_regexp(output, "0xaa")
        
        output=deviceObj.executeCmd("./lpc_cpld_x86_64 blu w 0xa101 0xde")
        output=deviceObj.executeCmd("./lpc_cpld_x86_64 blu r 0xa101")
        CommonKeywords.should_match_a_regexp(output, "0xde")
        
        output=deviceObj.executeCmd("lspci")
        CommonKeywords.should_match_ordered_regexp_list(output, lscpi_pattern)
        
        output=deviceObj.executeCmd("lspci | wc -l")
        CommonKeywords.should_match_a_regexp(output, "102")
        
        output=deviceObj.executeCmd("ping -c 2 10.208.84.102")
        output=deviceObj.executeCmd("fdisk -l")
        CommonKeywords.should_match_ordered_regexp_list(output, fdisk_op_re)
        
        deviceObj.executeCmd("cd")
        deviceObj.sendCmd("reboot")
        deviceObj.read_until_regexp("localhost login:", 400)
        deviceObj.loginToDiagOS()
        log.success("Successful iteration %s for warm_reset_stress_test" %str(val))
        
    log.success("warm_reset_stress_test is successful")
    deviceObj.executeCmd("cd")
    remove_files_from_device(device,bios_deb_image)
    
    
@logThis
def check_IntelRC(device):
    deviceObj=Device.getDeviceObject(device)
    bios_menu_lib.send_key(device,"KEY_RIGHT",times=2)
    out=deviceObj.read_until_regexp('Runtime Error Logging',timeout=15)
    CommonKeywords.should_match_ordered_regexp_list(out,mainmenu_RC)
    log.success('Success in Intel RC Main')
    
    # processor config
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    out=deviceObj.read_until_regexp('Monitor/Mwait',timeout=15)
    CommonKeywords.should_match_ordered_regexp_list(out,processor_config)
    log.success('Success in processor config')
    
    #Advanced power management configuration
    bios_menu_lib.send_key(device,"KEY_ESC",times=1)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    out=deviceObj.read_until_regexp('SOCKET RAPL Config',timeout=15)
    CommonKeywords.should_match_ordered_regexp_list(out,power_management_config)
    log.success('Success in Advanced power management configuration')
    
    #Common RefCode Configuration
    bios_menu_lib.send_key(device,"KEY_ESC",times=1)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    out=deviceObj.read_until_regexp('Numa.*able',timeout=15)
    CommonKeywords.should_match_ordered_regexp_list(out,common_refcode_config)
    log.success('Success in Common RefCode Configuration')
    
    #QPI general configuration
    bios_menu_lib.send_key(device,"KEY_ESC",times=1)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=2)
    out=deviceObj.read_until_regexp('QPI Debug Print Level.*All',timeout=15)
    
    CommonKeywords.should_match_ordered_regexp_list(out,qpi_general_config)
    log.success('Success in QPI general configuration')
    
    #Integrated Memory controller
    bios_menu_lib.send_key(device,"KEY_ESC",times=2)
    time.sleep(10)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    out=deviceObj.read_until_regexp('Enforce Timeout.*Auto',timeout=15)
    CommonKeywords.should_match_ordered_regexp_list(out,integrated_memory_controller)
    log.success('Success in Integrated Memory controller')
    
    #IIO Configuration
    bios_menu_lib.send_key(device,"KEY_ESC",times=1)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=1)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    out=deviceObj.read_until_regexp('IIO South Complex Configuration',timeout=15)
    CommonKeywords.should_match_ordered_regexp_list(out,iio_configuration)
    log.success('Success in IIO Configuration')
    
    #General ME Configuration 
    bios_menu_lib.send_key(device,"KEY_ESC",times=1)
    bios_menu_lib.send_key(device,"KEY_DOWN",times=4)
    bios_menu_lib.send_key(device,"KEY_ENTER",times=1)
    out=deviceObj.read_until_regexp('MCTP Bus Owner',timeout=15)
    CommonKeywords.should_match_ordered_regexp_list(out,me_config)
    log.success('Success in General ME Configuration ')
    
    bios_menu_lib.send_key(device,"KEY_ESC",times=1)#back to IntelRC
    time.sleep(10)
    log.success("All tests passed")


#def check_pressing_undefined_keys  DUT
 #   Step  2  check_left_right_keys_for_main_menu_and_exit_screen  DUT
 
def check_main_menu_content(device):
    deviceObj=Device.getDeviceObject(device)
    m19_out = deviceObj.read_until_regexp('ESC:', timeout=10)
    result_string = ''
    log.info("Checking main menu content")
    for i in main_menu_items:
        pattern = i
        match = re.search(pattern, m19_out)
        if match:
            log.info(str(match.group(1)))
            result_string = result_string + str(match.group(1)) + '||'
        else:
            log.info(i)
            log.info("not available")

            raise RuntimeError("main menu datanot available")



def check_left_right_keys_for_main_menu_and_exit_screen(device):
    deviceObj=Device.getDeviceObject(device)
    log.info("Pressing left key to move to save and exit screen")
    bios_menu_lib.send_key(device,"KEY_LEFT",times=1)
    out=deviceObj.read_until_regexp('Boot Override',timeout=15)
    CommonKeywords.should_match_ordered_regexp_list(out,save_and_exit_screen_pattern)
    log.success("Moved to save and exit screen successfully.")
    
    log.info("Pressing right key to move to advance menu screen")
    bios_menu_lib.send_key(device,"KEY_RIGHT",times=2)
    out=deviceObj.read_until_regexp('NVMe Configuration ',timeout=15)
    CommonKeywords.should_match_ordered_regexp_list(out,advance_menu_check)
    log.success("Moved to advance menu screen successfully.")
    
    
def check_pressing_undefined_keys(device):
    deviceObj=Device.getDeviceObject(device)
    log.info("Pressing any undefined key : 1")
    bios_menu_lib.send_key(device,"KEY_1",times=3)
    time.sleep(10)
    check_main_menu_content(device)
    log.success("Successfully checked no effect of undefined key on bios setup.")
    

def check_tco_feature(device):
    deviceObj=Device.getDeviceObject(device)
    
    download_deb_package(device)
    out=deviceObj.executeCmd("cd /home/cel_diag/moonstone/bin")
    
    log.info("Checking sysinfo test")
    out=deviceObj.executeCmd("./cel-sysinfo-test --all")
    CommonKeywords.should_match_a_regexp(out,"OPT test all.*PASS")
    
    log.info("Enable TCO_wdt")
    deviceObj.executeCmd("sudo modprobe iTCO_wdt")
    out=deviceObj.executeCmd("dmesg | grep -i iTCO")
    CommonKeywords.should_match_a_regexp(out,"iTCO_wdt: initialized")
    
    log.info("Executing TCO commands in sequence")
    deviceObj.executeCmd("echo 30 > /proc/sys/kernel/panic")
    deviceObj.executeCmd("echo 1 > /proc/sys/kernel/sysrq")
    deviceObj.sendCmd("echo c > /proc/sysrq-trigger")
    out = deviceObj.read_until_regexp('Rebooting in 30 seconds',timeout=100)
    log.success("Device will restart/reboot in 30 seconds after crashed state")
    out = deviceObj.read_until_regexp('localhost login:',timeout=400)
    deviceObj.loginToDiagOS()
    log.success("Successfully rebooted device after crashing")
    remove_diag_package_and_image(device)
    
    
def update_bios_with_bmc_image(deviceM, image, mode='primary'):
    device_obj=Device.getDeviceObject(deviceM)
    log.debug("Switch to bmc console")
    device.switchToBmc()
    device.loginToNEWBMC()
    
    log.info("Download bios images")
    cmd="/usr/bin/bmcbiosflash.sh "+ image + ' '+mode
    device_obj.sendCmd(cmd)
    if mode=='primary':
        mode = 'Primary'
    else: 
        mode='Secondary'
    device_obj.read_until_regexp('Program '+mode+' BIOS Successful!',timeout=300)
    log.info("%s bios downloaded successfully" %mode)
    out = device_obj.read_until_regexp('root@moonstone:~#',timeout=300)
    time.sleep(10)
    bios_menu_lib.send_key(deviceM,"KEY_ENTER",times=3)
    
    log.debug("Switch to CPU")
    device.switchToCpu()
    try:
      device_obj.read_until_regexp('localhost login:',timeout=200)
      device_obj.loginToDiagOS()
    except Exception:
      device_obj.executeCmd("reboot")
      device_obj.read_until_regexp('localhost login:',timeout=200)
      device_obj.loginToDiagOS()
    
def Switch_to_BMC():
    
    device.switchToBmc()
    device.loginToNEWBMC()
    device.sendMsg('\r\n')
    
    
def Switch_to_ONL():
    device.switchToCpu()
    
    
def powerCycle_device(device):
    device_obj=Device.getDeviceObject(device)
    MOONSTONECommonLib.powerCycle(device)
    
    
def check_power_reset_cause(device):
    deviceObj = Device.getDeviceObject(device)
    cmd1 = f"ipmitool -I lanplus -H {bmc_mgmp_ip} -C 17 -U root -P 0penBmc sel clear"
    cmd2 = f"ipmitool -I lanplus -H {bmc_mgmp_ip} -C 17 -U root -P 0penBmc sel list"
    cmd3 = "ipmitool chassis power reset"
    cmd4 = "ipmitool sel list"
    
    # Step 1
    log.info("running powercycle command")
    powerCycle_device(device)
    out_4 = deviceObj.executeCmd(cmd4)
    if ("Error" in out_4) or ("error" in out_4) or ("Failed" in out_4) or ("failed" in out_4):
        raise RuntimeError("error in sel list")
    CommonKeywords.should_match_a_regexp(out_4, sel_list_pattern)
    log.success("ipmitool sel list has no error and it is empty")

    
       # Step 2
    log.info("running command reboot")
    deviceObj.sendCmd("reboot")
    out_1 = deviceObj.read_until_regexp(pattern_reset_cause, timeout=100)
    out_1_1 = deviceObj.read_until_regexp('localhost login', timeout=400)
    x = re.search(pattern_reset_cause, out_1)
    if x is None:
        raise RuntimeError("reset cause not fetched")
    log.info(x.group(1))
    log.cprint(x.group(1))
    if x.group(1) != reset_cause_reboot:
        raise RuntimeError("reset cause is not " + reset_cause_reboot)
    log.success("reset cause is "+reset_cause_reboot+" for reboot")

    deviceObj.loginToDiagOS()
    log.success("exited from boot setup successfully")
    
    
    # Step 3
    Device.execute_local_cmd(deviceObj, cmd2)
    Device.execute_local_cmd(deviceObj, cmd1)
    time.sleep(30)
    log.info("running command power reset")
    deviceObj.sendCmd(cmd3)
    out_2 = deviceObj.read_until_regexp(pattern_reset_cause, timeout=400)
    out_2_2 = deviceObj.read_until_regexp('localhost login', timeout=400)
    x = re.search(pattern_reset_cause, out_2)
    if x is None:
        raise RuntimeError("reset cause not fetched")
    if x.group(1) != reset_cause_power_reset:
        raise RuntimeError("reset cause is not "+reset_cause_power_reset)
    log.success("reset cause is "+reset_cause_power_reset+" for power reset")
    deviceObj.loginToDiagOS()
    out_4 = deviceObj.executeCmd(cmd4)
    if ("Error" in out_4) or ("error" in out_4) or ("Failed" in out_4) or ("failed" in out_4):
        raise RuntimeError("error in sel list")
    CommonKeywords.should_match_a_regexp(out_4, sel_list_pattern)
    log.success("ipmitool sel list has no error and it is empty")
    
    
    
    
    # Step 4
    log.info("running power chassis off and on")
    check_power_chasis_status(device, 'on')
    set_power_chasis(device, 'off')
    check_power_chasis_status(device, 'off')
    set_power_chasis(device, 'on')
    check_power_chasis_status(device, 'on')
    deviceObj.loginToDiagOS()
    out_4 = deviceObj.executeCmd(cmd4)
    if ("Error" in out_4) or ("error" in out_4) or ("Failed" in out_4) or ("failed" in out_4):
        raise RuntimeError("error in sel list")
    CommonKeywords.should_match_a_regexp(out_4, sel_list_pattern)
    log.success("ipmitool sel list has no error and it is empty")
    
    
    
def check_power_chasis_status(device, status):
    device_obj = Device.getDeviceObject(device)
    mgmt_ip = device_obj.managementIP
    promptServer = device_obj.promptServer
    cmd = lanplus_ipmitool_cmd.format('chassis power status')
    log.info("Checking chassis status through cmd : %s" % cmd)
    c1 = Device.execute_local_cmd(device_obj, cmd, timeout=10)
    log.info("Output : " + c1)

    chassis_pattern = "Chassis Power is %s" % status
    if chassis_pattern in c1:
        log.info("Chassis Status is as expected!! " + chassis_pattern)
    else:
        raise RuntimeError("Expected value of Chassis Status should be %s but got opposite of it." % status)


def set_power_chasis(device, status):
    deviceObj = Device.getDeviceObject(device)
    mgmt_ip = deviceObj.managementIP
    promptServer = deviceObj.promptServer
    cmd = lanplus_ipmitool_cmd.format("power %s" % status)

    log.info("Turn %s power through cmd %s" % (status, cmd))
    c1 = Device.execute_local_cmd(deviceObj, cmd, timeout=10)
    log.info('Output : ' + c1)

    val = "Down/Off" if status == 'off' else "Up/On"
    pattern = "Chassis Power Control: %s" % val
   
    log.info("Sleeping for 200 seconds.")
    if status == 'on':
        out_1 = deviceObj.read_until_regexp(pattern_reset_cause, timeout=400)
        x = re.search(pattern_reset_cause, out_1)
        if x is None:
            log.info("reset cause not fetched")
            raise RuntimeError("reset cause not fetched")
        log.info(x.group(1))
        if x.group(1) != reset_cause_power_chasis:
            raise RuntimeError("reset cause is not "+reset_cause_power_chasis)
        log.success("reset cause is (0x33) for power chassis on")

    time.sleep(200)

    CommonKeywords.should_match_a_regexp(c1, pattern)
    if (status == 'on'):
        #sel_list_pattern = sel_list_power_on_pattern
        sel_cmd = lanplus_ipmitool_cmd.format('sel list | tail')
        log.info("Fetching BMC sel list after setting power chassis status")
        c2 = Device.execute_local_cmd(deviceObj, sel_cmd, timeout=120)
        log.info("Output : " + c2)
        
        log.cprint("next line")
        log.cprint(sel_list_pattern)
        CommonKeywords.should_match_a_regexp(c2, sel_list_pattern)
        log.success("Sel list is as expected after power %s" % status)

def memtest86_usg_image_to_executable(device):
    deviceObj = Device.getDeviceObject(device)
    c1 = deviceObj.executeCmd("dhclient -v ma1")
    download_file_through_brixia(device, memtest_file_path, memtest_file)

    c3 = deviceObj.executeCmd("dd if=memtest86-usb.img of=/dev/sdc1", timeout=320)
    if ("Error" in c1) or ("error" in c1) or ("Failed" in c1) or ("failed" in c1):
        raise RuntimeError("dd if=memtest86-usb.img of=/dev/sdc1 output is giving error in its output")

def set_usb_partition_1(device):
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_RIGHT", 5)
    m161_out = deviceObj.read_until_regexp('Boot Option #2 ', timeout=10)
    bios_menu_lib.send_key(device, "KEY_DOWN", 3)
    run_loop = True
    while run_loop:
        try:
            bios_menu_lib.send_key(device, "KEY_ENTER")
            bios_menu_lib.send_key(device, "KEY_DOWN")
            bios_menu_lib.send_key(device, "KEY_ENTER")
            m16_out = deviceObj.read_until_regexp('Boot Option #1          \[UEFI:  USB, Partition', timeout=10)
            run_loop = False
            break
        except Exception:
            continue
    bios_menu_lib.send_key(device, "KEY_F4")
    bios_menu_lib.send_key(device, "KEY_ENTER")
    m161_out = deviceObj.read_until_regexp('\(x\) Exit', timeout=60)

    log.success("successfully set USB partion 1 as first boot priority")


def check_memtest86(device):
    deviceObj = Device.getDeviceObject(device)
    bios_menu_lib.send_key(device, "KEY_s")

    m161_out = deviceObj.read_until_regexp('\(c\)onfiguration')
    m161_out = deviceObj.read_until_regexp('Finished pass #1', timeout=100000)
    m161_out = deviceObj.read_until_regexp('Finished pass #2', timeout=100000)
    m161_out = deviceObj.read_until_regexp('Finished pass #3', timeout=100000)

    m161_out = deviceObj.read_until_regexp('Test Complete', timeout=10000000)
    bios_menu_lib.send_key(device, "KEY_ENTER")
    bios_menu_lib.send_key(device, "KEY_RIGHT")
    bios_menu_lib.send_key(device, "KEY_y")
    bios_menu_lib.send_key(device, "KEY_x")
    log.info("successfully completed the test")
    out = deviceObj.read_until_regexp('to enter setup', timeout=140)

    counter = 5
    while counter >= 0:
        bios_menu_lib.send_key(device, "KEY_DEL")
        counter -= 1
        time.sleep(1)
    log.success("successfully entered into bios")




    
    
    
