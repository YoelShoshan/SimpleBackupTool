import os
import subprocess
import easygui as eg
import Tkinter, tkFileDialog, tkMessageBox

root = Tkinter.Tk()

finished_choosing_source_dir = False
    
rootdir = ''
    
while (finished_choosing_source_dir == False):    
    rootdir = tkFileDialog.askdirectory(parent=root,initialdir=u"C:/",title=u'Please select backup SERVER directory')
    if '' == rootdir :
        print "No Base directory selected. Exiting."
        sys.exit(0)

    if len(rootdir ) < 5:
        #tkMessageBox.showwarning("Suspicious source path", "Warning - source path is %s" % test_server_dir)
        if tkMessageBox.askyesno("Question", type='yesno', icon='warning', \
            message="Warning: Are you sure you want to use %s as BASE directory?" %rootdir ):
            finished_choosing_source_dir = True
            break
        else:
            continue
        
    finished_choosing_source_dir = True


#rootdir = "C:/backup_server"

OPTION_GET_STATUS = "Get Status"
OPTION_RECOMPRESS_VIDEO_FILES = "Recompress video files (mp4,avi,mov)"
OPTION_ERASE_ORIGINAL_VIDEO_FILES = "Erase original for files that have _newencoding version"


msg     = "What would you like to do?"
choices = [OPTION_GET_STATUS,OPTION_RECOMPRESS_VIDEO_FILES,OPTION_ERASE_ORIGINAL_VIDEO_FILES]
#reply   = eg.buttonbox(msg,image='hard-drive-fire.jpg',choices=choices)
reply   = eg.buttonbox(msg,choices=choices)


ENCODING_POSTFIX = "_newencoding"
total_should_encode_size = 0
total_should_encode_files_num = 0
total_encoded_size = 0
total_encoded_files_num = 0
should_encode_map = {}
encoded_map = {}

#next steps:
#0. i gotta add some simple "progress bar", even to print x out of y files completed (z%)
#1. Show statistics on how many files have _NewEncoding version and compare sizes.
#2. Delete all files that i see that there is a _NewEncoding version of them (after checking there are no sound/visual problems)

print "Note: I do not support Unicode yet !!!"
print "I should look how i supported it in backup_tool.py and use the same method."

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
            file_func((current_sub_path+file).lower(),depth+1)
        else: # a dir
            walk_helper(nfile,current_sub_path+file+u"/",depth,dir_func,file_func)


def operate_on_dir_place_holder(rel_dir,depth):
    #print_tabs(depth)
    #out_msg_n ( rel_dir.encode('utf-8') )
    pass




def check_should_encode_file(full_path_file):
    if not (".mp4" in full_path_file or ".mov" in full_path_file or ".avi" in full_path_file):
        return False
    if ("error" in full_path_file or "Error" in full_path_file or "ERROR" in full_path_file):
        return False
    if ENCODING_POSTFIX in full_path_file:
        return False
    return True

def check_is_encoded_file(full_path_file):
    if not (".mp4" in full_path_file or ".mov" in full_path_file or ".avi" in full_path_file):
        return False
    if ENCODING_POSTFIX in full_path_file:
        return True
    return False

def get_file_size(file):
    return os.stat(file).st_size

def show_stats_file(file,depth):
    global total_should_encode_size
    global total_should_encode_files_num
    global should_encode_map
    global total_encoded_size
    global total_encoded_files_num
    global encoded_map
    
    if "?" in file:
        print "Ignoring [%s]" % file
        return
    
    lwr_file = file.lower()

    if "error" in lwr_file:
        print "Ignoring [%s]" % lwr_file
        return

    src_file = rootdir+'/'+file
    
    if check_should_encode_file(src_file):    
        total_should_encode_size += get_file_size(src_file)
        total_should_encode_files_num += 1
        should_encode_map[src_file.lower()] = 1        
    elif check_is_encoded_file(src_file):
        total_encoded_size += get_file_size(src_file)
        total_encoded_files_num += 1
        encoded_map[src_file.lower()]=1

def convert_to_encoded_name(full_path_name):
    p = full_path_name.rpartition('.')
    if len(p) != 3:
        print "Error! problem partitioning [%s]" % src_file
        print "Got %d partitions instead of the expected 3!" % len(p)
        return
    
    #debug
    #print lwr_file
    #return
    
    res = p[0]+ENCODING_POSTFIX+'.'+'mp4'
    return res

def convert_to_orig_name(full_path_name):
    if not ENCODING_POSTFIX in full_path_name:
        print "Error! [%s] not found in [%s]!" % (ENCODING_POSTFIX,full_path_name)
    res = full_path_name.replace(ENCODING_POSTFIX,"")
    return res

