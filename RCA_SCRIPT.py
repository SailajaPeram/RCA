import paramiko
import time
import warnings
import os


class ssh_connect:
    def __init__(self):
        self.ssh_username = os.environ["SSH_USERNAME"]
        self.ssh_password = os.environ["SSH_PASSWORD"]
        self.admnpwd = os.environ["ADMIN_PASSWORD"]
        self.node1 = os.environ["NODE1_IP"]
        self.node2 = os.environ["NODE2_IP"]
        self.node3 = os.environ["NODE3_IP"]
        self.folder_name = os.environ["BUG_ID"]
        self.remote_server_ip = os.environ["REMOTE_SERVER_IP"]
        self.maglev_password = os.environ["MAGLEV_PASSWORD"]
        self.remote_server_username = os.environ["REMOTE_SERVER_USERNAME"]
        self.remote_server_password = os.environ["REMOTE_SERVER_PASSWORD"]
        self.variable = "maglev@"
        self.cluster_type = os.environ["THREE_NODE_CLUSTER"]
        self.text_file = os.environ["TEXT_FILE_NAME"]

    def ssh_login(self, port, ip, username, password):
        try:
            warnings.filterwarnings(action='ignore', module='.*paramiko.*')
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, port, username, password)
            time.sleep(2)
            global channel
            channel = ssh.invoke_shell()
            time.sleep(5)
            output = channel.recv(9999).decode('utf-8')
            return output
        except Exception as e:
            print("could not complete execution")

    def copy_function(self, ips_list, tarfiles_list):
        for i1, i2 in zip(ips_list, tarfiles_list):
            try:
                warnings.filterwarnings(action='ignore', module='.*paramiko.*')
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                port = 2222
                ip = i1
                username = self.ssh_username
                password = self.ssh_password
                sudo1 = "sudo "
                copy = 'scp -r '
                if ("::" or ":") in i1:
                    server_path = ' maglev@[2001:420:54ff:a4::509:199]:/var/www/html/RCA/maglev/' + self.folder_name
                else:
                    server_path = '  maglev@10.106.176.199:/var/www/html/RCA/maglev/' + self.folder_name
                copy_command = sudo1 + copy + i2 + server_path
                print(copy_command)
                commands_cpy = [copy_command]
                function = self.ssh_login(port, ip, username, password)
                print(function)
                if "Maglev Restricted Shell is active" in function:
                    print("yes")
                    commands1 = ['_shell']
                    for comand in commands1:
                        channel.send(comand)
                        channel.send("\n")
                        time.sleep(5)
                        output = channel.recv(9999).decode('utf-8')
                        print(output)
                        time.sleep(2)
                        if "Password:" in output:
                            time.sleep(0.1)
                            channel.send(self.maglev_password + "\n")
                            print("******")
                            time.sleep(2)
                        else:
                            time.sleep(2)
                        while not channel.recv_ready():
                            time.sleep(1)
                        output = channel.recv(9999).decode('utf-8')
                        print(output)
                        if "Password:" in output:
                            time.sleep(0.1)
                            channel.send(self.maglev_password + "\n")
                            print("******")
                            time.sleep(1)
                        else:
                            time.sleep(1)
                else:
                    print("no")
                for comand in commands_cpy:
                    channel.send(comand)
                    channel.send("\n")
                    print(commands_cpy)
                time.sleep(10)
                output = channel.recv(9999).decode('utf-8')
                print(output)
                time.sleep(5)
                if "password" in output:
                    time.sleep(0.1)
                    channel.send(self.maglev_password + "\n")
                    print("*****")
                    time.sleep(2)
                else:
                    time.sleep(2)
                while not channel.recv_ready():
                    time.sleep(1)
                output = channel.recv(9999).decode('utf-8')
                print(output)
                time.sleep(10)
                if "Are you sure you want to continue connecting (yes/no)?" in output:
                    time.sleep(2)
                    channel.send("yes" + "\n")
                time.sleep(10)
                if "password:" in output:
                    time.sleep(0.1)
                    channel.send(self.remote_server_password + "\n")
                    print("*****")
                    time.sleep(2)
                else:
                    time.sleep(2)
                time.sleep(10)
                output = channel.recv(9999).decode('utf-8')
                print(output)
                while output:
                    output = channel.recv(9999).decode('utf-8')
                    time.sleep(10)
                    print(output)
            except Exception as e:
                print("could not complete execution")
            finally:
                print("Copied to remote location: http://10.106.176.199/RCA/maglev/"+self.folder_name)

    def sending_file_to_server(self):
        print("##################################")
        string = 'Created RCA package:'
        obj1 = open(self.text_file, "r")
        re = obj1.read()
        x = re.split("\n")
        matching = [s for s in x if string in s]
        print(matching)
        output_list = []
        for i in matching:
            k = i.split("\r")[0]
            output_list.append(k)
        print(output_list)
        node1_tar_file = output_list[0][20:]
        if self.cluster_type == "yes":
            node2_tar_file = output_list[1][20:]
            node3_tar_file = output_list[2][20:]
            ips_list = [self.node1, self.node2, self.node3]
            tarfiles_list = [node1_tar_file, node2_tar_file, node3_tar_file]
            self.copy_function(ips_list, tarfiles_list)
        else:
            ips_list = [self.node1]
            tarfiles_list = [node1_tar_file]
            self.copy_function(ips_list, tarfiles_list)

    def creating_directory(self):
        dir_com = 'mkdir /var/www/html/RCA/maglev/' + self.folder_name
        commands = [dir_com]
        port = 22
        ip = self.remote_server_ip
        username = self.remote_server_username
        password = self.remote_server_password
        function = self.ssh_login(port, ip, username, password)
        print(function)
        for comand in commands:
            channel.send(comand)
            channel.send("\n")
        time.sleep(5)
        output = channel.recv(9999).decode('utf-8')
        # print(output)

    def ssh_rca_function(self, list):
        for i in list:
            try:
                commands = ['rca']
                port = 2222
                ip = i
                username = self.ssh_username
                password = self.ssh_password
                function = self.ssh_login(port, ip, username, password)
                print(function)
                for comand in commands:
                    channel.send(comand)
                    channel.send("\n")
                while not channel.recv_ready():
                    time.sleep(5)
                output = channel.recv(9999).decode('utf-8')
                print(output)
                print("*****")
                if "password" in output:
                    channel.send(self.maglev_password + "\n")
                    time.sleep(5)
                else:
                    time.sleep(5)
                while not channel.recv_ready():
                    time.sleep(0.1)
                time.sleep(5)
                output = channel.recv(9999).decode('utf-8')
                print(output)
                if "password" in output:
                    time.sleep(0.1)
                    channel.send(self.admnpwd + "\n")
                    output = channel.recv(9999).decode('utf-8')
                    print(output)
                print("*****")
                output = channel.recv(9999).decode('utf-8')
                print(output)
                time.sleep(5)
                while not channel.recv_ready():
                    time.sleep(1)
                time.sleep(5)
                output = channel.recv(9999).decode("utf-8")
                print(output)
                while output:
                    output_str = channel.recv(9999).decode("utf-8")
                    channel.send("\n")
                    out = output_str.strip("\n")
                    with open(self.text_file, "a+") as text_file:
                        if "Created RCA package:" in out:
                            text_file.write(out)
                        else:
                            time.sleep(0.1)
                    if self.variable in out:
                        break
                    else:
                        print(out)
                    print("####")
            except Exception as e:
                print("could not complete execution")

    def rca(self):
        if self.cluster_type == "yes":
            print("3 node cluster")
            list = [self.node1, self.node2, self.node3]
            self.ssh_rca_function(list)
        else:
            print("single node")
            list = [self.node1]
            self.ssh_rca_function(list)


object = ssh_connect()
object.creating_directory()
object.rca()
object.sending_file_to_server()
