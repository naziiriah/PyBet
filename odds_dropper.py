import time
import os
import requests

class oddsDropper:
    def __init__(self):
        self.data = []
        self.time = int(round(time.time() * 1000))
        self.endTag = '-0'
        self.odds_api = os.getenv('ODDS_API')
        self.index = 0
        self.numberOfTimesAPIIsCalled = 0
    
    def call_pinnacle(self):
        try:
            self.numberOfTimesAPIIsCalled += 1
            complete_api = f"{self.odds_api}{self.time}{self.endTag}"
            response = requests.get(complete_api)
            if(response.status_code == 200):
                data = response.json()['data']
                filtered_stte = []
                for i, state in enumerate(data):
                   if state['points']  == "" or' ':
                       filtered_stte.append(state)
                   else:
                         if ".25" or ".75" not in state['points']:
                            filtered_stte.append(state)
                
                self.data = filtered_stte                            
                       
        except Exception as e:
            print("error hppend", e)
        finally: 
            self.data.sort(key=lambda x: (x['lineType'] != 'money_line', x['lineType'] == 'money_line'))

            if len(self.data) != 0:
                self.sort_pinnacle_soccer_matches()  
                self.time = int(round(time.time() * 1000))

            print(self.data)


    def sort_pinnacle_soccer_matches(self):
        new_data = self.data
        self.data = [state for state in self.data if state['nickname'] != 'Soccer']
        for state in new_data:
            if state['nickname'] == 'Soccer' and '(Corners)' not in state['home']:
                self.data.append(state)
                
    def is_ready_for_next_call(self):
        return self.index == len(self.data)
    
    def update_index(self, index):
        self.index = index
    

