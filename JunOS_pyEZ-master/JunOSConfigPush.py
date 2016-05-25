
__author__ = 'dipsingh'

from pprint import pprint
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *
from jnpr.junos import Device
from getpass import *
import argparse,sys,yaml,jinja2
from glob import glob



conf_file= 'BaseCosConfig.txt'
defaults = {
    'port':'22',
    'devices':[],
    'config_file':"BaseCosConfig.txt",
    'user':'',
    'password':'',
    'ssh_key':''
}

def parse_arguments(arguments):
    parser = argparse.ArgumentParser(description="utility to push configurations to JunOS devices")
    parser.add_argument("-d","--device", help="Devices to apply configuration to")
    parser.add_argument("--config", help="Config file to apply")
    parser.add_argument("-l","--device-list",help="File Containing list of devices to apply configuration to")
    parser.add_argument("-u","--user",help="Username to login to device")
    parser.add_argument("-p","--password",action='store_true',help="Prompt for password to login to device")
    parser.add_argument("-c","--confirm",action='store_true',help="Auto Confirm configuration changes(No diff changes review)",required=False)
    parser.add_argument("-P","--port",required=False,help="Netconf port to connect on",)
    args=parser.parse_args()
    return args


def get_device_list(file):
    try:
        devices = [line.strip() for line in open(file,'r')]
        pprint("devices i read from the file %s " %devices)
        return devices
    except IOError:
        pprint ("Error:Unable to read devices from file ")
        exit()

args = parse_arguments(sys.argv)

if args.port:
    port = args.port
elif defaults['port'] != '':
    port = defaults['port']
else:
    port = '22'

if args.password is True:
    password = getpass('Password for %s :' % args.user)
elif defaults['password'] != '':
    password = defaults['password']
else:
    password=''

if args.device:
    devices = [args.device]
elif args.device_list:
    devices = get_device_list(args.device_list)
elif defaults['devices'] != []:
    devices = defaults['devices']
else:
    pprint("Error: No device(s) specified")
    exit()

for device in devices:
    pprint('***Processing %s ***' % device)
    dev = Device(device,user=args.user,password=password,port=port,ssh_private_key_file=defaults['ssh_key'],gather_facts=False)
    try:
        dev.open()
    except ConnectError:
        pprint("Error: Unable to connect")
        continue


    dev.bind(cfg=Config)
    pprint("Locking Configuration")

    try:
        dev.cfg.lock()
    except LockError:
        pprint('Error: Failed to lock configuration')
        continue

    pprint("Pushing configuration from template %s" %args.config)

    datavars = yaml.load(open('seed.yamls').read())
    template = jinja2.Template(open('JunosTemplate.Jinja2').read())

    dev.cfg.load(template_path=template,template_vars=datavars,format = 'text',merge=True)
    dev.cfg.load(path="BaseCosConfig.txt",format = 'set',merge=True)


    pprint("Verifying configuration")
    commit_check = dev.cfg.commit_check()

    if commit_check is True:
        if args.confirm is True:
            pprint("Confirmation bypassed")
            dev.cfg.commit()
            dev.close()
            continue

        else:
            pprint("The following configs will be applied ")
            diff = dev.cfg.pdiff()
            commit_config = ''
            while commit_config != 'YES' and commit_config != 'NO':
                commit_config = raw_input('Apply configuration (YES/NO)')
                if commit_config == 'YES':
                    pprint("Commiting")
                    rsp = dev.cfg.commit()
                    if rsp is True:
                        pprint ("Commit successful")
                        dev.close()
                elif commit_config == 'NO' :
                    pprint("Rolling back")
                    dev.cfg.rollback()
                    dev.close()

    else:
        pprint("Error: Config verification failed")
        dev.close()

