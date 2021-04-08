#__author__:"jcm"
import pika
import socket
import uuid
import re
import math
import random
import queue
import  json

class batch_management(object):
    def __init__(self):
        self.response_list = []
        self.cmd_data = {}
        self.response_list = queue.Queue()
        self.error_connection = queue.Queue()
        try:
            csock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            csock.connect(('8.8.8.8',80))
            (addr,port) = csock.getsockname()
            csock.close()
            self.host = addr
        except socket.error as e:
            self.host = '127.0.0.1'
        self.credentials = pika.PlainCredentials('admin','admin')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host,
                                                                            port = 5672,
                                                                            virtual_host='/',
                                                                            credentials=self.credentials))
        self.channel =self.connection.channel()
        result = self.channel.queue_declare('',exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.callback_queue,self._on_response,True)#准备接收
    def _get_result(self):
        while self.response_list.qsize() != 0:
            response = self.response_list.get()
            response = json.loads(response.decode('utf8'))

            if response[0] in self.cmd_data:
                self.cmd_data[response[0]].append(response[1])
            else:
                self.cmd_data[response[0]] = [response[1],]
    def _on_response(self,ch,method,props,body):
        if self.corr_id == props.correlation_id:
            self.response = body
    def _call(self,command_hosts):
        '''

        :param Command_hosts: (cmd,[host1,host2])
        :return:
        '''
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.task_id = str(math.floor(1e5 * random.random()))


        self.channel.exchange_declare(exchange='direct_logs',
                                      exchange_type='direct')


        for i in command_hosts[1]:
            try:
                self.channel.basic_publish(exchange='direct_logs',
                                   routing_key=i,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                       message_id=self.task_id
                                   ),
                                   body=command_hosts[0])
            except pika.exceptions.AMQPConnectionError or pika.exceptions.ChannelClosedByBroker as e:
                self.error_connection.put(i)

        while self.response is None:
            '''
            response: (task_id,cmd_result)
            '''
            self.connection.process_data_events() #无阻塞接收
        self.response_list.put(self.response)

    def _run(self,command_data):
        host_list = re.findall(r'[1-9]{1}[0-9]{0,1}[0-9]{0,1}.[0-9]{1}[0-9]{0,1}[0-9]{0,1}.[0-9]{1}[0-9]{0,1}[0-9]{0,1}.[1-9]{1}[0-9]{0,1}[0-9]{0,1}',command_data)
        cmd = re.findall(r'"(.*)"',command_data)
        cmd = cmd[0].strip() if cmd else  re.findall(r"'(.*)'",command_data)[0].strip()
        self._call((cmd,host_list))
        print('task_id: %s'%self.task_id)
    def _check_task(self,task_data):
        self._get_result()
        task_id = str(task_data).split(' ')[1].strip()
        if task_id in self.cmd_data:
            for i in self.cmd_data[task_id]:
                print(i)
            if self.error_connection.qsize() !=0:
                error_host = self.error_connection.get()
                self.cmd_data[task_id].append('------------%s---------------\n输入的IP:%s有误，无法连接rabbitmq\n'%(error_host,error_host))


    def start(self):
        while True:
            cmd = input(">>:")
            cmd_list = cmd.strip().split(' ')
            if hasattr(self,'_%s'%cmd_list[0]):
                func = getattr(self,'_%s'%cmd_list[0])
                func(cmd)

if __name__ == '__main__':
    ss = batch_management()
    ss.start()














