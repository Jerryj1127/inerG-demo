from src.db_connection_manager import DatabaseConnection

class Well:
    def __init__(self, api_well_number):
        self.api_well_number = api_well_number
        self.conn = DatabaseConnection.get_connection()
        self.cursor = self.conn.cursor()
        
        # Verify well exists and get basic info
        self.cursor.execute('''
            SELECT w.well_id, w.well_name, w.well_number, 
                   c.company_name, co.county_name, t.township_name
            FROM wells w
            JOIN companies c ON w.company_id = c.company_id
            JOIN townships t ON w.township_id = t.township_id
            JOIN counties co ON t.county_id = co.county_id
            WHERE w.api_well_number = ?
        ''', (api_well_number,))
        
        result = self.cursor.fetchone()
        if result is None:
            raise ValueError(f"No well found with API number: {api_well_number}")
            
        self.well_id = result[0]
        self.well_name = result[1]
        self.well_number = result[2]
        self.company = result[3]
        self.county = result[4]
        self.township = result[5]



    # Making the sqlite do the heavy lifing (SUM) instead of getting data of each quater
    #and sum them up in python, which would cost 4 seperate db fetch + addition in python 
    def get_production_for_year(self, production_year: int = 2020):
        self.cursor.execute('''
            SELECT 
                SUM(oil_production) as total_oil,
                SUM(gas_production) as total_gas,
                SUM(brine_production) as total_brine
            FROM production_data
            WHERE well_id = ? AND production_year = ?
        ''', (self.well_id, production_year))
        
        result = self.cursor.fetchone()
        return {
            'total_oil': result[0] or 0,
            'total_gas': result[1] or 0,
            'total_brine': result[2] or 0
        }
    
    #gets the total production so far, to be used when there is multiple year worth of data
    def get_total_production(self):
        self.cursor.execute('''
            SELECT 
                SUM(oil_production) as total_oil,
                SUM(gas_production) as total_gas,
                SUM(brine_production) as total_brine
            FROM production_data
            WHERE well_id = ?
        ''', (self.well_id,))
        
        result = self.cursor.fetchone()
        return {
            'total_oil': result[0] or 0,
            'total_gas': result[1] or 0,
            'total_brine': result[2] or 0
        }



    def get_production_for_quarter(self, quarter: int, production_year: int = 2020):
        pass



    def __str__(self):
        return f"API Well Number: {self.api_well_number}\n" \
                f"Well Name: {self.well_name}\n" \
                f"Company: {self.company}\n" \
                f"County: {self.county}\n" \
                f"Township: {self.township}"




# #test
# if __name__ == "__main__":
    
#     x = "34059242540000remove_this"
    
#     try:
#         well = Well(x)
#         print(well)    
#         print(well.get_total_production())
#         print(well.get_production_for_year(2022))
        
#     except Exception as e:
#         print("Error: ", e)

#     finally:
#         DatabaseConnection.close_connection()