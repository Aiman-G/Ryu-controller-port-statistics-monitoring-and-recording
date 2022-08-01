# Ryu-controller-port-statistics-monitoring-and-recording ( Extension )
Do not forget to change the line : path = './my_ryu_apps/monitor_data' , to put your own path.
There will be an n csv files, where n is the number of datapaths ( OVS switches ) .

Exmaple : Run a mininet network :

sudo mn --topo tree,3 --mac --arp --switch ovsk  --link tc  --controller remote,ip=127.0.0.1,port=6633

and run the script above:

ryu run  --verbose --observe-links  ./my_ryu_apps/FILENAME.py 

Replace FILENAME with name of the file with the name of the file of the script above 
