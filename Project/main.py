import redis
import uuid
from datetime import datetime

r = redis.Redis(host="localhost", port=6379, db=0)

def increment_count(r, start_str):
    day_str = start_str + ":" + datetime.today().strftime('%Y-%m-%d')
    if r.exists(day_str):
        day_count = int(r.get(day_str)) + 1
        r.set(day_str, day_count)
    else:
        r.set(day_str, 1)

while (True):

    exp_time = 7 * 24 * 60 * 60

    print("Enter 1 for shortening a url")
    print("Enter 2 for decoding the shortened url")
    print("Enter 3 for Dashboard")
    ipt = input()
    if (ipt == "1"):
        og = "url:" + input("Enter long url")
        if r.exists(og):
            short = r.hget(og, "short")
            refs = r.hget(og, "refs") + 1
            refs = r.hmget(og, {"short": short, "refs": refs})
            print(short)
        else:
            short = uuid.uuid4().hex[:6].lower()
            r.hmset(og, {"short": short, "refs": 0})
            r.expire(og, exp_time)
            print(short)
            # Update day count
            increment_count(r, "new_day")
            

    elif (ipt == "2"):
        exs = r.keys("url:*")
        found = False
        for key in exs:
            current_short = r.hget(key, "short")
            if current_short == ipt:
                found = True
                print(key[4:])
                increment_count(r, "decode_day")
                break

        if not found:
            print("Key doesn't exist")

    else:
        

    
    pass