import sqlite3

class database:
    
    def __init__(self) -> None:
        self.db = sqlite3.connect('index.db')
        self.cursor = self.db.cursor()
        print('DB connected')
        
    def create_table(self):
        try:
            table ="""CREATE TABLE IF NOT EXISTS record (id STRING PRIMARY KEY, OUTCOME, GOALLINE, DATE)"""
            self.cursor.execute(table)
            print("table created")
        except:
            print("error happened")
        finally:
            print("completed")
            
    def get_entry(self, __primary_key__):
        query = f"""SELECT  OUTCOME, GOALLINE, DATE FROM record WHERE id = {__primary_key__}"""
        self.cursor.execute(query)
        print("Only one data") 
        output = self.cursor.fetchone() 
        return output
        
    def insert(self, data):
        # Corrected Python SQLite code
        try:
            # Assuming 'data' is a dictionary with the necessary keys
            query = """INSERT INTO record (id, OUTCOME, GOALLINE, DATE) VALUES (?, ?, ?, ?)"""
            self.cursor.execute(query, (data["id"], data["OUTCOME"], data["GOALLINE"], data["DATE"]))
            self.db.commit()  # Commit the transaction
            print(f"Item {data['id']} added")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            
    def update_record(self, data):
        if data['UPDATE'] == 'goalline':
            query = f"UPDATE record SET GOALLINE = TRUE WHERE id = {data['id']}"
            self.cursor.execute(query)
        elif data['UPDATE'] == 'outcome':
            query = f"UPDATE record SET OUTCOME = TRUE WHERE id = {data['id']}"
            self.cursor.execute(query)
        self.db.commit()
        
    def query_all(self):
        query = f"""SELECT  OUTCOME, GOALLINE, DATE FROM record"""
        self.cursor.execute(query)
        output = self.cursor.fetchall()
        for i,out in enumerate(output):
            print(out[0]) 
            
        print(output) 


    def close_connection(self):
        self.cursor.close()
        print("connection closed")