import socket
from optparse import OptionParser
import struct
import select
import sys
import thread
import threading
import time
import ctypes

def client_simple_FTP_GBN():
    """This is the client side implementation of the SFTP project.
    
        It will initiate connection with the server and then send data
        which will be collected by the server. The Go-back-N sliding window protocol with ARQ is used when transferring the data.
        
        Authored by: Nikhil Khatu
        CSC573 Professor: Harfoush
    """
    pass

# compute 16-bit internet checksum of data
def sum(data):
    csum = 0
    for i in range(0,len(data),2):			#check data in increments of 2 bytes. i.e. pair adjacent octets
        if i + 1 >= len(data): csum += ord(data[i]) & 0xFF
        else: csum = csum + (((ord(data[i]) << 8) & 0xFF00) + (ord(data[i+1]) & 0xFF))
    while (csum >> 16) > 0:					#compute 1's complement sum over each octer pair
        csum = (csum & 0xFFFF) + (csum >> 16)
    return (~csum) & 0xFFFF				#return 1's complement of sum

#rdt_send() gets data from the file, creates the packet, and then sends it.
#Additionally each packet is added in the buffer.
def rdt_send():
    global nextseqnum, amount_data_sent, base, file_object, file_size
    global dict, clientSocket, N, MSS, t, file_to_be_sent, RTT

    start_time = time.time() #start delay timer
    file_object = open(file_to_be_sent, "rb", 0)
    
    while base < file_size:
        if nextseqnum < (base + (N * MSS)):
            
            if (file_size - amount_data_sent) < MSS:
                left_to_send = file_size - amount_data_sent
                data_buffer = file_object.read(left_to_send)
                pack_packet = struct.pack('IHH%ds' % (left_to_send, ), nextseqnum, sum(data_buffer), 21845, data_buffer)
                amount_data_sent += left_to_send
            else:
                data_buffer = file_object.read(MSS)
                pack_packet = struct.pack('IHH%ds' % (MSS, ), nextseqnum, sum(data_buffer), 21845, data_buffer)
                amount_data_sent += MSS
            if(nextseqnum in dict): pass #print 'error: Dictionary already has key! Cannot add value! Seq#: ', nextseqnum
            else:
                dict.setdefault(nextseqnum, pack_packet)
                clientSocket.sendto(pack_packet, (serverName, serverPort))
                #print 'sent: ', nextseqnum, base
            if (base == nextseqnum):
                t.cancel()
                t = threading.Timer(RTT, timeout)
                t.start()
            nextseqnum += MSS
         
        else: pass
    file_object.close()
    end_time = time.time()
    print 'Time to transmit ', file_to_be_sent,'with ', amount_data_sent,'bytes: ', (end_time - start_time)
    print 'using Go-back-N where: N =', N, 'MSS = ', MSS, 'RTT = ', RTT
    print 'dst ip address= ', serverName, 'and dst port = ', serverPort 
    pass

#rdt_rcv receives all the available data in the buffer, unpacks it, and then stores it in a tuple.
#the data is then processed to check for expected ACKs.
#if buffered data is no longer needed it is removed from the dictionary container
def rdt_rcv():
    global nextseqnum, base, file_size, dict, clientSocket, RTT
    global N, MSS, t, serverName, serverPort, amount_data_sent
    
    ack_pack = ctypes.create_unicode_buffer(8, 512)
    while base < file_size:
        bytes_of_ack = clientSocket.recv_into(ack_pack)
        ACK_tuple = struct.unpack_from('IHH', ack_pack)
        
        i = 8
        while i <= bytes_of_ack:
            ACK_seq, all_zeros, ACK_indicator = iter(ACK_tuple)
            #print 'rcv:', ACK_seq, base
            if (all_zeros == 0 and ACK_indicator == 43690):
                base = ACK_seq
                #if ACK_seq > base + (N * MSS): base = ACK_seq + MSS ####???????
                #print 'ACK rcv: ', ACK_seq
                iter_item = dict.iterkeys()
                while 1:
                    try:
                        seqkey = iter_item.next()
                        if seqkey < base: #########???????????!!!!!!!!!!!!
                            del dict[seqkey]
                            #print 'seqkey deleted', seqkey, ACK_seq
                    except: break
                
                #print 'received: base ', base,'seq# ', nextseqnum
                if base == nextseqnum: t.cancel()	# stop timer
                else:
                    t.cancel()
                    t = threading.Timer(RTT, timeout)  # restart timer
                    t.start()
            
            i += 8
    clientSocket.close()
    pass

#resends the buffered data when the timer timesout.        
def timeout():
    global dict, t, clientSocket, MSS, nextseqnum, base, RTT
    print 'Timeout, sequence number = ', base
    
    t.cancel() # stop timer
          
    i = base
    while i <= (nextseqnum - MSS) and base < file_size:               #resend packets before nextseqnum
        if(dict.has_key(i)):
            pack_packet = dict.get(i)
            clientSocket.sendto(pack_packet, (serverName, serverPort))
            #print 'Resent seq# :', i
        else: pass #print 'error: key ', i, 'does not exist in dictionary!'
        
        i += MSS
    
    #restart the timer if full file has not been acknowledged
    if base < file_size:
        t = threading.Timer(RTT, timeout) #start timer
        t.start()

    pass

# initialize the parameters
def init_parameters():
    global clientSocket, file_object, amount_data_sent, RTT
    global serverName, serverPort, N, MSS, file_size
    global base, nextseqnum, dict, t, file_to_be_sent
    
    
    ack_pack = 0
    dict = {}
    base = 0
    nextseqnum = 0
    amount_data_sent = 0
    RTT = .5
    
    #user defined values
    serverName = sys.argv[1]		#192.168.0.22
    serverPort = int(sys.argv[2])		#7735
    file_to_be_sent = sys.argv[3]	#"./rfc2131.txt"
    N = int(sys.argv[4])
    MSS = int(sys.argv[5])				#1000
    RTT = float(sys.argv[6])
    
    # Open socket and File object
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    file_object_2 = open(file_to_be_sent, "rb", 0)
    #find size of file by adjusting the reference point
    file_object_2.seek(0,2)
    file_size = file_object_2.tell()
    file_object_2.close() 
    
    pass

# Enter Main function to begin client program
def main():

    global t
    init_parameters()
    
    #send the size of file to the server and wait for ACK
    sent = False
    while sent == False:
        pack_size = struct.pack('iHH', file_size, sum(unicode(file_size)), 21845)
        clientSocket.sendto(pack_size, (serverName, serverPort))
        ack_pack = clientSocket.recv(6)
        server_received, all_zeros, ACK_indicator = struct.unpack('?HH', ack_pack)
        if (server_received == True) and (all_zeros == 0) and (ACK_indicator == 43690): sent = True
    
	# Start the threaded timer
    t = threading.Timer(RTT, timeout)
    t.start()    
    senderThread = threading.Thread(target=rdt_send)
    receiverThread = threading.Thread(target=rdt_rcv)
    senderThread.start() # start rdt_send thread
    receiverThread.start() # start rdt_rcv thread

    pass
    
if __name__ == "__main__":
    main()
