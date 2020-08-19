import paramiko

hostname = "DEWDFGLP01721.wdf.sap.corp"
username = "I349233"
pwd=
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
