### <p align=center>nacos控制及监听工具</p>
#### 工具说明
该工具用于执行nacos的上线/下线操作以及监听nacos的状态,使用该工具可以实现注册到nacos微服务的用户无感知滚动更新(前提：微服务集群部署了多个节点)
#### 依赖安装
```shell
pip install nacos-sdk-python #安装该版本目前不支持账号密码鉴权操作
#配置升级说明
git clone https://github.com/laughing8912/nacos-sdk-python.git nacos
cd nacos
#如果有安装官方版本的nacos则卸载掉
pip3 uninstall nacos-sdk-python
pip3 install jsonpath
python3 setup.py install
pip3 install configparser
pip3 install argparse
pip3 install requests
```
#### 命令行说明：
``` properties
-sname , --servername 必须 注册到nacos的微服务名称
-i , --ip 必须 注册到nacos的微服务ip地址
-p , --port 必须 注册到nacos的微服务端口
-cm , --controlmodel 必须 操作类型，枚举值
    down：在nacos中下线微服务
    up: 在nacos中上线微服务
    getstatus：获取微服务上线/下线状态
    monitorup：持续监听微服务上线状态，微服务已上线则停止监听
    monitordown：持续监听微服务下线状态，微服务已下线则停止监听
-w , --weight 可选 微服务权重，不输入时默认值为1
```
#### 配置文件说明：
- 配置文件路径：conf/config.ini
- 配置参数说明：详见配置文件中的注释
#### 命令行示例
```shell
python nacoscontrol/main.py -sname service-xxx -i xx.xx.xx.xx -p xxxx -cm down
python nacoscontrol/main.py -sname service-xxx -i xx.xx.xx.xx -p xxxx -cm up
python nacoscontrol/main.py -sname service-xxx -i xx.xx.xx.xx -p xxxx -cm monitordown
python nacoscontrol/main.py -sname service-xxx -i xx.xx.xx.xx -p xxxx -cm monitorup
```
#### 工具集成示例
- 前置条件

<font color=red>nacos迭代到2.1.3之后，Java微服务启动后不会在nacos中改变执行下线操作时设置的结果。如果Java微服务程序启动后未告知nacos服务已上线，则需启用本程序的监听功能以佐证微服务进程能正常提供服务，获取到接口结果后(本程序获取的结果忽略了返回的值UP/DOWN，有结果则认为微服务程序能正常提供服务，否则认为微服务程序还未启动成功)，由本程序执行上线操作，从而达到滚动更新效果。</font>

- jenkins关键代码
```groovy
script {
    ansiblePlaybook(
        playbook: "${env.WORKSPACE}/java_publish_prod.yml",
        inventory: "${env.WORKSPACE}/hosts",
        credentialsId: 'vagrant',
        extraVars:[
            source_dir: "${source_dir}",
            branch_name: "${branch_name}",
            version: "-"+"${env.BUILD_NUMBER}",
            target_host: "${target_host}",
            target_dir: "${target_dir}",
            micro_service_name: "${micro_service_name}",
        ]
    )
}
```
- ansible关键代码
```yaml
- hosts: "{{target_host}}"
  serial: 1
  tasks:
    - name: "启动JAVA"
      shell: 'sh start-service.sh'
      args:
        chdir: "{{target_dir}}"
      register: start_result
    - debug:
        msg: "{{start_result.stdout_lines}}"
      when: start_result.stdout_lines is defined
```
- java启动脚本
```shell
#!/bin/bash
JAVA="java"
pythoncmd="/usr/bin/python3"
ifconfigcmd="/usr/sbin/ifconfig"
package=`ls -lrc target/|grep .jar$|head -n1|awk '{print $9}'`
killprogressname=`echo ${package}| sed -e 's/-[0-9]*.[0-9]*.[0-9]*.jar$//g'`
port="xxxx"
username="xxxx" #nacos登录用户名
password="xxxx" #nacos登录密码
LOGSTASH_PARAM=""
logfile="/dev/null"
if [   -z "$1" ] ;then
    echo "日志目录为：${logfile}"
else
    logfile=$1
    echo "日志目录为：${logfile}"
fi
#生产环境配置中心ID
nacos_namespace="xxxx"
NACOS_OPT="${NACOS_OPT} --spring.cloud.nacos.discovery.namespace=${nacos_namespace} --spring.cloud.nacos.config.namespace=${nacos_namespace}"
NACOS_OPT="${NACOS_OPT} -Dfile.encoding=utf-8  --spring.cloud.nacos.username=${username} --spring.cloud.nacos.password=${password}"
server_name="xxxx"
ip_addr=`${ifconfigcmd} | grep  "inet"|grep "xxx.xx" | awk '{ print $2}'`
# 下线微服务
${pythoncmd} nacoscontrol/main.py -sname ${server_name} -i ${ip_addr} -p ${port} -cm down
# 等待微服务下线成功
${pythoncmd} nacoscontrol/main.py -sname ${server_name} -i ${ip_addr} -p ${port} -cm monitordown
echo "kill $package 进程"
ps -aux|grep target/${killprogressname}|grep -v grep| awk '{print $2}'| xargs kill -9
echo "创建logs 目录"
if [ ! -d "logs" ];then
  mkdir logs
else
  echo "文件夹已经存在"
fi
echo "启动$package"
rm -rf logs/start.out
JAVA_OPT="${JAVA_OPT} -server -Xms512m -Xmx2048m -Xmn256m -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=320m"
nohup $JAVA ${JAVA_OPT} -jar target/$package --server.port=$port ${NACOS_OPT} 2>&1 >> ${logfile} &
# 等待微服务上线成功
${pythoncmd} nacoscontrol/main.py -sname ${server_name} -i ${ip_addr} -p ${port} -cm monitorup
echo "service is start,pid is:`ps -aux|grep target/$package|grep -v grep| awk '{print $2}'`,port is:${port}"
```
#### 其它说明
- 联系方式

使用过程中如碰到问题可扫描下面微信二维码联系本人

![1700189602468](assets/1700189602468.png)
