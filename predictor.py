#TODO : Predict throughput from

def init():
    global last_throughput
    global alpha
    alpha = 0.1
    last_throughput = 0.1
    
def predict_throughput(throughput):
    global last_throughput
    global alpha
    last_throughput = throughput * alpha + last_throughput * (1-alpha)
    return last_throughput

def add_half():
    global last_throughput
    last_throughput = last_throughput*1.5

def dec_half():
    global last_throughput
    last_throughput = last_throughput*0.5
