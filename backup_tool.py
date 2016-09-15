#!/usr/bin/env python
import os
import shutil
import hashlib
import Tkinter, tkFileDialog, tkMessageBox
import sys
import datetime

root = Tkinter.Tk()

def out_tab():
    print "\t"
    log_file.write("  ")

def out_msg(text):
    print text,
    log_file.write(text)
    
def out_msg_n(text):
    print text
    log_file.write(text)
    log_file.write(u"<br>\r\n")
    

test_server_dir = ""
test_client_dir = ""

if len(sys.argv) == 1: #no args were passed    
    #ask the user for requested server/client folders
    
    finished_choosing_source_dir = False
    
    while (finished_choosing_source_dir == False):    
        test_server_dir = tkFileDialog.askdirectory(parent=root,initialdir=u"C:/",title=u'Please select backup SERVER directory')
        if '' == test_server_dir:
            print "No server directory selected. Exiting."
            sys.exit(0)
    
        if len(test_server_dir) < 5:
            #tkMessageBox.showwarning("Suspicious source path", "Warning - source path is %s" % test_server_dir)
            if tkMessageBox.askyesno("Question", type='yesno', icon='warning', \
                message="Warning: Are you sure you want to use %s as SERVER directory?" %test_server_dir):
                finished_choosing_source_dir = True
                break
            else:
                continue
            
        finished_choosing_source_dir = True
    
    finished_choosing_dest_dir = False
    
    while (finished_choosing_dest_dir == False):    
        test_client_dir = tkFileDialog.askdirectory(parent=root,initialdir=u"C:/",title=u'Please select backup CLIENT')
        
        if '' == test_client_dir:
            print "No client directory selected. Exiting."
            sys.exit(0)
    
        if len(test_client_dir) < 5:
            #tkMessageBox.showwarning("Suspicious source path", "Warning - source path is %s" % test_server_dir)
            if tkMessageBox.askyesno("Question", type='yesno', icon='warning', \
                message="Warning: Are you sure you want to use %s as CLIENT directory?" %test_client_dir):
                finished_choosing_dest_dir = True
                break
            else:
                continue
            
        finished_choosing_dest_dir = True
elif len(sys.argv) == 3:
    test_server_dir = sys.argv[1]
    test_client_dir = sys.argv[2]
else:
    out_msg_n("Error! Expecting either 2 args (server dir, client dir), or no dirs for user directories selection!")
    out_msg_n("Exiting.")
    sys.exit(1)    

now = datetime.datetime.now()

uni_time = str(now).replace(":","_").encode("utf-8")

file_name = test_client_dir+u"/backup_log"+uni_time+".html"

log_file = open(file_name,u'wt')

log_file.write(u"<head>\r\n")
log_file.write(u"<meta http-equiv=""Content-Type"" content=""text/html; charset=utf-8"">\r\n")

out_msg_n("Operation started!")
out_msg_n("Server: [%s]" % test_server_dir)
out_msg_n("Client: [%s]" % test_client_dir)

#test_server_dir = u'C:/My Projects/Coding/test_backup_server'
#test_client_dir = u'C:/My Projects/Coding/test_backup_client'

#files that actualy exist on the client
dest_files_hashes_dict = {}

def get_file_md5(file_name, block_size=2**20):    
    f = open(file_name,u'rb')    
    
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    #return md5.digest()
    return md5.hexdigest()

def print_tabs(num):
    for i in xrange(num):
        out_msg("\t")

#check all client files first and build md5 map

