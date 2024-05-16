from impacket.smbconnection import SMBConnection
from impacket.dcerpc.v5 import transport, scmr

def create_service_and_run(remote_host, username, password, domain, service_name, executable_path):
    # Establish SMB Connection using the same remote_host for simplicity
    conn = SMBConnection(remote_host, remote_host, sess_port=139)
    conn.login(username, password, domain=domain)

    # Set up the transport for the DCERPC session over SMB
    string_binding = r'ncacn_np:{}[\pipe\svcctl]'.format(remote_host)
    rpc_transport = transport.DCERPCTransportFactory(string_binding)
    rpc_transport.set_credentials(username, password, domain)

    dce = rpc_transport.get_dce_rpc()
    dce.connect()
    dce.bind(scmr.MSRPC_UUID_SCMR)

    # Open SCManager
    sc_manager_handle = scmr.hROpenSCManagerW(dce)['lpScHandle']
    
    # Create the service
    create_resp = scmr.hRCreateServiceW(dce, sc_manager_handle, service_name, service_name, lpBinaryPathName=executable_path)
    service_handle = create_resp['lpServiceHandle']
    
    # Start the service
    scmr.hRStartServiceW(dce, service_handle)

    # Properly close handles and disconnect
    scmr.hRCloseServiceHandle(dce, service_handle)
    scmr.hRCloseServiceHandle(dce, sc_manager_handle)
    dce.disconnect()

# Example usage
target_ip = '192.168.1.100'
username = 'admin'
password = 'password'
domain = 'DOMAIN'
service_name = 'MyRemoteService'
executable_path = r'C:\Windows\System32\notepad.exe'

create_service_and_run(target_ip, username, password, domain, service_name, executable_path)
