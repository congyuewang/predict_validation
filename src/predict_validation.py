import os
import sys
def parse_df(raw_text):
    df_dict = dict()
    mylist = [line.rstrip('\n') for line in raw_text]
    for line in mylist:
        s=line.split('|')
        if len(s)==3 and s[0].isdigit():
            timestamp, ticker, price = tuple(s)
            df_dict[(int(timestamp), ticker)] = round(float(price), 2)
    return df_dict

def parse_window(window_txt):
    slide=window_txt.readline().strip()
    win_range=int(slide[0])
    return int(win_range)

def join_df(actual_df, predicted_df):
    diff_df = dict()
    for key, predicted_price in predicted_df.items():
        actual_price = actual_df[key]
        timestamp, _ = key
        error = round(abs(actual_price - predicted_price), 2)
        current_sum, n = diff_df.get(timestamp, (0, 0))
        diff_df[timestamp] = (round(current_sum + error, 2), n + 1)
    #print(diff_df)
    return diff_df

def compute_window_avg_error(diff_df, window,output):
    avg_df = []
    rolling_sum = 0.0
    rolling_n = 0
    rolling_avg=0.0
    #check upper and lower bound
    lower=2**32
    upper=-2**32
    for key in diff_df:
        if key>upper:
            upper=key
        if key<lower:
            lower=key
    #print((lower,upper))
    # I'm assuming the input time always starts at 1 and is sequential
    for i in range(lower, lower + window):
        diff, n = diff_df.get(i, (0, 0))
        rolling_sum += diff
        rolling_n += n
        if rolling_n!=0: 
            rolling_avg = round(rolling_sum / rolling_n, 2)
    if rolling_n==0:
        avg_df.append("|".join([str(x) for x in (1, window, 'N/A')]))
    else:
        avg_df.append("|".join([str(x) for x in (1, window, rolling_avg)]))

    for i in range (lower, upper):
        beg = i
        end = (i + window)
        beg_diff, beg_n = diff_df.get(beg, (0, 0))
        #print((beg_diff,beg_n))
        if end > upper:
            break
        end_diff, end_n = diff_df.get(end, (0, 0))
        #print((end_diff,end_n))
        rolling_sum -= beg_diff
        rolling_sum += end_diff
        rolling_n -= beg_n
        rolling_n += end_n
        #print(rolling_n)
# check if stock during time series ever exits
        if rolling_n!=0: 
            rolling_avg = round(rolling_sum / rolling_n, 2)                                        
            avg_df.append("|".join(str(x) for x in [beg + 1, end, rolling_avg]))
        else:                                       
            avg_df.append("|".join(str(x) for x in [beg + 1, end, 'NA']))
    output.write("\n".join(avg_df))

def calculate():
    
      actual_txt=open(sys.argv[2],'r')
      predicted_txt=open(sys.argv[3],'r')
      window_txt=open(sys.argv[1],'r')
      output=open(sys.argv[4],'w')
      actual_df = parse_df(actual_txt)
      predicted_df = parse_df(predicted_txt)
      window = parse_window(window_txt)
        
      diff_df = join_df(actual_df, predicted_df)
      error_txt = compute_window_avg_error(diff_df, window,output)
      output.close()
      actual_txt.close()
      predicted_txt.close()
      window_txt.close()
if __name__ == '__main__':
      calculate()


            
            
            
