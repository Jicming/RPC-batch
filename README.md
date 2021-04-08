RPC-rabbitmq 
目的：使用消息队列 批量执行命令、结果实时返回。

1.其中multiThread 文件夹下是使用rabbitmq 加多线程的方式，客户端连接远程主机上安装的rabbitmq实现批量远程执行任务。

2.excheange文件夹下使用了rabbitmq exchange的direct模式（通过routingkey和exchange决定那个唯一的queue可以接收消息）



效果如下：输入run "df -h" --hosts 192.168.4.55 10.4.3.5，可在输入ip的主机上执行命令并返回任务id，此过程不阻塞，

:run "df -h " --hosts 192.168.4.55 10.4.3.5

task id:45334

输入 check_task ID 可以不断check, 将已返回的命令结果打印到屏幕，此过程不阻塞

:check_task 41238

----------192.168.190.130------------

文件系统 容量 已用 可用 已用% 挂载点

/dev/mapper/centos-root 47G 5.5G 42G 12% /

devtmpfs 470M 0 470M 0% /dev

tmpfs 487M 0 487M 0% /dev/shm

tmpfs 487M 8.0M 479M 2% /run

tmpfs 487M 0 487M 0% /sys/fs/cgroup

/dev/sda1 1014M 150M 865M 15% /boot

tmpfs 98M 0 98M 0% /run/user/0

----------192.168.190.131------------

文件系统 容量 已用 可用 已用% 挂载点

/dev/mapper/centos-root 47G 5.5G 42G 12% /

devtmpfs 470M 0 470M 0% /dev

tmpfs 487M 0 487M 0% /dev/shm

tmpfs 487M 8.0M 479M 2% /run

tmpfs 487M 0 487M 0% /sys/fs/cgroup

/dev/sda1 1014M 150M 865M 15% /boot

tmpfs 98M 0 98M 0% /run/user/0
