import logging
logger = logging.getLogger(__name__)
from django.core.mail import send_mail
import os

def database_replace():
    print('cronjobs runs successfully ====>')
    f = open('/home/webiotspc/Documents/bhautik/github/admin/cronjob.txt','w')
    f.close()
    # db_file = 'db.sqlite3'

    # # Remove the existing SQLite database file
    # if os.path.exists(db_file):
    #     os.remove(db_file)

    # # Create a new SQLite database file (this will create an empty database)
    # open(db_file, 'a').close()
    
    
def print_hello():
    print("HELLO Good morning ==>")
    logger.info("CROn job was called")
    
    