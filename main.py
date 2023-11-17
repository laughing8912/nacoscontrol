#encoding=utf-8

from com.laughing.nacoscontrol.NacosControl import NacosControl
import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-sname", "--servername", required=True,help="Please enter micro server name!")
    ap.add_argument("-i", "--ip", required=True,help="Please enter micro server ip!")
    ap.add_argument("-p", "--port", required=True,help="Please enter micro server port!")
    ap.add_argument("-cm", "--controlmodel", required=True,help="Please enter controlModel!")
    ap.add_argument("-w", "--weight", required=False)
    args = vars(ap.parse_args())
    arg_service_name = args['servername']
    arg_service_ip = args['ip']
    arg_service_port = args['port']
    arg_service_control_model = args['controlmodel']
    arg_weight = args['weight']
    nacoscontrol=NacosControl()
    ''' 根据输入的指令执行相应的nacos操作
        down：在nacos中下线微服务
        up: 在nacos中上线微服务
        getstatus：获取微服务上线/下线状态
        monitorup：持续监听微服务上线状态，微服务已上线则停止监听
        monitordown：持续监听微服务下线状态，微服务已下线则停止监听
    '''
    if arg_service_control_model == "down":
        nacoscontrol.microServerInstanceDownLine(service_name=arg_service_name,ip=arg_service_ip,port=arg_service_port,weight=arg_weight)
    elif arg_service_control_model == "up":
        nacoscontrol.microServerInstanceUpLine(service_name=arg_service_name,ip=arg_service_ip,port=arg_service_port,weight=arg_weight)
    elif arg_service_control_model == "getstatus":
        nacoscontrol.getMicroServerInstanceStatus(service_name=arg_service_name,ip=arg_service_ip,port=arg_service_port)
    elif arg_service_control_model == "monitorup":
        nacoscontrol.monitorMicroServerInstanceStatus(service_name=arg_service_name,ip=arg_service_ip,port=arg_service_port,status=True)
    elif arg_service_control_model == "monitordown":
        nacoscontrol.monitorMicroServerInstanceStatus(service_name=arg_service_name,ip=arg_service_ip,port=arg_service_port,status=False)
    else:
        print("请输入正确的指令！")

if __name__ == '__main__':
    main()


