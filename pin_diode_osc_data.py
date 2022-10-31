from typing import IO, Counter
import json
import math

# read bin file: read the header and the data for each channel
if __name__ == '__main__':
    file_name = input("Write file name:")
    try:
        with open(file_name, "rb") as f:
            start = f.read(10) # reads first 10 bytes of the .bin file
            print(start)
            
            chID = bytes()
            count = 0
            while True:        # reads header and records it into chID
                s = f.read(1)
                chID += s
                if s == b'}':
                    count += 1
                    if count == 6:
                        break
                    
            #chID = f.read(729) # HEADER <-- todo parce and take dat
            
            header = json.loads(chID) # converts JSON header to Python obj
            print(header)
         
            data_to_read = header['SAMPLE']['DATALEN']*2 # extracts doubled value of DATALEN parameter
            print(data_to_read)

            CH1_EN = True
            CH2_EN = True
            if header['CHANNEL'][0]['DISPLAY'] != 'ON':
                CH1_EN = False
            if header['CHANNEL'][1]['DISPLAY'] != 'ON':
                CH2_EN = False

            print(CH1_EN,",",CH2_EN)

            if CH1_EN:
                noise1 = f.read(4) #start for ch1
                print(noise1) 
                data1 = f.read(data_to_read)
            if CH2_EN:
                noise2 = f.read(4) #start for ch2 ### reads 4 bytes after header
                print(noise2)
                data2 = f.read(data_to_read)

            data_ints_ch1 = []
            data_ints_ch2 = []

            for i in range(0, data_to_read,2):
                if CH1_EN:
                    data_ints_ch1.append(int.from_bytes(data1[i:i+2], "little", signed=True)) 
                if CH2_EN:
                    #data_ints_ch2.append(data2[i:i+2]) # reads the rest of the damp
                    data_ints_ch2.append(int.from_bytes(data2[i:i+2], "little", signed=True))
                
            #print(data_ints_ch2)

    except IOError:
        print("Error")
    
    # a function to find the negative peak of each signal
    def find_min(L1,L2):
        min_1 = min(L1)
        min_2 = min(L2)
        return min_1, min_2

    def convert(list):
        s = [str(i) for i in list]
        res = int("".join(s))
        return(res)

    # вытаскивает частоту семплирвания из хедера 
    SampleRate = header['SAMPLE']['SAMPLERATE']
    numbers = []

    for word in SampleRate:
        if word.isdigit():
            numbers.append(int(word))
            SampleRate = SampleRate.replace(word,"")

    S_r = convert(numbers)

    # converting the scale of sample rate to each correspondant integer value
    if 'k' in SampleRate:
        S_r *= 1000
    elif 'M' in SampleRate:
        S_r *= 1000000
    elif 'G' in SampleRate:
        S_r *= 1000000000
    print("Sample Rate is", S_r, "Samples per seconds")

    # extract the scale for Channel 1
    Scale1 = header['CHANNEL'][0]['SCALE']
    scales1 = []
    # separate integers from chars in channel 1 scale string
    for scl_1 in Scale1:
        if scl_1.isdigit():
            scales1.append(int(scl_1))
            Scale1 = Scale1.replace(scl_1,"")
        if scl_1 == '.':
            break;

    # obtain the integers from channel 1 scale string
    Y1_scale = convert(scales1)

    # converting the channel 1 scale to each correspondant integer value
    if 'm' in Scale1:
        Y1_scale *= 0.001
        
    print("Channel 1 scale: ", Y1_scale, "volts")

    # extract the scale for Channel 2
    Scale2 = header['CHANNEL'][1]['SCALE']
    scales2 = []
    # separate integers from chars in channel 2 scale string
    for scl_2 in Scale2:
        if scl_2.isdigit():
            scales2.append(int(scl_2))
            Scale2 = Scale2.replace(scl_2,"")
        if scl_2 == '.':
            break;

    # # obtain the integers from channel 2 scale string
    Y2_scale = convert(scales2)

    # converting the channel 2 scale to each correspondant integer value
    if 'm' in Scale2:
        Y2_scale *= 0.001

    print("Channel 2 scale: ", Y2_scale, "volts")


    # convert the ADC values to correspondant voltages values
    volts_ch1, volts_ch2 =[], []
    volts_ch1 = [i *(Y1_scale * 10)/(2**14)  for i in data_ints_ch1] # this oscilloscope has resolution of 14-bit
    volts_ch2 = [i *(Y2_scale * 10)/(2**14) for i in data_ints_ch2]

    def find_zeros(list_1):
        zero_1 = 0
        next_1 = list_1[0]
        for item_1 in list_1:
            if (next_1 > 0.0) and (item_1 < 0.0):
                zero_1 = list_1.index(next_1)
                break;
            else:
                next_1 = item_1
        return zero_1

    points_to_print = 300
    # plotting 300 points of each channnel


    Ch1_0 = find_zeros(volts_ch2[0:points_to_print])

    #extract the frequency from the header
    F = 30000
    #F = int(header['CHANNEL'][1]['FREQUENCE'])
    print("Frequency of the signal:", F, "Hertz")
    T = 1/F
    print("Period of the signal", T, "Seconds")

    points_to_measure = int(T*(S_r)+ Ch1_0) #T = 1/F 
    CH1 = []
    CH2 = []
    for item in volts_ch1[Ch1_0:points_to_measure]:
        CH1.append(item)
    for item in volts_ch2[Ch1_0:points_to_measure]:
        CH2.append(item)

    #Ch1_peak_neg, Ch2_peak_neg = find_min(CH1,CH2)
    Ch2_peak_neg = min(CH2)
    print(Ch2_peak_neg)

