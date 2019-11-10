from telnetlib import Telnet
from multiprocessing import pool

Collected_Data = []
NodeCounter = 0

class NE_Adapter:
    def __init__(self, NodeIP, Commands):
        self.NodeIP = NodeIP
        self.Commands = Commands
        self.CommandsResult = {}
        self.tn = Telnet()
        self.log = []

        if self.Conn_Init() == True:
            for i in self.Commands:
                self.CommandsResult[i] = self.CMD_Exec(i)
            self.Conn_Terminator()
            self.CollectionStatus = True
        else:
            for i in self.Commands:
                self.CommandsResult[i] = self.NodeIP + ' is unreachable!'
            print(self.NodeIP + ' is unreachable!')
            try:
                self.Conn_Terminator()
            except:
                print(self.NodeIP + 'ConnectionTermination Exception!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1')

    def Conn_Init(self):
        try:
            self.tn.open(self.NodeIP,23,timeout=3)
            loginResult = self.tn.read_until(b'login:',5)
            if ('login:') not in loginResult:
                self.log.append(self.NodeIP+' - Login Failed!-1')
                return False
            self.tn.write(("cli\n").encode('ascii'))
            loginResult = self.tn.read_until(b'Password: ',5)
            if ('Password:') not in loginResult:
                self.log.append(self.NodeIP+' - Login Failed!-2')
                return False
            self.tn.write(("cli\n").encode('ascii'))
            loginResult = self.tn.read_until(b'Username: ',5)
            if ('Username:') not in loginResult:
                self.log.append(self.NodeIP+' - Login Failed!-3')
                return False
            self.tn.write(("admin1\n").encode('ascii'))
            loginResult = self.tn.read_until(b'Password: ',5)
            if ('Password:') not in loginResult:
                self.log.append(self.NodeIP+' - Login Failed!-4')
                return False
            self.tn.write(("Admin1%p55\n").encode('ascii'))
            passResult = self.tn.read_until(b'(Y/N)?',5)
            if ('Y/N') not in passResult:
                self.log.append(self.NodeIP+' - Login Failed!-5')
                return False
            self.tn.write(('y' + "\n").encode('ascii'))
            self.tn.read_until(b'#')
            self.tn.write(('paging status disabled' + "\n").encode('ascii'))
            self.tn.read_until(b'#')
            return True
        except:
            self.log.append('The issue is in Conn_Init block$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
            return False

    def CMD_Exec(self,cmd):
        try:
            if 'restore' in cmd:
                print('Executing DB Restore on '+str(self.NodeIP))
                self.tn.write((cmd + "\n").encode('ascii'))
                data = self.tn.read_until(b"#")
                if 'database restore complete' in data:
                    print(self.NodeIP +' is ***************** SUCCESSFULLY ********************* restored!')
                    self.log.append(self.NodeIP +' is ***************** SUCCESSFULLY ********************* restored!')
                else:
                    self.log.append((self.NodeIP+' FAILED to be restored!'))
                    print(self.NodeIP+' FAILED to be restored!')
            else:
                if 'ip' in cmd:
                    print('Setting DB Server IP on '+str(self.NodeIP)) 
                elif 'path' in cmd:
                    print('Setting DB file path on '+str(self.NodeIP))
                elif 'userid' in cmd:
                    print('Setting sftp credentials on '+str(self.NodeIP))
                self.tn.write((cmd + "\n").encode('ascii'))
                data = self.tn.read_until(b"#",5)
            return data.decode('utf-8')
        except TypeError:
            self.log.append('The issue is in CMD_Exec block $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')

    def Conn_Terminator(self):
        self.tn.write(('logout\n').encode('ascii'))
        self.tn.close()

def P_Executer(Node_Info):
    global NodeCounter
    NodeCounter += 1
    print(str(NodeCounter) + ") "+ Node_Info[0] +' Started...')
    NodeObject = NE_Adapter(Node_Info[0],Node_Info[1])
    print(str(NodeCounter) + ") "+ Node_Info[0] +' Finished!')
    if NodeObject == None:
        print('The issue is in P_Executer block $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    return NodeObject

def collect_result(res):
    global Collected_Data
    Collected_Data.append(res)

def multiRestore(phns):
    global NodeCounter
    NodeCounter = 0
    p = pool.Pool(20)
    for node in phns:
        commands = ['config database server ip 10.0.1.254',
                    'config database server userid otn\nlucent!123',
                    'config database path /home/otn/TSOL/PHN/BACKUPS/'+node,
                    'config database restore force\nyes']
        p.apply_async(P_Executer,args=([phns[node],commands],), callback=collect_result)
    p.close()
    p.join()


if __name__ == '__main__':
    source = {}
    counter = 1
    datafile = input('Full Data file name: ')
    with open(datafile) as netData:
        content = netData.read().splitlines()
    for i in content:
        tmp = i.split('^')
        source[tmp[0]] = tmp[1]
    multiRestore(source)
    try:
        if Collected_Data != []:
            with open('Output.log','w') as logfile:
                for items in Collected_Data:
                    for logs in items.log:
                        logfile.write(logs+'\n')
    except TypeError:
        print('The issue is in log export block $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    print("""
                            (o o)
                      --oOO--(_)--OOo--
                  All nodes are restored!""")

