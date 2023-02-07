# 功能
build  指定的镜像

## 用法
1. 先根据用户环境，手动制作一个基础镜像。
2. 将安装文件解压放到一个目录中。多文件快速解压命令见备注。
3. 运行工具，制作镜像。工具会自动build和检查。最终输出push命令。如果制作失败，会输出失败列表。
4. 复制输出的命令执行push镜像即可。

## 工具流程
工具会做如下操作
1. 编译 Dockerfile 模板
2. 初始化 build 目录,解析模板中需要COPY的文件到 build 目录。
3. build
4. 检查镜像
5. 输出push命令

工具执行完后，可复制输出的命令执行push。失败的会有失败列表输出。

# 操作
## 解压tidb企业版安装包
将企业服务安装包的镜像解压到指定目录。 这个目录用于参数 --mirror-dir
```bash
ls tidb-enterprise-server-v6.1.1-linux-amd64/*.tar.gz | xargs -P4 -i  tar xzvf '{}' -C mirror
```
## 参考命令
建议将日志输出到文件，这样标准输出的信息可以直接复制执行。
--dockerfile-template  支持通配符或多个文件
```bash
python build.py --mirror-dir /tmp/build/mirror/ --work-path /tmp/worker/ --dockerfile-template dockerfile/tikv --base-image gcr.io/pingcap-public/pingcap/alpine-glibc:alpine-3.14.3 --image-namespace "pingcap.com/test" --image-version v6.1.1 --log-file=/tmp/build.log
```

# 备注
## 注意
1. 历史镜像制作的遗留问题，lightning镜像中会有br工具，请注意。
2. 如用户有特殊配置，比如yum repo等，请先制作base镜像，再以base镜像作为基础制作组件镜像。
3. check_image 中，通过运行镜像判断镜像是否可用，passCodes可根据情况更新，默认返回值为0。

## 清理重复镜像
如果重复build同tag名的镜像，新的镜像会把旧的镜像取代。如果制作镜像的机器空间满了，可以清理下。
如果镜像在使用，则不会被清理。
``` bash
docker rmi `docker images|grep none|awk '{print $3}'`
```