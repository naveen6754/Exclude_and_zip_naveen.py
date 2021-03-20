import os
import time
import logging
import fnmatch
import smtplib

import gzip
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from itertools import chain
from configparser import ConfigParser
tracker=0


'''
Description : function navigates the list of root directores specified in the property file "config.ini"
              to zip the files that are older than 7 days (which are not zip files already) ,except the 
              files and directories that have been specified in the "config.ini" file

Arguments   :  zip_the_file() function takes 3 arguments
              1. paths            - It takes path as a list variable , which holds set of path under 
                                    which, it is going to follow the zipping process based the policy 
                                    setup
              2. exclude_dir      - It takes list , which holds directories that need to be skipped
              3. exclude_list     - It takes list , which holds directories that need to be skipped
              
exit        : returns exit status as 0 if the process was successful zipping the files else,
              returns exit status as 1 if there was an error that was encountered during the process
'''

def zip_the_file(paths, exclude_dir, exclude_list):
    try:
        # collecting the current time and timestamp that need to be plugged on file
        now = time.time() 
        dt = time.strftime("%d-%m-%Y_%H%M%S") # current format date month year
        
        # looping through the root directories 
        for path_i in paths:
            path,days = path_i.split(':')
            for root, dirs, filenames in os.walk(path):
                for filename in filenames:
                    if root not in exclude_dir:
                       if not [pat for pat in exclude_list if fnmatch.fnmatch(filename, pat)]:
                                 file=os.path.join(root, filename)
                                 filetime = file+'.'+dt+'.gz'
                                 if not filename.endswith('.gz') and os.path.getmtime(file) < now - int(days) *86400:
                                        try:
                                        #print("file that is being zipped {} to {}".format(file,filetime))
                                        #os.system('gzip -c {} > {}'.format(file,filetime))
                                        #os.system('gzip < {} > {}'.format(file,filetime))
                                              input = open(file, 'rb')
                                              s = input.read()
                                              input.close()
                                              output = gzip.GzipFile(filetime, 'wb')
                                              output.write(s)
                                              output.close() 
                                        except Exception as gzip1:
                                              logging.exception('Zipping Failed file: {} \n'.format(file)) 
                                              continue
                                        if os.path.exists(filetime):
                                              logging.info("Successfully Zipped the file : {}".format(filetime))
                                              os.remove(file)
        return 0
    except Exception as e:
        logging.exception('Process stopped in Zip call: \n')
        return 1

'''
Description : function to send email to the desired group or person , when the execution of the script fails
'''
def send():
    from_add = config.get('email', 'from')
    to_add = config.get('email', 'to')
    cc_info = config.get('email', 'cc')
    email_srv= config.get('email','host')
    rcpt = cc_info.split(",") 
    msg = MIMEMultipart('alternative')
    part = MIMEBase('application', 'octet-stream')
    msg['Subject'] = "Zipping week old files"
    msg['From'] = from_add
    msg['To'] = to_add
    msg['cc'] = cc_info
    print("here")
    if tracker == 0:
               Zipf = 'There was an exception encountere during the process of zipping \n\t at machine time  :'+time.ctime(time.time())+'\n\t logs can be found '+os.getcwd().strip('bin')+'log/exclude_n_zip.log'
    elif tracker == 1: 
               Zipf = 'There were few files that failed to zip , please check the log file to track them  :'+time.ctime(time.time())+'\n\t logs can be found '+os.getcwd().strip('bin')+'log/exclude_n_zip.log'
    html = """\
            <HTML>
            <table bgcolor=#DCE1D7 height=600>
            <tr bgcolor=#000459 height=80 >
            <table><td align=center><h2>&nbspArchive week old files&nbsp</h2></td></table>
            </tr>
            <tr>
            <b>Zipping stopped with an error</b>
            </br>
            <pre>
            """ + Zipf + """
            </pre>
            </br>
            <b> DEVOPS </b>
            <tr bgcolor=#000459 height=50>
            </tr>
            </table>
            </HTML>
            """
    part2 = MIMEText(html, 'html')
    msg.attach(part)
    msg.attach(part2)
    s = smtplib.SMTP(email_srv)
    s.sendmail(from_add, rcpt, msg.as_string())
    s.quit()

'''
Description : main function ,that is hub to call the zip function with config file loaded and
              calls the send_email function in encounter of error/failure during the execution
'''

if __name__ == '__main__':
     
    try:
        # reading the excludes from config parser
        config = ConfigParser()
        config.read('./config.ini')
        log_path = config.get('log_path','log_file_path')
        paths_info = [x.strip() for x in config.get('root_paths', 'root_dirs').split(',')]
        exclude_dir_info = [x.strip() for x in config.get('excludes', 'exclude_dirs').split(',')]
        exclude_list_info = [x.strip() for x in config.get('excludes', 'exclude_file').split(',')]
        logging.basicConfig(filename=log_path, level=logging.INFO,
                    format='%(levelname)s:%(name)s:%(asctime)s:%(message)s')
        c_time=datetime.datetime.now()
        logging.info("\n\n\t\t::::::::::::::Zip Process for day {}::::::::::::::\n\n".format(c_time.strftime("%c")))
         
        # call to the zip function with config
        exit_info = zip_the_file(paths_info, exclude_dir_info, exclude_list_info) 
        if exit_info == 0 or tracker == 0: 
            pass
        else:
            print(sending)
            send()
    except KeyboardInterrupt:
            send()
            logging.exception('Keyboard Interrupt encountered \n')
    except Exception:
            send()
            logging.exception('Process Stopped due to following exception : \n')
