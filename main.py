import odds_dropper
import book_maker
from dotenv import load_dotenv
import schedule
import time
load_dotenv()

odds_event = odds_dropper.oddsDropper()
sporty_event = book_maker.bookMaker()

def main():
    if len(odds_event.data) > 0:
        for i,event in enumerate(odds_event.data):
            try:
                if i == 0:
                    sporty_event.open_browser()
                    time.sleep(4)
                    sporty_event.open_site()
                    time.sleep(4)
                    sporty_event.click_layout()
                    time.sleep(2)
                    sporty_event.login()
                sporty_event.store_event(event)
                time.sleep(2)
                sporty_event.search_match()
                sporty_event.get_event()
                for i,events_from_sporty in enumerate(sporty_event.searched_event):
                    if sporty_event.compare_sporty_events_with_pinnacle(i):
                        sporty_event.select_event(i)
                        time.sleep(3)
                        sporty_event.select_all_tag()
                        time.sleep(3)
                        if "Soccer" in sporty_event.event_from_pinnacle['nickname']: 
                            if sporty_event.event_from_pinnacle['periodNumber'] == "0":
                                sporty_event.sort_football_bets_base_on_outcome
                        elif "Tennis" in sporty_event.event_from_pinnacle['nickname']:
                            sporty_event.sort_tennis_bets_base_on_outcome()
                        elif "Basketball" in sporty_event.event_from_pinnacle['nickname']:
                            sporty_event.sort_basketball_bets_base_on_outcome()
                        else:
                            print("non selected sports")
            except Exception as e:
                print(e)
            finally:
                sporty_event.searched_event = []
                if len(odds_event.data) - 1 == i:
                    sporty_event.close_browser()
                else:
                    sporty_event.to_home()
                    time.sleep(3)
            odds_event.update_index(i+1)
    else:
        odds_event.update_index(0)   

   
def start():
    if odds_event.is_ready_for_next_call():
        odds_event.call_pinnacle()
        time.sleep(10)
        main()


schedule.every(60).seconds.do(start)

while True:
    schedule.run_pending()
    time.sleep(1)

