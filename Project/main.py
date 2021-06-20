import redis
import uuid
from datetime import datetime
import matplotlib.pyplot as plt

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def increment_count(r, start_str):
    day_str = start_str + ":" + datetime.today().strftime('%Y-%m-%d-%H-%M')
    if r.exists(day_str):
        day_count = int(r.get(day_str)) + 1
        r.set(day_str, day_count)
    else:
        r.set(day_str, 1)


def extract_graph_data(r, day_str):
    days = sorted(r.keys(day_str + ":*"))
    days_values = [int(r.get(k)) for k in days]
    days = [d[len(day_str) + 1:] for d in days]
    return days, days_values


def plot_graph(days, days_values, title):
    fig = plt.gcf()
    fig.canvas.manager.set_window_title(title)
    x_range = list(range(len(days)))
    plt.bar(x_range, days_values)
    plt.xticks(x_range, days)
    plt.show()


new_day = "new_day"
decode_day = "decode_day"


def main():
    while (True):

        exp_time = 7 * 24 * 60 * 60

        print("Enter 1 for shortening a url")
        print("Enter 2 for decoding the shortened url")
        print("Enter 3 for Dashboard")
        print("Enter exit to exit")
        ipt = input()
        if ipt == "1":
            short = ""
            og = "url:" + input("Enter long url \n")
            if r.exists(og):
                short = r.hget(og, "short")
            else:
                short = uuid.uuid4().hex[:6].lower()
                r.hset(og, mapping={"short": short, "refs": 0})
                r.expire(og, exp_time)
                # Update day count
                increment_count(r, new_day)
            print(short)

        elif ipt == "2":
            shrt = input("Enter short url \n")
            exs = r.keys("url:*")
            found = False
            for key in exs:
                current_short = r.hget(key, "short")
                if current_short == shrt:
                    found = True
                    print(key[4:])
                    increment_count(r, decode_day)

                    refs = int(r.hget(key, "refs")) + 1
                    r.expire(key, exp_time)
                    r.hset(key, mapping={"short": shrt, "refs": refs})

                    break

            if not found:
                print("Key doesn't exist")

        elif ipt == "3":
            print("Enter 1 for graphs")
            print("Enter 2 for top 3 links")
            print("Enter 3 for all mappings")
            ipt_2 = input()
            if ipt_2 == "1":
                days_new, days_new_values = extract_graph_data(r, new_day)
                days_decode, days_decode_values = extract_graph_data(
                    r, decode_day)

                plot_graph(days_new, days_new_values,
                           "New shortened links/day")
                plot_graph(days_decode, days_decode_values,
                           "Decoded links/day")

            elif ipt_2 == "2":
                urls = r.keys("url:*")
                urls_redis = [{"site": k[4:]} | r.hgetall(k) for k in urls]
                urls_sorted = sorted(urls_redis, key=lambda k: k["refs"])[:3]
                print(urls_sorted)

            elif ipt_2 == "3":
                urls = r.keys("url:*")
                urls_redis = [{"site": k[4:], "ttl": r.ttl(
                    k)} | r.hgetall(k) for k in urls]
                print(urls_redis)
        else:
            return


if __name__ == "__main__":
    main()
