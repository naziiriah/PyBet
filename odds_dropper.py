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
    
    async def call_pinnacle(self):
        try:
            self.numberOfTimesAPIIsCalled += 1
            complete_api = f"{self.odds_api}{self.time}{self.endTag}";
            response = requests.get(complete_api)
            if(response.status_code == 200):
                data = response.json()['data']
                filtered_data = [state for state in data if abs(float(state['points'])) % 0.5 != 0.25]
                self.data  = filtered_data
        except:
            print("error hppend")
        finally: 
            self.data.sort(key=lambda x: (x['lineType'] != 'money_line', x['lineType'] == 'money_line'))

            if len(self.data) != 0:
                self.sort_pinnacle_soccer_matches()  
                self.time = int(time.time() * 1000)  

            print(self.data)


    def sort_pinnacle_soccer_matches(self):
        new_data = self.data
        self.data = [state for state in self.data if abs(float(state['points'])) % 0.5 != 0.25]
        self.data = [state for state in self.data if state['nickname'] != 'Soccer']
        for state in new_data:
            if state['nickname'] == 'Soccer' and '(Corners)' not in state['home']:
                self.data.append(state)
                
    def is_ready_for_next_call(self):
        return self.index == len(self.data)
    
    def update_index(self, index):
        self.index = index
    

