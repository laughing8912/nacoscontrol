# encoding=utf-8
import time
import os
import configparser
import nacos
import requests


class NacosControl:
    cf = configparser.ConfigParser()
    cf.read(os.path.join(os.getcwd(),"nacoscontrol/conf/config.ini"),encoding="utf-8")
    server_address = cf.get("Nacos-Config","server_address")
    namespace = cf.get("Nacos-Config","namespace")
    username = cf.get("Nacos-Config","username")
    password= cf.get("Nacos-Config","password")
    cluster_name = cf.get("Nacos-Config","cluster_name")
    group_name = cf.get("Nacos-Config","group_name")
    metadata = cf.get("Nacos-Config","metadata")
    # 监听微服务状态的时间间隔
    monitortimeinterval = int(cf.get("Nacos-Config","monitortimeinterval"))
    # 是否启用监听微服务启动结果
    monitorprocstartresult = None
    if cf.get("MicroService-Config","monitorprocstartresult") == "True":
        monitorprocstartresult = True
    else:
        monitorprocstartresult = False
    # 证明微服务实例健康的URL
    procinterfaceurl = cf.get("MicroService-Config","procinterfaceurl")

    def __init__(self, server_address, namespace):
        self.server_address = server_address
        self.namespace = namespace

    def __init__(self):
        pass

    # nacos客户端工具实例化
    client = nacos.NacosClient(server_address , namespace=namespace , username=username , password=password)

    # 微服务下线
    def microServerInstanceDownLine(self, service_name, ip, port,weight=None):
        try:
            self.client.modify_naming_instance(service_name=service_name, ip=ip, port=port,
                                               cluster_name=self.cluster_name,
                                               weight=weight, metadata=self.metadata, enable=False)
        except Exception as e:
            print(e.__context__)
            print("执行服务下线操作发生异常")
            return False
        else:
            return True

    # 微服务上线
    def microServerInstanceUpLine(self, service_name, ip, port,weight=None):
        try:
            self.client.modify_naming_instance(service_name=service_name, ip=ip, port=port,
                                               cluster_name=self.cluster_name,
                                               weight=weight, metadata=self.metadata, enable=True)
        except Exception :
            print("执行服务上线操作发生异常")
            return False
        else:
            return True

    # 获取微服务状态
    def getMicroServerInstanceStatus(self, service_name, ip, port):
        # status_msg=self.client.send_heartbeat(service_name=service_name, ip=ip, port=port, cluster_name=self.cluster_name)
        hosts_list = self.client.list_naming_instance(service_name=service_name, clusters=self.cluster_name,
                                                    namespace_id=self.namespace, group_name=self.group_name, healthy_only=True).get("hosts")
        # print(hosts_list)
        enable_status = False
        if hosts_list is None or hosts_list == []:
            enable_status = False
            return enable_status
        else:
            index = 0
            for i in range(0, len(hosts_list)):
                if str(hosts_list[i].get("ip")) == ip and str(hosts_list[i].get("port")) == port:
                    index = i
                    enable_status = hosts_list[index].get("enabled")
                    break
                else:
                    continue
            if enable_status:
                return enable_status
            else:
                enable_status = False
                return enable_status

    ''' 获取微服务启动结果
        ip：微服务IP地址
        port：微服务端口
    '''
    def getMicroServiceStartResult(self,ip,port):
        requesturl = "http://"+ip+":"+port+self.procinterfaceurl
        getmicrostartresult = False
        status = None
        try:
            response = requests.get(requesturl)
            jsondata = response.json()
            status = jsondata["status"]
        except Exception :
            return getmicrostartresult
        if status != None or status != '':
            getmicrostartresult = True
        return getmicrostartresult

    ''' 监听微服务上线/下线状态
        service_name：微服务实例名
        ip：微服务IP地址
        port：微服务端口
        status：布尔型，上线为True，下线为False
    '''
    def monitorMicroServerInstanceStatus(self, service_name, ip, port, status):
        up_down_status = True
        i = 0
        microprocstartstatus = False
        if status:
            write_time_note = "上线等待时间"
        else:
            write_time_note = "下线等待时间"
        while up_down_status:
            time.sleep(self.monitortimeinterval)
            micro_status = self.getMicroServerInstanceStatus(service_name=service_name, ip=ip, port=port)
            if status == True and micro_status == False and self.monitorprocstartresult:
                microprocstartstatus = self.getMicroServiceStartResult(ip,port)
                if microprocstartstatus:
                    self.microServerInstanceUpLine(service_name, ip, port,weight=None)
            i += 1
            print(write_time_note+"："+str(i*self.monitortimeinterval)+"秒，等待结果："+str(micro_status))
            if micro_status == status:
                up_down_status = False