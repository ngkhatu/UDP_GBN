client
---------
$ python client_simple_FTP_GBN.py <server ip> <server-port(7735)><location/filename> <window size> <max segment size> <RTT/timeout>

jondoe@SFTPclient:~/Desktop$ python client_simple_FTP_GBN.py 192.168.0.22 7735 ./scratch.py 53 83 .0003
Timeout, sequence number =  0
Timeout, sequence number =  0
Timeout, sequence number =  2075
Timeout, sequence number =  2241
Timeout, sequence number =  3154
Timeout, sequence number =  3320
Time to transmit  ./scratch.py with  4076 bytes:  0.513924837112
using Go-back-N where: N = 53 MSS =  83 RTT =  0.0003
dst ip address=  192.168.0.22 and dst port =  7735
Timeout, sequence number =  4076

server
---------
$ python server_simple_FTP_GBN.py <local-port(7735) <location/filename> <prob of packet loss> <max segment size>

jondoe@SFTPserver:~/Desktop$ python server_simple_FTP_GBN.py 7735 ./sftp_readme.txt .05 83
The server is ready to receive
Receive file size (in bytes):  764
Packet loss, sequence number =  83
File ./sftp_readme.txt of  764  bytes has been received.  MSS =  83
Time to receive  ./sftp_readme.txt with  764 bytes:  0.0593628883362
dst ip address=  192.168.0.23 and dst port =  44145
