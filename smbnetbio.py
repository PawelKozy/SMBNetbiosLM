from impacket.smbconnection import SMBConnection
from impacket.dcerpc.v5 import srvs, scmr

def create_service_and_run(conn, service_name, executable_path):
    rpc_transport = scmr.DCERPCTransportFactory(r'ncacn_np:%s[\pipe\svcctl]' % conn.getRemoteHost())
    rpc_transport.set_dport(139)
    rpc_transport.setRemoteName(conn.getRemoteName())
    rpc_transport.set_credentials(conn._username, conn._password, conn._domain, conn._lmhash, conn._nthash)
    
    dce = rpc_transport.get_dce_rpc()
    dce.connect()
    dce.bind(scmr.MSRPC_UUID_SCMR)
    
    # Open SCManager
    resp = scmr.hROpenSCManagerW(dce)
    sc_manager_handle = resp['lpScHandle']
    
    # Create the service
    resp = scmr.hRCreateServiceW(dce, sc_manager_handle, service_name+'\x00', service_name+'\x00', lpBinaryPathName=executable_path+'\x00')
    service_handle = resp['lpServiceHandle']
    
    # Start the service
    scmr.hRStartServiceW(dce, service_handle)
    
    # Properly close handles and disconnect
    scmr.hRCloseServiceHandle(dce, service_handle)
    scmr.hRCloseServiceHandle(dce, sc_manager_handle)
    dce.disconnect()

# Connection info
target_ip = '192.168.1.100'
username = 'admin'
password = 'password'
domain = 'DOMAIN'

# Connection setup
conn = SMBConnection(target_ip, target_ip, sess_port=139)
conn.login(username, password, domain=domain)

# Create and start service
create_service_and_run(conn, 'MyRemoteService', r'C:\Windows\System32\notepad.exe')
