#__author__:"jcm"
import pika
import uuid
import threading
import queue
import os,re
import random,math
import json

local = threading.local()

BASEPATH = os.path.dirname(os.path.abspath(__file__))

class batch_management(object):
    def __init__(self):
        self.response_queue = queue.Queue()
        self.cmd_data = {}
        self.task_id =''
        self.error_connection =queue.Queue()
    def _get_result(self):
        while self.response_queue.qsize() != 0:
            response = self.response_queue.get()
            response = json.loads(response.decode('utf8'))
            if response[0] in self.cmd_data:
                self.cmd_data[response[0]].append(response[1])
            else:
                self.cmd_data[response[0]] = [response[1],]

    def _call_result(self,command,host,task_id):
        corr_id = str(uuid.uuid4())
        response = None
        def _on_response(ch, method, props, body):
            nonlocal response
            if corr_id == props.correlation_id:
                response = body
        try:
            credentials = pika.PlainCredentials('admin', 'admin')

            connection = pika.BlockingConnection(pika.ConnectionParameters(host=host,
                                                                           port=5672,
                                                                           virtual_host='/',
                                                                           credentials=credentials))
            channel = connection.channel()
            result = channel.queue_declare('', exclusive=True)
            callback_queue = result.method.queue
            channel.basic_consume(callback_queue,
                                  _on_response,
                                  True
                                  )
            channel.basic_publish(exchange='',
                                       routing_key='rpc_queue',
                                       properties=pika.BasicProperties(
                                           reply_to=callback_queue,
                                           correlation_id=corr_id,
                                           message_id=task_id
                                       ),
                                       body=str(command)
                                       )
            while response is None:
                connection.process_data_events()
            self.response_queue.put(response)

        except pika.exceptions.AMQPConnectionError or  pika.exceptions.ChannelClosedByBroker as e:
            self.error_connection.put(host)


    def _run(self,command_data):
        host_list = re.findall(r'[1-9]{1}[0-9]{0,1}[0-9]{0,1}.[0-9]{1}[0-9]{0,1}[0-9]{0,1}.[0-9]{1}[0-9]{0,1}[0-9]{0,1}.[1-9]{1}[0-9]{0,1}[0-9]{0,1}',command_data)
        cmd = re.findall(r'"(.*)"',command_data)[0].strip()
        self.task_id = str(math.floor(1e5 * random.random()))
        for i in host_list:
            t = threading.Thread(target=self._call_result, args=(cmd, i, self.task_id))
            t.start()
        self._get_result()
        print('task id: %s' % self.task_id)

    def _check_task(self,data):
        self._get_result()
        task_id = str(data).split(' ')[1].strip()
        if task_id in self.cmd_data:
            for i in self.cmd_data[task_id]:
                print(i)
            if self.error_connection.qsize():
                while self.error_connection.qsize() != 0:
                    error_host = self.error_connection.get()
                    self.cmd_data[task_id].append('------------%s---------------\n输入的IP:%s有误，无法连接rabbitmq\n'%(error_host,error_host))
        else:
            print('输入的task id：%s 有误'%task_id)

    def start(self):
        while True:
            cmd = input('>>:')
            cmd_list = cmd.strip().split(' ')
            if hasattr(self,'_%s'%cmd_list[0]):
                func = getattr(self,'_%s'%cmd_list[0])
                func(cmd)

if __name__ =='__main__':
    ss = batch_management()
    ss.start()

