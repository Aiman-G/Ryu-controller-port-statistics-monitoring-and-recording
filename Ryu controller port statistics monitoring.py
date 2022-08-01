

import os # for file paths and svaing csv files
import pandas as pd
import json 
import csv
from datetime import datetime
  


from operator import attrgetter
from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub



class SimpleMonitor13(simple_switch_13.SimpleSwitch13):

    def __init__(self, *args, **kwargs):
        super(SimpleMonitor13, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(10)

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)


       

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         '
                         'in-port  eth-dst           '
                         'out-port packets  bytes')
        self.logger.info('---------------- '
                         '-------- ----------------- '
                         '-------- -------- --------')
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['eth_dst'])):
            self.logger.info('%016x %8x %17s %8x %8d %8d',
                             ev.msg.datapath.id,
                             stat.match['in_port'], stat.match['eth_dst'],
                             stat.instructions[0].actions[0].port,
                             stat.packet_count, stat.byte_count)


        # *********** Flow Statistics Data ***************
    


    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         port     '
                         'rx-pkts  rx-bytes rx-error '
                         'tx-pkts  tx-bytes tx-error')
        self.logger.info('---------------- -------- '
                         '-------- -------- -------- '
                         '-------- -------- --------')
        for stat in sorted(body, key=attrgetter('port_no')):
            self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d',
                             ev.msg.datapath.id, stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors)

          
          
          
        # *********** Port statistics Data ************
        path = './my_ryu_apps/monitor_data' # change this path to your prefered path
        str_datapath_id = str( ev.msg.datapath.id ) 
        output_file_name = os.path.join( path,'port_stats_dpid_' + str_datapath_id + '.csv' ) # we will write a independent file for each datapath
        # note : body in ev.msg.body is a list of namedTuples. so to get to the named tuple use the list index frst
        for element in body:
            
            time_stamp_dict= {}
            port_stats_dict = {}
            time_stamp_dict['DateTime'] = datetime.now()
            port_stats_dict['datapath'] = ev.msg.datapath.id
            port_stats_dict = {**time_stamp_dict , **port_stats_dict}

            #print ("element as dict", element._asdict())
            port_stats_dict_temporary = {}
            port_stats_dict_temporary = element._asdict() # _asdict() method is a builtin method to convert namedtuples to dictionaaries.
            port_stats_dict = {**port_stats_dict, **port_stats_dict_temporary} # merge the temporory dictionry with stats dict, to add datapath first
            #port_stats_dict['port_no'] = hex( port_stats_dict['port_no'] ) # if we want prot numbers in hexidecimal 
            self.write_csv(port_stats_dict, output_file_name)  
                         
            
    @staticmethod
    def write_csv(data_dict,output_file_name):

        if os.path.isfile(output_file_name) ==  False : # if file does not exists 
            
            with open(output_file_name, 'w') as outfile:
                writer = csv.writer(outfile) # open file for wiriting ( wriing the headers (column names))
                writer.writerow(list(data_dict.keys())) # add headers

        # open for appending rows , if we want to wirte the updated statistcs of each switch,
        # we can use 'w', instead of 'a'. 
        with open(output_file_name, 'a') as outfile: 
            writer = csv.DictWriter(outfile, fieldnames = data_dict.keys())
            writer.writerow(data_dict)



