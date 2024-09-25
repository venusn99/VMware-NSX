import requests
import getpass
# requests.get(url, params={key: value}, args)
nsx_manager_ip= ''
password= getpass.getpass(f"Enter the password for NSX Manager{nsx_manager_ip}")
r = requests.get(url=https://{nsx_manager_ip}/)