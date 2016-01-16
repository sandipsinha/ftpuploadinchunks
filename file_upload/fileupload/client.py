__author__ = 'ssinha'
from fileupload import config
import requests
import os


class uploadfile:
    host = None
    authstr = None
    user = None
    passw = None
    service = None
    token = None
    version = None

    def __init__(self, host = config.get( 'fileload', 'host' ), authstr = config.get( 'fileload', 'token-ext'),
                                        user = config.get( 'fileload', 'user'), passw = config.get( 'fileload', 'passw'),
                                        service = config.get( 'fileload', 'service'), version = config.get( 'fileload', 'version')):
        self.host = host
        self.authstr = authstr
        self.user=user
        self.passw = passw
        self.service = service
        self.version = version


    def authenticate(self):
        authurl = self.host + self.authstr
        userstr = self.service + ':' + self.user
        headers = {'X-Storage-User': userstr, 'X-Storage-Pass': self.passw}
        r = requests.get(authurl, headers=headers)
        self.token = r.headers['X-Auth-Token']
        if r.status_code == 200:
            pass
        else:
             print "Token cannot be created"
             sys.exit(1)


    def execute(self, method, *args, **kargs):
        method_map={'create-container':self.create_container,
                    'upload-file':self.upload_file,
                    'delete-container': self.delete_container
                    }
        result = method_map[method](*args,**kargs)
        return result

    def create_container(self, containerName):
        self.authenticate()
        headers = {'X-Auth-Token':self.token}
        requestURL = self.host + self.version + '/' + self.service + '/' + containerName
        r = requests.put(requestURL, headers=headers)
        if r.status_code == 201:
            return True
        else:
            print "Folder cannot be created"
            return False



    def upload_file(self, containerName, fileName = None):
        check_file(fileName)
        self.authenticate()
        try:
            
            requestURL = self.host + self.version + '/' + self.service + '/' + containerName  
            #print 'The requestURL is', requestURL
            headers = {'X-Auth-Token':self.token}
            #files = {'file': (os.path.basename(fileName), open(fileName, 'rb'))}
            r = requests.put(requestURL, headers=headers, files = fileName)
            return True if r.status_code == 201 else False
        except Exception as e:
            print 'Error occured', e
            return False

    def delete_container(self, containerName):
        check_file(containerName)
        self.authenticate()
        try:
            requestURL = self.host + self.version + '/' + self.service + '/' + containerName  
            headers = {'X-Auth-Token':self.token}
            r = requests.delete(requestURL, headers=headers)
            return True if r.status_code == 204 else False
        except Exception as e:
            print 'Error occured. Folder could not be deleted', e
            return False
        
def check_file(fileName):
    if fileName is None:
        print 'No file name specified, exiting'
        return None

        
        
        

        
        
        
        





