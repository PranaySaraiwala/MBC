import paramiko
import base64


def decode(text):
    base64_bytes = text.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')
    return message



hostname = "DEWDFGLP01721.wdf.sap.corp"
username = decode("STM0OTIzMw==")
password = decode("SWNoX01hY29fMTIz")

commands = [

    "pwd",
    "id",
    "uname -a",
    "df -h"
    # "sudo su - cleouser",
    # "ps -ef | grep VLT",


#for proxy servers
#"ps -ef | grep VLP",
]

# initialize the SSH client
client = paramiko.SSHClient()
# add to known hosts
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    client.connect(hostname=hostname, username=username, password=password)
except:
    print("[!] Cannot connect to the SSH Server")
    exit()
#Now let's iterate over commands we just defined and execute them one by one:

# execute the commands
for command in commands:
    print("="*50, command, "="*50)
    stdin, stdout, stderr = client.exec_command(command)
    output=str(stdout.read().decode())
    print(output.count("\n"))


    err = stderr.read().decode()
    if err:
        print(err)
