# Ryu-controller-port-statistics-monitoring-and-recording ( Extension )

This is an extension of of Ryu controller "simple_switch_13" that collect the port statistics data to csv files (for more, read Ryu controller generous documentation).

The code will generate an $n$ csv files, where $n$ is the number of datapaths ( OVS switches ). A time stamp field has been added, this is very  important if you want to do time-series data analyis. 


Do not forget to change the line : path = './my_ryu_apps/monitor_data' , to put your own path.
Ex:
Run a mininet network :

sudo mn --topo tree,3 --mac --arp --switch ovsk  --link tc  --controller remote,ip=127.0.0.1,port=6633

and run the script above:

ryu run  --verbose --observe-links  ./my_ryu_apps/FILENAME.py 

Replace FILENAME with name of the file with the name of the file of the script above 

In case you want the data of the whole network in single csv file, you can concatenate these csv files into a single file using Pandas libarary .


