from fabric import task, Connection, SerialGroup
import functools

target_group = SerialGroup('muxi@10.16.70.46',
                           'muxi@10.16.81.26',
                           'muxi@10.16.94.136',)

## Define a task to update the remote server's package index
@task
def update(c):
    with c.cd('/tmp'):
        c.run('sudo apt-get update')

## Define a task to upgrade the remote server's packages
@task
def upgrade(c):
    with c.cd('/tmp'):
        c.run('sudo apt-get upgrade -y')

## Define a task to install a package on the remote server
@task
def installpackage(c, packagename):
    with c.cd('/tmp'):
        c.run(f'sudo apt-get install -y {packagename}')

@task
def checkanddisableservice(c, servicename):
    result = c.run(f'systemctl is-active {servicename}', warn=True)
    if result.stdout.strip() == "active":
        c.run(f'sudo systemctl stop {servicename}', warn = True)
        c.run(f'sudo systemctl disable {servicename}', warn = True)
    else:
        print(f'{servicename} service is not running')

@task
def checkandstartservice(c, servicename):
    result = c.run(f'systemctl is-active {servicename}', warn=True)
    if result.stdout.strip() == "inactive":
        c.run(f'sudo systemctl enable {servicename}', warn = True)
        c.run(f'sudo systemctl start {servicename}', warn = True)
    else:
        print(f'{servicename} service is already running')

@task 
def turnoffntpservice(c):
    checkanddisableservice(c, "ntp")
    checkanddisableservice(c, "chronyd")
    checkanddisableservice(c, "systemd-timesyncd")

@task
def turnonntpservice(c):
    checkandstartservice(c, "ntp")
    checkandstartservice(c, "chronyd")
    checkandstartservice(c, "systemd-timesyncd")

def is_dir_exists(c, dir_path):
    cmd = '[ -d ' + dir_path + ' ] && echo ok'
    result = c.run(cmd)
    return result.stdout == 'ok'

def is_file_exists(c, file_path):
    cmd = '[ -f ' + file_path + ' ] && echo ok'
    result = c.run(cmd)
    return result.stdout == 'ok'

def check_has_dir(c, dir_path, transmit_if_not_exist=True):
    if not is_dir_exists(c, dir_path):
        if transmit_if_not_exist:
            c.run('sudo mkdir -p ' + dir_path)

def check_has_file(c, file_path, transmit_file_path=""):
    if not is_dir_exists(c, file_path):
        if not transmit_file_path == "":
            c.run('touch ' + file_path)
        else:
            print("transmit_file_path?")

service_dir_path = "/lib/systemd/system/"
config_dir_path = "/etc/"

@task
def setmasterptpservice(c):    
    # ptp service\config
    check_has_file(c, service_dir_path + "ptp4l.service", "./master_ptp4l.service")
    check_has_file(c, config_dir_path + "ptp4l-master.conf", "./ptp4l-master.conf")
    # phc2sys servic 
    check_has_file(c, service_dir_path + "phc2sys.service", "./master_phc2sys.service")
    c.run("sudo systemctl daemon-reload")
    checkandstartservice(c, "ptp4l")
    checkandstartservice(c, "phc2sys")


@task
def setslaveptpservice(c):
    # ptp service\config
    check_has_file(c, service_dir_path + "ptp4l.service", "./ptp4l.service")
    check_has_file(c, config_dir_path + "ptp4l-slave.conf", "./ptp4l-slave.conf")
    # phc2sys servic 
    check_has_file(c, service_dir_path + "phc2sys.service", "./phc2sys.service")
    c.run("sudo systemctl daemon-reload")
    checkandstartservice(c, "ptp4l")
    checkandstartservice(c, "phc2sys")


    

