import time

full = list(range(1, 55))

def rate_limited(array):
    count = 0
    chunks = array[count:count + 10]
    while chunks[-1] != array[-1]:
        print(array[count], array[count + 10])
        chunks = array[count:count + 10]
        print(chunks)
        count = count + 10
        time.sleep(1)
    print(chunks)

rate_limited(full)