import pandas as pd
from datetime import datetime
import logging

# Define logger and set logging template
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

class TestData:
    start_date: str
    end_date: str

    def __init__(self, start_date: str = '2019-01-02', end_date: str = None):
        self.start_date = start_date
        self.end_date = end_date if end_date else datetime.now().strftime('%Y-%m-%d')
        
        self.stocks = [
            'ACB', 'BCM', 'BID', 'BVH', 'CTG', 'FPT', 'GAS', 'GVR', 'HDB', 'HPG',
            'MBB', 'MSN', 'MWG', 'PLX', 'POW', 'SAB', 'SHB', 'SSB', 'SSI', 'STB',
            'TCB', 'TPB', 'VCB', 'VHM', 'VIB', 'VIC', 'VJC', 'VNM', 'VPB', 'VRE'
        ]
        
        self.indices = ['VNINDEX', 'HNXINDEX', 'UPCOMINDEX']
        
        self.group_codes = [
            'HOSE', 'VN30', 'VNMidCap', 'VNSmallCap', 'VNAllShare', 'VN100', 'ETF',
            'HNX', 'HNX30', 'HNXCon', 'HNXFin', 'HNXLCap', 'HNXMSCap', 'HNXMan', 'UPCOM', 'FU_INDEX'
        ]
        
        self.etfs = [
            "E1VFVN30", "FUEBFVND", "FUEDCMID", "FUEFCV50", "FUEIP100", "FUEKIV30",
            "FUEKIVFS", "FUEKIVND", "FUEMAV30", "FUEMAVND", "FUESSV30", "FUESSV50",
            "FUESSVFL", "FUEVFVND", "FUEVN100"
        ]
        
        self.cw = [
            'CACB2304', 'CACB2305', 'CACB2306', 'CACB2307', 'CACB2401', 'CFPT2310',
            'CFPT2313', 'CFPT2314', 'CFPT2316', 'CFPT2317', 'CFPT2318', 'CHDB2306',
            'CHPG2315', 'CHPG2316', 'CHPG2319', 'CHPG2322', 'CHPG2329', 'CHPG2331',
            'CHPG2332', 'CHPG2333'
        ]
        
        self.futures = [
            'VN30F2406', 'VN30F2407', 'VN30F2409', 'VN30F2412'
        ]