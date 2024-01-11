import socket
import time
import struct
import random
import sys


def server_simple_FTP_GBN():
    """This is the server side implementation of the SFTP project.
    
    Once the client initiates a connection the program will receive data using Go-back-N sliding window protocol.
    
    Authored by: Nikhil Khatu
    CSC 573 Professor: Harfoush
    """
    pass

def sum(data):
    csum = 0
    
    for i in range(0,len(data),2):
        if i + 1 >= len(data): csum += ord(data[i]) & 0xFF
        else: csum = csum + (((ord(data[i]) << 8) & 0xFF00) + (ord(data[i+1]) & 0xFF))

    while (csum >> 16) > 0:
        csum = (csum & 0xFFFF) + (csum >> 16)

    return (~csum) & 0xFFFF




def main():
    
    #user defined values
    serverPort = int(sys.argv[1])		#7735
    filename = sys.argv[2]				#"./rfc2131.txt"
    prob_of_packet_loss = float(sys.argv[3])	#.35 -- 0 < p < 1
    # please check this line. it might require the value to be type casted to
    #something else like int, since the input taken by argv is a string
    #(eg - check the handling at next field for port number)
    MSS = int(sys.argv[4])                           #1000	
    
    
    
    # Open socket object
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.bind(('', serverPort))
    
    file_object = open(filename, "wb")
    print "The server is ready to receive"
    
    #values of padding in ACK
    all_zeros = 0
    ACK_indicator = 43690
    
    #Send ACK once size of file is received
    file_size = 0
    size_received = False
    while size_received == False:
        size_packet, (clientName, clientPort) = serverSocket.recvfrom(8)
        size, checksum, indicator = struct.unpack('IHH', size_packet)
        if (checksum == sum(unicode(size))) and (indicator == 21845):
            size_received = True
            file_size = size
            pack_ACK = struct.pack('?HH', size_received, all_zeros, ACK_indicator)
            serverSocket.sendto(pack_ACK, (clientName, clientPort))
    print 'Receive file size (in bytes): ', file_size
    start_time = time.time()
        
    #Enter loop to receive data   
    recv_size = 0
    while recv_size < file_size:
        # Read from buffer according to the size of the packet expected
        last_data_size = file_size - recv_size
        if last_data_size < MSS:
            PACKETDATA = serverSocket.recv(8 + last_data_size)
            try: seq_num, checksum, indicator, data = struct.unpack('IHH%ds' % (last_data_size, ), PACKETDATA)
            except struct.error: continue
        else:
            PACKETDATA = serverSocket.recv(8 + MSS)
            
            try: seq_num, checksum, indicator, data = struct.unpack('IHH%ds' %(MSS), PACKETDATA)
            except struct.error : continue  
        #Probability Loss Service
        #Generate random number [0,1), then determine if packet is dropped
        r = random.random()
        if r <= prob_of_packet_loss:
            print 'Packet loss, sequence number = ', seq_num
            continue
        # verify packet with checksum, type 0101010101010101, and sequence
        if sum(data) != checksum: print "Bad Checksum!"
        elif indicator != 21845: print "Wrong Type!"
        elif recv_size < seq_num:
            pack_ACK = struct.pack('IHH', recv_size, all_zeros, ACK_indicator)
            serverSocket.sendto(pack_ACK, (clientName, clientPort))
            #print 'Received:', seq_num, 'ACK RE-sent. Expecting seq#: ', recv_size, ' next to: ', clientName,':', clientPort, '.'
        elif recv_size == seq_num:
            file_object.write(data)
            #print 'Received seq#: ', seq_num 
            #adjust the 'received_size' according to amount received
            if last_data_size < MSS:
                recv_size += last_data_size
                pack_ACK = struct.pack('IHH', recv_size, all_zeros, ACK_indicator)
                serverSocket.sendto(pack_ACK, (clientName, clientPort))
                end_time = time.time()
                print 'File', filename, 'of ', recv_size, ' bytes has been received.', ' MSS = ', MSS
                print 'Time to receive ', filename, 'with ', recv_size, 'bytes: ', (end_time - start_time)
                print 'dst ip address= ', clientName, 'and dst port = ', clientPort 
            else:
                recv_size += MSS
                #send ACK: 'recv_size' is also the sequence number i.e. next expected byte number
                pack_ACK = struct.pack('IHH', recv_size, all_zeros, ACK_indicator)
                serverSocket.sendto(pack_ACK, (clientName, clientPort))
                #print 'ACK sent. Expecting seq#: ', recv_size, ' next to: ', clientName,':', clientPort, '.'
        
    #Close socket and file object
    file_object.close()
    serverSocket.close()

if __name__ == "__main__":
    main()

        








