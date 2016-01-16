"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
" Last Updated: 07/22/2014
"
" All things authentication related.  
"
" Uses flask-security extension: https://pythonhosted.org/Flask-Security
"
"""

"""
" Copyright:    Loggly, Inc.
" Author:       Sandip Sinha
" Email:        ssinha@loggly.com
"
"""
from flask                import Blueprint, render_template, request, flash,redirect, json
from werkzeug             import secure_filename
from law                  import config
from flask import jsonify
import os




blueprint = Blueprint( 'flupld', __name__,
                        template_folder = 'templates',
                        static_folder   = 'static' )

readsize = 1024

@blueprint.route( '/', methods=['GET','POST'])
def upload():


# Get the name of the uploaded file
     file = request.files['filename']
     print 'file upload request received ', file    
#     # Check if the file is one of the allowed types/extensions
     if file :
#         # Make the filename safe, remove unsupported chars
         filename = secure_filename(file.filename)
#         # Move the file form the temporal folder to
#         # the upload folder we setup
         file.save(os.path.join(config.get('fileload', 'UPLOAD_FOLDER'),'temp',filename))
         file_status = [{'upldstatus':'complete','name':filename}]
         data = {'filename': filename, 'status':'complete' }
         resp = jsonify(data)
         resp.status_code = 200
         return resp
     else:
         data = {'filename': 'Bad files', 'status':'failure' }
         resp = jsonify(data)
         resp.status_code = 400
         return resp


@blueprint.route( '/combine/', methods=['GET','POST'])
def joinchunks():
    msg = request.form
    outfile = msg['filename']
    filesize = msg['filesize']
    tofile = os.path.join(config.get('fileload', 'UPLOAD_FOLDER'),outfile)
    fromdir = os.path.join(config.get('fileload', 'UPLOAD_FOLDER'),'temp')
    output = open(tofile, 'wb')
    parts  = os.listdir(fromdir)
    parts.sort(  )
    for filename in parts:
        filepath = os.path.join(fromdir, filename)
        fileobj  = open(filepath, 'rb')
        while 1:
            filebytes = fileobj.read(readsize)
            if not filebytes: break
            output.write(filebytes)
        fileobj.close()
    output.close()
    data = {'filename': outfile}
    if os.path.isfile(tofile) and os.stat(tofile).st_size == int(filesize):
        data['status'] = 'Success'
        for filename in parts:
            filepath = os.path.join(fromdir, filename)
            os.remove(filepath)
    else:
        data['status'] = 'Failed'
    resp = jsonify(data)
    resp.status_code = 200
    return resp


