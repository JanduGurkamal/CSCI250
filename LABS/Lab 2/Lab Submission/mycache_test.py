from mycache import MyCache

mc = MyCache(16, 256, 1024,
             2, 8, 32, 128)

adds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

total_time, hit_rate = mc.access(adds)
print("Total latency:", total_time)
print("L1 hit rate:", hit_rate)