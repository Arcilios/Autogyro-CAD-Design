import serial
import time

ser = serial.Serial('COM17', 9600)  
time.sleep(2)

for speed in range(85, 96):  
    command = f"P{speed}T90\n"  
    ser.write(command.encode())
    print(f"Testing FS90R with P{speed}")
    time.sleep(2)

ser.write(b"P90T90\n")
print("Stop test")
ser.close()
