#__author__:"jcm"
import pika
import re
import subprocess
import json
import socket
class batch_server(object):
    def __init__(self):
        try:
            csock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            csock.connect(('8.8.8.8', 80))
            (addr, port) = csock.getsockname()
            csock.close()
            self.host = addr
        except socket.error:
            self.host = "127.0.0.1"
        self.credentials = pika.PlainCredentials('admin', 'admin')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host,
                                                                            port=5672,
                                                                            virtual_host = '/',
                                                                            credentials=self.credentials))
        self.channel = self.connection.channel()
        self.queue = self.channel.queue_declare(queue='rpc_queue')
    def _on_request(self,ch,method,props,body):
        cmd = body.decode()
        command_result = subprocess.getstatusoutput(cmd)[1]
        cmd_res = '----------%s------------\n'%self.host+command_result+'\n'
        callback = json.dumps([props.message_id,cmd_res])
        print('-----------执行了命令：%s ------------- \n'%cmd)
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties = pika.BasicProperties(correlation_id=props.correlation_id),
                         body=callback)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    def get_message(self):
        # self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume('rpc_queue',self._on_request)
        self.channel.start_consuming()


if __name__ =='__main__':
    ss = batch_server().get_message()























