####importing base libraries####
import spidev
import OPi.GPIO as GPIO
from time import sleep
import struct

spi =spidev.SpiDev() ###establishing spi connection
spi.open(1, 0)

GPIO.setmode(GPIO.BOARD)###set ce pin as pin 22
GPIO.setup(22, GPIO.OUT)

####this class is used for defining register map of nrf24####
class reg_mapping:
    def __init__(self):#register map
	    self.registers = [
	        ("CONFIG",0x00),
	        ("EN_AA",0x01),
	        ("EN_RXADDR",0x02),
	        ("SETUP_AW",0x03),
	        ("SETUP_RETR",0x04),
	        ("RF_CH",0x05),
	        ("RF_SETUP",0x06),
	        ("STATUS",0x07),
	        ("OBSERVE_TX",0x08),
	        ("RPD",0x09),
	        ("RX_ADDR_P0",0x0A),
	        ("RX_ADDR_P1",0x0B),
	        ("RX_ADDR_P2",0x0C),
	        ("RX_ADDR_P3",0x0D),
	        ("RX_ADDR_P4",0x0E),
	        ("RX_ADDR_P5",0x0F),
	        ("TX_ADDR",0X10),
	        ("RX_PW_P0",0X11),
	        ("RX_PW_P1",0x12),
	        ("RX_PW_P2",0x13),
	        ("RX_PW_P3",0x14),
	        ("RX_PW_P4",0x15),
	        ("RX_PW_P5",0x16),
	        ("FIFO_STATUS",0x17),
	        ("DYNPD",0x1C),
	        ("FEATURE",0x1D)
	    ]

    def data(self,register_name):#register finding functionality
        for register in self.registers:
            if register[0] == register_name:
                #print(f"Register found: {register}")	
                return register
        return None
        
####this class implements spi functions defined in nrf datasheet####        
class SPI:
    def __init__(self,reg_map): #spi commands
        self.commands = [
            ("R_REGISTER",0x00),#
            ("W_REGISTER",0X20),#
            ("R_PX_PAYLOAD",0x61),#
            ("W_TX_PAYLOAD",0xA0),#
            ("FLUSH_TX",0xE1),#
            ("FLUSH_RX",0xE2),#
            ("REUSE_TX_PL",0xE3),
            ("R_RX_PL_WID",0x60),#
            ("W_ACK_PAYLOAD",0xA8),#                                                                        
            ("W_TX_PAYLOAD_NO_ACK",0xB0),#
            ("NOP",0xFF)#
        ]
        self.reg_map = reg_map    
      
    
    def NOP(self): #used to read status register
        to_send = [self.commands[10][1]]
        result = spi.xfer(to_send)
        print(f"Status Register = {result}")    
 
    def write_nrf_reg(self,reg_name,data): #used to write to nrf registers in reg map
        register = self.reg_map.data(reg_name) #check if the register even exists
        if register is None:
	        print(f"{reg_name} Register is not found while writing")
        else:
            print(f"{reg_name} Register found while writing")	
            reg_addr = register[1]
            to_send = [self.commands[1][1] | reg_addr ,data]    #writng the data t that register
            spi.xfer(to_send)

    def read_nrf_reg(self,reg_name): #used to read from nrf registers in reg map
        register = self.reg_map.data(reg_name)#check if the register even exists
        if register is None:
	        print(f" {reg_name} Register is not found while reading") 
        else:
            print(f"{reg_name} Register found while reading") 
            reg_addr = register[1]
            to_send = [self.commands[0][1] | reg_addr,0x00]  #reading the value of the register
            result = spi.xfer(to_send)[1]
            print(f"received result = : {result}")
            return result
            
    def flush_tx(self): #flushes tx // used after sending is done 
        to_send = [self.commands[4][1],0x00]
        spi.xfer(to_send)
        print(f"Flushed tx")    

    def flush_rx(self): #flushes rx // make space for incoming data
        to_send = [self.commands[5][1],0x00]
        spi.xfer(to_send)
        print(f"Flushed rx") 
        
    def read_rx_payload_width(self): #checks rx payload width                          
        to_send = [self.commands[7][1],0x00]
        result = spi.xfer(to_send)[1]
        print(f"rx payload width = : {result} bytes")
        return result
        
    def read_rx_payload(self): #reads rx fifo 
        to_send = [self.commands[2][1]]
        width = self.read_rx_payload_width()
        for i in range (width):
            to_send.append(0x00)
        result = spi.xfer(to_send)
        #print(f"rx payload = : {payload}")
        return result
        
    def write_ack_payload(self,pipe_no,data): #writes ack payload used in rx mode
        print(data)
        data = list(data)
        print(data)
        to_send = [self.commands[8][1]] + data
        spi.xfer(to_send)
        print(f"Ack Payload sent = {to_send}, length in bytes = {len(data)}")   
        
    def write_tx_payload(self,data): #write tx payload
        print(data)
        data = list(data)
        print(data)
        to_send = [self.commands[3][1]] + data
        spi.xfer(to_send)
        print(f"Payload sent = {to_send}, length in bytes = {len(data)}")        
    
    def write_tx_payload_no_ack(self,data): #writes tx payload does not expect ack
        print(data)
        data = list(data)
        print(data)
        to_send = [self.commands[9][1]] + data
        spi.xfer(to_send)
        print(f"Payload sent = {to_send}, length in bytes = {len(data)}")   
       
    #I will always be using pin 22 as ce pin    
    def set_ce(self):
        GPIO.output(22, GPIO.HIGH) 
	
    def unset_ce(self):
        GPIO.output(22, GPIO.LOW)
    		
    
        
