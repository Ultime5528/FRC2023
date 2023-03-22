import numpy as np
import timeit

color1 = np.array([255,255,0])
color2 = np.array([0,255,0])

def speedtest2(color1, color2, t):
    start = timeit.default_timer()
    x = np.add(np.multiply(1 - t, color1), np.multiply(t, color2))
    end = timeit.default_timer()
    print(end - start)
    return x.astype(int)

def speedtest(color1, color2, t):
    start = timeit.default_timer()
    x = ((1 - t) * color1 + t * color2).astype(int)
    end = timeit.default_timer()
    print(end - start)
    return x.astype(int)

print(speedtest(color1, color2, 0.5))
print(speedtest2(color1, color2, 0.5))
