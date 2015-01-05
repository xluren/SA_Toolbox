#!/usr/bin/python2.6 
import re
import os 
import json

def get_net_info():
    net_info_dict={}
    with open("/proc/net/dev") as file_handle:
        while 1:
            line=file_handle.readline()
            if line.find(":") != -1:
                key=line.split(":")[0].strip()
                value=line.split(":")[1].split()
                net_info_dict[key]={}
                net_info_dict[key]["traffic_in"]=line.split(":")[1].split()[0]
                net_info_dict[key]["packet_in"]=line.split(":")[1].split()[1]
                net_info_dict[key]["error_in"]=line.split(":")[1].split()[2]
                net_info_dict[key]["drop_in"]=line.split(":")[1].split()[3]

                net_info_dict[key]["traffic_out"]=line.split(":")[1].split()[0]
                net_info_dict[key]["packet_out"]=line.split(":")[1].split()[1]
                net_info_dict[key]["error_out"]=line.split(":")[1].split()[2]
                net_info_dict[key]["drop_out"]=line.split(":")[1].split()[3]

            if not line:
                break
    return  net_info_dict

def get_eth_info():
    dir_name="/etc/sysconfig/network-scripts/"
    eth_info_dict={}
    ifcfg_list=os.listdir(dir_name)
    for ifcfg in ifcfg_list:
        if ifcfg.startswith("ifcfg") and not ifcfg.endswith("lo"):
            key=ifcfg.split("-")[-1].strip()
            line_list=open(dir_name+ifcfg).readlines()
            ip=""
            for line in  line_list:
                if line.startswith("IPADDR"):
                    ip=line.split("=")[-1].strip().strip('"')
            eth_info_dict[key]=ip
    return eth_info_dict

def cal_info(net_info_dict,eth_info_dict):
    cal_keys="traffic_in,packet_in,error_in,drop_in,traffic_out,packet_out,error_out,drop_out"
    cal_dict={}
    for item in cal_keys.split(","):
        cal_dict["inside_"+item]=0
        cal_dict["outside_"+item]=0

    for eth_name,ip_addr in  eth_info_dict.items():
        for  key in  cal_keys.split(","):
            cal_dict["inside_"+key]=net_info_dict[eth_name][key]

    return cal_dict
def dump_netinfo2file():
    net_info_dict=get_net_info()
    eth_info_dict=get_eth_info()
    cal_result={}
    cal_dict=cal_info(net_info_dict,eth_info_dict)
    json_file=file("/tmp/result")
    try:
        json_str=json.load(json_file)
    except:
        cal_result["last"]=cal_dict
        json_str=json.dumps(cal_result)
        with open("/tmp/result","w") as f:
            f.write(json_str)
    else:
        f=file("/tmp/result")
        json_dict_last=json.load(f)["last"]
        json_dict_now=cal_dict
        
        for k,v in  json_dict_now.items():
            if k.find("traffic")!=-1:
                print k,(int(v)-int(json_dict_last[k]))/1024
            else:
                print k,int(v)-int(json_dict_last[k])
dump_netinfo2file()