class NRF: 
    def __init__(self,spi):
        self.spi = spi  
        self.PW_MIN = (0b00 << 1)
        self.PW_LOW = (0b01 << 1)
        self.PW_HIGH = (0b10 << 1)
        self.PW_MAX = (0b11 << 1)
        self.RF_250kbps = (0b100 << 3)    
        self.RF_1Mbps = (0b000 << 3)     
        self.RF_2Mbps = (0b001 << 3)  
  
    def configure_crc(self,value):
        self.spi.write_nrf_reg("CONFIG",value)#keep bit 1 to low as it is nrf power up bit
               
    def set_prim_rx_0(self):# if r_t is high transmit mode otherwise in receive mode #will later include functionality of rx mode
        config = self.spi.read_nrf_reg("CONFIG")
        config &= 0xfe #setting up the prim rx bit to 0 for transmission
        self.spi.write_nrf_reg("CONFIG",config)    
     
    def set_prim_rx_1(self):# if r_t is high transmit mode otherwise in receive mode #will later include functionality of rx mode
        config = self.spi.read_nrf_reg("CONFIG")
        config |= 0x01 #setting up the prim rx bit to 1 for recieve mode
        self.spi.write_nrf_reg("CONFIG",config)                         
                 
    def set_auto_retransmit_count(self,count):     
        self.spi.write_nrf_reg("SETUP_RETR",count) # this count bit 7:4 define time delay between each transmit and 3:0 define number of retries       
    
    def set_address_width(self,width):
        self.spi.write_nrf_reg("SETUP_AW",width)# bit 7:2 should be 0 only bit 1:0 define width "00' is illegal       
        print(width) 
   
    def set_tx_addr(self,data):
        data = struct.unpack("<BBBBB",data)
        to_send = [0x20|0x10]+[int(value) for value in data]
        spi.xfer(to_send)
        #self.spi.write_nrf_reg("TX_ADDR",value)#keep bit 1 to low as it is nrf power up bit
        
    def set_rx_addr(self,pipe_no,data):
        data = struct.unpack("<BBBBB",data)
        if pipe_no == 0:
            to_send = [0x20|0x0A]+[int(value) for value in data]
            spi.xfer(to_send)	
            to_send = [0x0A,0x00,0x00,0x00,0x00,0x00]#reading x address    
            result = spi.xfer(to_send)[1:]
            print(f"writte addr to pipe 0 = {result}")
        elif pipe_no == 1:
            to_send = [0x20|0x0B]+[int(value) for value in data]
            spi.xfer(to_send)	
            to_send = [0x0B,0x00,0x00,0x00,0x00,0x00]#reading x address    
            result = spi.xfer(to_send)[1:]
            print(f"writte addr to pipe 1 = {result}")
        elif pipe_no == 2:
            to_send = [0x20|0x0C]+[int(value) for value in data]
            spi.xfer(to_send)	
            to_send = [0x0C,0x00,0x00,0x00,0x00,0x00]#reading x address    
            result = spi.xfer(to_send)[1:]
            print(f"writte addr to pipe 0 = {result}" )
        elif pipe_no == 3:
            to_send = [0x20|0x0D]+[int(value) for value in data]
            spi.xfer(to_send)	
            to_send = [0x0D,0x00,0x00,0x00,0x00,0x00]#reading x address    
            result = spi.xfer(to_send)[1:]
            print(f"writte addr to pipe 0 = {result}")
        elif pipe_no == 4:
            to_send = [0x20|0x0E]+[int(value) for value in data]
            spi.xfer(to_send)	
            to_send = [0x0E,0x00,0x00,0x00,0x00,0x00]#reading x address    
            result = spi.xfer(to_send)[1:]
            print(f"writte addr to pipe 0 = {result}")
        elif pipe_no == 5:
            to_send = [0x20|0x0F]+[int(value) for value in data]
            spi.xfer(to_send)	
            to_send = [0x0F,0x00,0x00,0x00,0x00,0x00]#reading x address    
            result = spi.xfer(to_send)[1:]
            print(f"writte addr to pipe 0 = {result}" )                                                            
        else :
            print("pipe does not exist")
        
    def en_rx_data_pipe(self,pipe_no):#enbling the specific pipe
        pipe = self.spi.read_nrf_reg("EN_RXADDR")
        pipe |= (1 << pipe_no)
        self.spi.write_nrf_reg("EN_RXADDR",pipe)
        self.spi.read_nrf_reg("EN_RXADDR")
        
    def set_rx_pw(self,pipe_no,width): 
        if pipe_no == 0: 
            self.spi.write_nrf_reg("RX_PW_P0",width)
            self.spi.read_nrf_reg("RX_PW_P0")
        elif pipe_no == 1:
            self.spi.write_nrf_reg("RX_PW_P1",width)
            self.spi.read_nrf_reg("RX_PW_P1")
        elif pipe_no == 2: 
            self.spi.write_nrf_reg("RX_PW_P2",width)
            self.spi.read_nrf_reg("RX_PW_P2")
        elif pipe_no == 3:	 
            self.spi.write_nrf_reg("RX_PW_P3",width)			
            self.spi.read_nrf_reg("RX_PW_P3")
        elif pipe_no == 4: 
            self.spi.write_nrf_reg("RX_PW_P4",width)
            self.spi.read_nrf_reg("RX_PW_P4")
        elif pipe_no == 5:	                       
            self.spi.write_nrf_reg("RX_PW_P5",width)                                     
            self.spi.read_nrf_reg("RX_PW_P5")
        else :
            print("pipe does not exist")  
            
    def payload_available(self,pipe_no):         
        status = self.spi.read_nrf_reg("STATUS")
        if (status & 14) == 0b1110:
            print("rx fifo empty") 
        elif pipe_no == 0: 
            status &= (1 << pipe_no)
            if status != 0:
                return 1
            else:
                return 0     
        elif pipe_no == 1:
            status &= (1 << pipe_no)
            if status != 0:
                return 1
            else:
                return 0   
        elif pipe_no == 2: 
            status &= (1 << pipe_no)
            if status != 0:
                return 1
            else:
                return 0   
        elif pipe_no == 3:	 
            status &= (1 << pipe_no)
            if status != 0:
                return 1
            else:
                return 0  	
        elif pipe_no == 4: 
            status &= (1 << pipe_no)
            if status != 0:
                return 1
            else:
                return 0   
        elif pipe_no == 5:	                       
            status &= (1 << pipe_no)
            if status != 0:
                return 1
            else:
                return 0                                      
        else :
            print("pipe does not exist")  
                      
    def set_Channel_frequency(self,frequency_channel):
        self.spi.write_nrf_reg("RF_CH",frequency_channel) #bit 7 is always 0    
    
    def set_data_rate_power(self,rate,power):
        rf_set1 = self.spi.read_nrf_reg("RF_SETUP")
        rf_set = rf_set1 & rate
        rf_set &= power
        rf_set |= rf_set1        
        self.spi.write_nrf_reg("RF_SETUP",rf_set)
    
    def set_power_up(self):
        config = self.spi.read_nrf_reg("CONFIG")
        config |= (1 << 1) #setting up the power up bit
        self.spi.write_nrf_reg("CONFIG",config)  
        self.spi.read_nrf_reg("CONFIG")
   
    def send_payload(self,payload):
        self.spi.write_tx_payload(payload)
        self.spi.set_ce()##pulsing ce pin
        sleep(0.2)
        self.spi.unset_ce() 
        #sleep(1)
        #GPIO.setup(22, GPIO.LOW)
        print(f"Payload sent")    
        
    def da_aa(self,pipe_no): #using this to disable auto acknowldgement on addressed data pipe
        pipe = self.spi.read_nrf_reg("EN_AA")
        temp = ~(pipe & (1 << pipe_no))
        #pipe &= temp 
        self.spi.write_nrf_reg("EN_AA",pipe)
        self.spi.read_nrf_reg("EN_AA")
        #print(self.spi.read_nrf_reg("EN_AA"))         
		           
