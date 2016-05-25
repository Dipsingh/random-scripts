
__author__ = 'dipsingh'

from ciscoconfparse import CiscoConfParse
import os ,argparse,re

def arguments():
 ''' Function to define the script command line arguments '''
 global config_file

 parser = argparse.ArgumentParser(description='A Python implementation for auditing qos trust on trunk port and Access Port.')
 parser.add_argument('-c', '--config', help='Specify a host file', required=True)

 args = vars(parser.parse_args())

 if args['config']:
     config_file = args['config']

 return config_file


parse = CiscoConfParse(arguments())
cfgdiff = CiscoConfParse([])

text = config_file
re1='(ag)'

rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
l2agg = rg.search(text)

if l2agg:
    for intf in parse.find_objects(r'^interface.+?thernet'):
        has_qos_trust = intf.has_child_with(r' mls qos trust dscp')
        is_switchport_trunk = intf.has_child_with(r'switchport mode trunk')
        is_switchport_infra = intf.has_child_with(r'INFRA:TRUNK*.*')

        if (is_switchport_trunk and is_switchport_infra) and (not has_qos_trust):
            cfgdiff.append_line("!")
            cfgdiff.append_line(intf.text)
            cfgdiff.append_line("mls qos trust dscp")
    cfgdiff.save_as(config_file+'_new')
    print ("Config Created with _new extension for L2AGG")
else:
    for intf in parse.find_objects(r'^interface.+?thernet'):
        has_qos_trust = intf.has_child_with(r' mls qos trust dscp')
        is_switchport_trunk = intf.has_child_with(r'switchport mode trunk')
        is_switchport_infra = intf.has_child_with(r'INFRA:TRUNK*.*')
        is_switchport_access = intf.has_child_with(r'switchport mode access')
        is_switchport_shutdown = intf.has_child_with(r'shutdown')

        if (is_switchport_trunk and is_switchport_infra) and (not has_qos_trust):
            cfgdiff.append_line("!")
            cfgdiff.append_line(intf.text)
            cfgdiff.append_line("mls qos trust dscp")
        elif (is_switchport_access and (not is_switchport_shutdown)) and (not has_qos_trust):
            cfgdiff.append_line("!")
            cfgdiff.append_line(intf.text)
            cfgdiff.append_line("mls qos trust dscp")

    cfgdiff.save_as(config_file+'_new')
    print ("Config created with _new extension for TOR")


