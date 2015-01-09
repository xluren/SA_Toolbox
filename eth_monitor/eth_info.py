#!/usr/bin/python2.6 
import re
import os 
import json
import commands 
import ConfigParser


def read_conf(conf_file):
    config = ConfigParser.ConfigParser()
    config.read(conf_file)
    option_dict={}

    secs=config.sections()
    for sec in secs:
        option_dict[sec]={}
        for option in  config.options(sec):
            key=option
            value=config.get(sec,key)
            option_dict[sec][key]=value

    return option_dict

def get_net_info(conf_dict):
    net_file=conf_dict["network"]["net_file"]

    net_info_dict={}
    with open(net_file) as file_handle:

        while 1:
            line=file_handle.readline()
            if line.find(":") != -1:
                key=line.split(":")[0].strip()
                value=line.split(":")[1].split()
                net_info_dict[key]={}

                net_info_dict[key]["RX_traffic"]=value[0]
                net_info_dict[key]["RX_packet"]=value[1]
                net_info_dict[key]["RX_packet_error"]=value[2]
                net_info_dict[key]["RX_packet_drop"]=value[3]

                net_info_dict[key]["TX_traffic"]=value[8]
                net_info_dict[key]["TX_packet"]=value[9]
                net_info_dict[key]["TX_packet_error"]=value[10]
                net_info_dict[key]["TX_packet_drop"]=value[11]
            if not line:
                break

    return  net_info_dict

def get_eth_info(conf_dict):
    network_script_path=conf_dict["network"]["network_script_path"]
    eth_info_dict={}

    ifcfg_list=os.listdir(network_script_path)
    for ifcfg in ifcfg_list:
        if ifcfg.startswith("ifcfg") and not ifcfg.endswith("lo"):
            key=ifcfg.split("-")[-1].strip()
            line_list=open(network_script_path+ifcfg).readlines()
            ip=""
            for line in  line_list:
                if line.startswith("IPADDR"):
                    ip=line.split("=")[-1].strip().strip('"')
            eth_info_dict[key]=ip
    return eth_info_dict

def cal_info(net_info_dict,eth_info_dict):
    cal_keys="traffic,packet,packet_error,packet_drop"
    RT='RX,TX'
    net_type="inside,outside"

    cal_dict={}
    for item in cal_keys.split(","):
        for rt_type in  RT.split(","):
            for  net in net_type.split(","):
                cal_dict[net+"_"+rt_type+"_"+item]=0

    for eth_name,ip_addr in  eth_info_dict.items():
        net_type="inside"
        for  key in  cal_keys.split(","):
            for rt_type in RT.split(","):
                cal_dict[net_type+"_"+rt_type+"_"+key]=net_info_dict[eth_name][rt_type+"_"+key]
    return cal_dict

def zabbix_send(conf_dict):

    net_info_dict=get_net_info(conf_dict)
    eth_info_dict=get_eth_info(conf_dict)

    cal_result={}
    cal_dict_now=cal_info(net_info_dict,eth_info_dict)

    json_output_file=conf_dict["network"]["json_output_file"]
    zabbix_send_file=conf_dict["common"]["zabbix_send_file"]

    monitor_key,monitor_value=check_readonly(conf_dict)

    try:
        file_handle=file(json_output_file)
        cal_dict_last=json.load(file_handle)["last"]
    except:
        pass 
    else:
        with open(zabbix_send_file,"w") as file_handle:
            for k,v in  cal_dict_now.items():
                file_handle.write("%s %d" %(k,int(v)-int(cal_dict_last[k])))
            file_handle.write("%s %d" % (monitor_key,monitor_value))


    cal_result["last"]=cal_dict_now
    json_str=json.dumps(cal_result)

    with open(json_output_file,"w") as f:
        f.write(json_str)


def check_readonly(conf_dict):
    mounts_file=conf_dict["file_system"]["mounts_file"]
    print mounts_file
    readonly_flag=0
    pattern=re.compile('(^|,)ro($|,)')
    with open(mounts_file) as file_handle:
        while 1:
            line = file_handle.readline()
            if not line:
                break
            else:
                match=pattern.search(line.split()[3])
                if match:
                    readonly_flag=1
                    break
    return "file_system_readonly",readonly_flag

conf_dict=read_conf("./eth_info.conf")
zabbix_send(conf_dict)
