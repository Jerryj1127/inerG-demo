import xlrd
import os
from src.Config import Config
from src.utils.downloader import download_file
from src.db_connection_manager import DatabaseConnection



def get_excel_data(filename):
    try:
        
        workbook = xlrd.open_workbook(filename)
        sheet = workbook.sheet_by_index(0)
        
        # Get the headers :: oth row
        headers = [str(cell.value).strip() for cell in sheet.row(0)]
        
        data = [] 
        for row_no in range(1, sheet.nrows): #skipped 0th row
            row = sheet.row(row_no)
            row_dict = {}
            for col_no, cell in enumerate(row):
                value = cell.value
                row_dict[headers[col_no]] = value
            data.append(row_dict)
        
        return data #returns the data as a list of key:val pairs
    except Exception as e:
        print(f"Error reading the .xls file: {e}")
        return None



def create_db_schema(conn):

    cursor = conn.cursor()
    
    #  table - companies
    cursor.execute('''CREATE TABLE IF NOT EXISTS companies (
                        company_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_name TEXT UNIQUE NOT NULL
                    )'''
                   )
                    
    # table- counties
    cursor.execute('''CREATE TABLE IF NOT EXISTS counties (
                        county_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        county_name TEXT UNIQUE NOT NULL
                    )'''
                   )
    
    # table - townships 
    cursor.execute('''CREATE TABLE IF NOT EXISTS townships (
                        township_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        township_name TEXT NOT NULL,
                        county_id INTEGER NOT NULL,
                        FOREIGN KEY (county_id) REFERENCES counties(county_id),
                        UNIQUE(township_name, county_id)
                    )'''
                   )
    
    # table - wells 
    cursor.execute('''CREATE TABLE IF NOT EXISTS wells (
                        well_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        api_well_number INTEGER UNIQUE NOT NULL,
                        well_name TEXT NOT NULL,
                        well_number TEXT NOT NULL,
                        company_id INTEGER NOT NULL,
                        township_id INTEGER NOT NULL,
                        FOREIGN KEY (company_id) REFERENCES companies(company_id),
                        FOREIGN KEY (township_id) REFERENCES townships(township_id)
                    )'''
                   )
                
    # table - production_data 
    cursor.execute('''CREATE TABLE IF NOT EXISTS production_data (
                        production_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        well_id INTEGER NOT NULL,
                        production_year INTEGER NOT NULL,
                        quarter INTEGER NOT NULL,
                        oil_production FLOAT,  
                        gas_production FLOAT,
                        brine_production FLOAT,
                        days INTEGER NOT NULL,
                        FOREIGN KEY (well_id) REFERENCES wells(well_id),
                        UNIQUE(well_id, production_year, quarter)
                    )'''
                   )

    conn.commit()
    return conn



def fill_db_data(data, conn):

    cursor = conn.cursor()
    
    # insert company names
    companies = set(row['OWNER NAME'] for row in data)
    for company in companies:
        cursor.execute('INSERT OR IGNORE INTO companies (company_name) VALUES (?)', (company,))
    

    # insert counties int the counties table
    counties = set(row['COUNTY'] for row in data)
    for county in counties:
        cursor.execute('INSERT OR IGNORE INTO counties (county_name) VALUES (?)', (county,))
    

    # insert townships wrt to the county_id 
    township_counties = set((row['TOWNSHIP'], row['COUNTY']) for row in data)
    for township, county in township_counties:

        cursor.execute('SELECT county_id FROM counties WHERE county_name = ?', (county,))
        county_id = cursor.fetchone()[0]
        
        cursor.execute(''' INSERT OR IGNORE INTO townships (township_name, county_id) 
                            VALUES (?, ?)
                            ''', (township, county_id))
    


    for row in data:
        # matching the company_id from companies table
        cursor.execute('SELECT company_id FROM companies WHERE company_name = ?', (row['OWNER NAME'],))
        company_id = cursor.fetchone()[0]
        
        # same for  county_id and township_id
        cursor.execute('SELECT county_id FROM counties WHERE county_name = ?', (row['COUNTY'],))
        county_id = cursor.fetchone()[0]
        
        cursor.execute('''SELECT township_id FROM townships 
                            WHERE township_name = ? AND county_id = ?
                            ''', (row['TOWNSHIP'], county_id))
        township_id = cursor.fetchone()[0]
        


        # Insert to the wells table if it doesnt exist
        # followed by a select opr to get row data with  well_id
        cursor.execute('''
        INSERT OR IGNORE INTO wells 
        (api_well_number, well_name, well_number, company_id, township_id)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            row['API WELL  NUMBER'],
            row['WELL NAME'],
            row['WELL NUMBER'],
            company_id,
            township_id
        ))
        
        cursor.execute('SELECT well_id FROM wells WHERE api_well_number = ?', (row['API WELL  NUMBER'],))
        well_id = cursor.fetchone()[0]
        


        # Inserting into the production_data table
        cursor.execute('''
        INSERT OR IGNORE INTO production_data 
        (well_id, production_year, quarter, oil_production, gas_production, 
         brine_production, days)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            well_id,
            int(row['Production Year']),
            int(row['QUARTER 1,2,3,4']),
            float(row['OIL']),
            float(row['GAS']),
            float(row['BRINE']),
            int(row['DAYS'])
        ))
    
    conn.commit()

def check_and_load_db():
    # url = "https://ohiodnr.gov/static/documents/oil-gas/production/20210309_2020_1%20-%204.xls" #--> returns 301
    url = "https://dam.assets.ohio.gov/raw/upload/ohiodnr.gov/documents/oil-gas/production/20210309_2020_1%20-%204.xls"

    if os.path.isfile(Config.DB_FILENAME):
        return
    
    filename = "assets/20210309_2020_1 - 4.xls"
    if not os.path.isfile(filename):
        filename = download_file(url)

    data = get_excel_data(filename)
    if data is None:
        raise Exception("Error while reading data from Excel sheet.")
    
    conn = DatabaseConnection.get_connection()
    create_db_schema(conn)
    

    fill_db_data(data, conn)
    
    # closing the connection right after populating the db
    # if required flask requests, if any can reopen another connecton
    DatabaseConnection.close_connection()
    
    print("Database created and populated successfully!")




# if __name__ == "__main__":
#     check_and_load_db()
