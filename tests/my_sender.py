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

####Send function####
nrf.configure_crc(0x0c) # just setting all interrupts of irq as 0
nrf.set_prim_rx_0() #setting nrf n transmit mode
nrf.set_auto_retransmit_count(0x00) # seting retransmits as 0 as running in while loop 
nrf.set_address_width(0x03) #set address width as 5
nrf.set_Channel_frequency(0x64) #setting channel frequency as 100 
nrf_spi.read_nrf_reg("RF_CH")
nrf.set_data_rate_power(nrf.RF_250kbps,nrf.PW_MAX) # two argument data rate and power
tx_addr = struct.pack("<BBBBB", 0x31,0x53,0x4e,0x53,0x52)#seting the same adress as receiver
nrf.set_tx_addr(tx_addr)
to_send = [0x10,0x00,0x00,0x00,0x00,0x00]#reading tx address    
result = spi.xfer(to_send)[1:]
nrf_spi.flush_tx()#flush tx fifo
nrf_spi.write_nrf_reg("STATUS",0x10)# this disables max rt 
nrf_spi.read_nrf_reg("STATUS")
print(result)
nrf.set_power_up()
lat = 36.2222
lng = 72.6789
count = 1
payload =  struct.pack("<Bff",0x01,lat,lng) ## arbitrary lat and long values
while True:
    nrf.send_payload(payload) #sending payload 1 bytes
    nrf_spi.flush_tx()#flush tx fifo 
    nrf_spi.write_nrf_reg("STATUS",0x10)#reset max rt
    nrf_spi.read_nrf_reg("STATUS")
    print(f"count = {count}")
    count = count + 1
