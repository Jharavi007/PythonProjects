import redis
from tinydb import TinyDB

def main():
    try:
        red = redis.Redis(host='localhost', port=6379, db=0)
        db = TinyDB('offlineDB.json')
        count_dict={}
        count_dict['SUCESS_MESSAGE_COUNT'] = int(red.get("success_count").decode("utf-8"))
        count_dict['BUFFER_MESSAGE_COUNT'] = len(db)
        print(count_dict)
    except:
        print("cannot determine count of messages")
        
if __name__=='__main__':
    main()