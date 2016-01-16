# ftpuploadinchunks
### This is a application which can be customized to upload a big file to upload using chunking. 

It is a paramater driven application which can specify the number of threads, the size of the chunks etc. For a complete description of the different parameters just run python cloudupload.py -h at the command prompt. 

Steps to run 

1.Download the folder and all the files. 
2.Created a virtual environment
3.Install the modules from the requirements.txt. 
4.Change/update the file_upload/fileupload/conf/oracle.cloud.conf file. For the purpose of this porgam it was initially designed to connect with Oracle cloud. However with a little tweak, you can use it upload to any repository. 
5.AT the command prompt run python <file- to be uploaded> <upload folder>




