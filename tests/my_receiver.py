####importing base libraries####
import spidev
import OPi.GPIO as GPIO
from time import sleep
import struct
from nrf_op import *

spi =spidev.SpiDev() ###establishing spi connection
spi.open(1, 0)

GPIO.setmode(GPIO.BOARD)###set ce pin as pin 22
GPIO.setup(22, GPIO.OUT)

####initializing classes####
reg_map = reg_mapping() 
nrf_spi = SPI(reg_map)
nrf = NRF(nrf_spi)

####Receive function####
nrf_spi.unset_ce()
nrf.configure_crc(0x0c) # just setting all interrupts of irq as 0
nrf.set_prim_rx_1() #setting nrf n receive mode #check
nrf.set_power_up()
nrf.da_aa(1)#check
nrf.set_address_width(0x03)
addr = struct.pack("<BBBBB",0x31,0x53,0x4e,0x53,0x52)
nrf.set_rx_addr(1,addr)#check
nrf.set_Channel_frequency(0x64)
nrf_spi.read_nrf_reg("RF_CH")
nrf.set_data_rate_power(nrf.RF_250kbps,PW_MAX)# takes two arguments data_rate and power 
nrf.set_rx_pw(1,9)#check
nrf_spi.flush_tx()#flush tx fifo
nrf.en_rx_data_pipe(1)#check
sleep(1)
nrf_spi.set_ce()
count = 1
while 1 :
    if (nrf.payload_available(1)):
        print(f"count = {count}")
        result = nrf_spi.read_rx_payload()[1:]
        print(result)
        payload = struct.unpack("<Bff",bytes(result))
        print(f"lat = {payload[1]}, lng = {payload[2]}")
        nrf_spi.flush_rx()
        nrf_spi.write_nrf_reg("STATUS",0x70)
        count = count + 1
    sleep(1)    

