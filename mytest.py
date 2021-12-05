import numpy as np

def main(bars):
    for i in bars:
        print(i)

        
if __name__ == "__main__":
    X = np.array([1,2,3,4]).reshape(1,4)
    Y = np.array([5,6,7,8]).reshape(1,4)
    all_bar_price_arr = np.concatenate((X, Y), axis=0)

    print(all_bar_price_arr)