def operate_on_file(rel_file,depth):
    print_tabs(depth)
    #print rel_file.encode("utf-8"),    
    abs_file_src = test_server_dir+u"/"+rel_file    
    print_tabs(depth)
    out_msg( (u"file: "+abs_file_src).encode("utf-8") )
    #si = os.stat(u'\\?\\UNC\\'+abs_file_src)
    si = os.stat(abs_file_src)
    out_msg(u" %u bytes " % si.st_size)
    
    abs_file_dest = test_client_dir+u"/"+rel_file
    
    src_file_md5 = get_file_md5(abs_file_src)
          
    out_msg("md5=[%s]" % src_file_md5)
    
    dest_exists = os.path.isfile(abs_file_dest)

    identical = False

    if (True == dest_exists):
        out_msg("Exists ")
        dest_file_md5 = get_file_md5(abs_file_dest)
        if (dest_file_md5 == src_file_md5):
            identical = True
            out_msg_n("Identical! Not copying.")
            return
    
    if (dest_files_hashes_dict.has_key(src_file_md5)):
        #client already has this file, no need to re-copy
        already_found_at = dest_files_hashes_dict[src_file_md5]
        out_msg( u"already found at :")
        out_msg_n( already_found_at.encode('utf-8'))
        out_file = open(abs_file_dest+u".link.txt",u'wt')
        out_file.write(u"Identical file found at ".encode('utf-8')+already_found_at.encode('utf-8'))
        out_file.close()
        return
    
    if (False == identical):
        #check if the client doesn't already have this file somewhere else
        
        #copy to client dir            
        shutil.copy(abs_file_src, abs_file_dest)
        out_msg_n(u"copied. ")
        dest_files_hashes_dict[src_file_md5] = abs_file_dest   
    
def operate_on_dir(rel_dir,depth):
    print_tabs(depth)
    #print (u"dir: [" + dir +u"]").encode("utf-8")
    abs_file_src = test_server_dir+u"/"+rel_dir    
    print_tabs(depth)
    out_msg( (u"source dir: "+abs_file_src).encode("utf-8"))

    abs_dir_dest = test_client_dir+u"/"+rel_dir    

    if not os.path.exists(abs_dir_dest):
        os.makedirs(abs_dir_dest)
   

def walk(dir,dir_func,file_func):
    walk_helper(dir,u"",-1,dir_func,file_func)

# dir_func(rel_dir,depth)
# file_func(rel_dir,depth)
def walk_helper(dir,current_sub_path,depth,dir_func,file_func):
    depth += 1
    dir_func(current_sub_path,depth)
    dir = os.path.abspath(dir)
    #for file in [file for file in os.listdir(dir) if not file in [".",".."]]:
    files = os.listdir(dir)
    for file in files:
        if file in ['.','..']:
            continue
        nfile = os.path.join(dir,file)
        if not os.path.isdir(nfile):
            try:
                file_func(current_sub_path+file.decode("cp1255"),depth+1)
            except UnicodeDecodeError, e:
                print "Error: ",
                print e
            #file_func(current_sub_path+file,depth+1)

        else: # a dir
            try:
                walk_helper(nfile,current_sub_path+file.decode("cp1255")+u"/",depth,dir_func,file_func)
            except UnicodeDecodeError, e:
                print "Error: ",
                print e
            #walk_helper(nfile,current_sub_path+file+u"/",depth,dir_func,file_func)



def operate_on_dir_place_holder(rel_dir,depth):
    print_tabs(depth)
    out_msg_n ( rel_dir.encode('utf-8') )

def add_file_to_dest_hash(rel_file,depth):
    abs_file_client = test_client_dir+u"/"+rel_file
    client_file_md5 = get_file_md5(abs_file_client)
    dest_files_hashes_dict[client_file_md5] = abs_file_client
    

def UpdateClient():    
    out_msg_n(u"***************************")
    out_msg_n(u"Scanning client first...")
    out_msg_n(u"***************************")
    out_msg_n("")
    
    walk(test_client_dir, operate_on_dir_place_holder, add_file_to_dest_hash)
    
    out_msg_n(u"***************************")
    out_msg_n(u"Updating client data...")
    out_msg_n(u"***************************")
    out_msg_n("")
    
    walk(test_server_dir, operate_on_dir, operate_on_file)
    
    out_msg_n(u"***************************")
    out_msg_n(u"Done! :)")
    out_msg_n(u"***************************")
    
    
UpdateClient()

log_file.write(u"</head>\r\n")