def recompress_file(file,depth):
    lwr_file = file.lower()
    if not (".mp4" in lwr_file or ".mov" in lwr_file or ".avi" in lwr_file):
    #if not (".mp4" in lwr_file):
        return

    if ("error" in lwr_file):
    #if not (".mp4" in lwr_file):
        return
    
    #print "Restore to mp4+mov+avi!!!!"
    
    if ENCODING_POSTFIX in file:
        return
    
    src_file = rootdir+'/'+file
    
    dst_file = convert_to_encoded_name(src_file)
    
    
    #print rootdir+'/'+file
    print "In:"+src_file+" Out:" + dst_file
    
    #"C:\Program Files (x86)\WinFF\ffmpeg.exe" -y -i "in.mp4" -crf 35.0 -vcodec libx264 -acodec libvo_aacenc -ar 48000 -b:a 128k -coder 1 -rc_lookahead 50 -threads 0 "out.mp4"
    exe_name = r"C:\Program Files (x86)\WinFF\ffmpeg.exe"
    
    #"Very High"    
    exec_str = exe_name+"  -y -i \""+src_file+"\" -crf 25.0 -vcodec libx264 -acodec libvo_aacenc -ar 48000 -b:a 160k -coder 1 -rc_lookahead 60 -threads 0 \""+dst_file+"\""
    
    #"High"
    #exec_str = exe_name+"  -y -i \""+src_file+"\" -crf 35.0 -vcodec libx264 -acodec libvo_aacenc -ar 48000 -b:a 128k -coder 1 -rc_lookahead 50 -threads 0 \""+dst_file+"\""
    
    print "Executing: " + exec_str

    subprocess.call(exec_str)
    
    before_size = get_file_size(src_file)
    after_size = get_file_size(dst_file)
    
    if after_size > before_size:
        print "ERROR!!!!! after encoding [%s] size is bigger than before encoding [%s] size !!!" % (src_file, dst_file)

    #perhaps delete the dst file now.

def create_new_encoding_files():
    walk(rootdir, operate_on_dir_place_holder, recompress_file)


    
def get_stats():
    walk(rootdir, operate_on_dir_place_holder, show_stats_file)
    print "Should Encode: (%d files) (%f bytes)" % (total_should_encode_files_num,float(total_should_encode_size)/(1024.0*1024.0))
    print "Already Encoded: (%d files) (%f bytes)" % (total_encoded_files_num,float(total_encoded_size)/(1024.0*1024.0))
    
    if (0==total_should_encode_size):
        print "No need to encode any file! quitting."
        return
    
    print "New encoding is %f%% of Prev encoding" % ((float(total_encoded_size) / float(total_should_encode_size))*100.0)
    
    should_encode_keys = should_encode_map.keys()
    encoded_keys = encoded_map.keys()
    
    print "------"
    for k in should_encode_keys:
        encoded_name = convert_to_encoded_name(k).lower()
        if not encoded_name in encoded_keys:
            print "[%s] found but no [%s] found!" % (k,encoded_name)
        else:
            should_encode_size = get_file_size(k)
            encoded_size = get_file_size(encoded_name)
            ratio = float(encoded_size) / float(should_encode_size)
            if ratio > 1.0:
                print "Error !!!!! encoded size for [%s] is bigger than before encoding [%s] !!! Ratio=%f" % (encoded_name,k,ratio)
    print "------"
    for k in encoded_keys:
        orig_name = convert_to_orig_name(k).lower()
        if not orig_name in should_encode_keys and not orig_name[:-4]+".avi" in should_encode_keys and not orig_name[:-4]+".mov" in should_encode_keys:
            print "[%s] found but no [%s] found!" % (k,orig_name)

def delete_orig(dry_run = True):
    should_encode_keys = should_encode_map.keys()
    encoded_keys = encoded_map.keys()
    
    if dry_run == True:
        print "Dry run !!! actual delete removed for safety."
    
    for k in encoded_keys:
        orig_name = convert_to_orig_name(k).lower()
        orig_name_fixed_ext = None
        if orig_name in should_encode_keys:
            orig_name_fixed_ext = orig_name
            
        if orig_name[:-4]+".avi" in should_encode_keys:
            orig_name_fixed_ext = orig_name[:-4]+".avi"
            
        if orig_name[:-4]+".mov" in should_encode_keys:
            orig_name_fixed_ext = orig_name[:-4]+".mov"
        
        if orig_name_fixed_ext!=None:        
            print "Found encoded=[%s] delete orig=[%s]" % (k,orig_name_fixed_ext)
            shell_cmd = "del \"%s\"" % orig_name_fixed_ext.replace("/","\\")
            print shell_cmd
            if dry_run == True:
                print "NOTE NOTE NOTE - Actual delete removed for safety!!!"
            else:
                os.system(shell_cmd)
                

#select what to do here:

#if reply == OPTION_GET_STATUS:
get_stats()
    
if reply == OPTION_RECOMPRESS_VIDEO_FILES:
    create_new_encoding_files()
    
if reply == OPTION_ERASE_ORIGINAL_VIDEO_FILES:
    delete_orig()
    msg     = "Now that you've seen the files that are about to be deleted, are you sure?"
    choices = ['Yes','No']
    reply   = eg.buttonbox(msg,image='hard-drive-fire.jpg',choices=choices)
    
    if reply == 'Yes':
        delete_orig(False)

"""count = 0

for root, subFolders, files in os.walk(rootdir):
    for file in files:
        lwr_file = file.lower()
        if ".mov" in lwr_file or ".mov" in lwr_file or ".avi" in lwr_file:
            print file
            p = file.rpartition('.')
            if len(p) != 3:
                print "Error! problem partitioning [%s]" % file
                print "Got %d partitions instead of the expected 3!" % len(p)
                continue
            src_file = file
            dst_file = p[0]+'_out'+'.'+'mp4'
            
            print "In:"+src_file+" Out:" + dst_file
            
            count+=1
            
print "Total %d files" % count
"""
            

print "Done!"