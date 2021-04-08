#__author__:"jcm"
import pika
import socket
import json
import subprocess

class batch_server(object):
    def __init__(self):
        try:
            csock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            csock.connect(('8.8.8.8',80))
            (addr,port) = csock.getsockname()
            csock.close()
            self.host = addr
        except socket.error as e:
            self.host ='127.0.0.1'
        self.credentials = pika.PlainCredentials('admin','admin')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.157.169',
                                                                            port=5672,
                                                                            virtual_host='/',
                                                                            credentials=self.credentials))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='direct_logs',
                                      exchange_type='direct')
        result = self.channel.queue_declare('',exclusive=True)
        self.queue_name = result.method.queue
    def _on_request(self,ch,method,props,body):
        '''
        :param ch:
        :param method:
        :param props:
        :param body:
        :return:
        :callback: (task_id,cmd_result)
        '''
        cmd = body.decode()
        commond_result = subprocess.getstatusoutput(cmd)[1]
        cmd_res = '------------------%s---------------\n'%self.host + commond_result+'\n'
        callback = json.dumps((props.message_id,cmd_res))
        print('----------------执行了命令：%s ------------------\n'%cmd)
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties = pika.BasicProperties(
                             correlation_id = props.correlation_id),
                            body =callback
                        )
        # ch.basic_ack(delivery_tag=method.delivery_tag)
    def get_message(self):
        self.channel.queue_bind(exchange='direct_logs',
                                queue=self.queue_name,
                                routing_key=self.host)
        self.channel.basic_consume(self.queue_name,
                                   self._on_request,
                                   True)
        print('-------start rpc server ----------')
        self.channel.start_consuming()




if __name__ =='__main__':
    ss = batch_server()
    ss.get_message()































