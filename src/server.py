#!/usr/bin/env python3

from flask import Flask, jsonify, request
from src.db_connection_manager import DatabaseConnection
from src.well import Well
from src.load_db import check_and_load_db

check_and_load_db()

app = Flask(__name__)

@app.route("/data", methods=['GET'])
def get_well_data():

    well_api_number = request.args.get("well") 
    if not well_api_number:
        return jsonify({"error": "Well number is required"}), 400
    
    try:
        well = Well(well_api_number)
        
        production_data = well.get_production_for_year() 
        
        #rearranging the keys and values before returing it
        # returing int instead of float, like in the sample data provided in qn
        
        response_data = {
            "oil": round(production_data["total_oil"]),
            "gas": round(production_data["total_gas"]),
            "brine": round(production_data["total_brine"])
        }
        
        return jsonify(response_data)
    
        # {
        # "oil": 381
        # "gas": 108074
        # "brine": 939
        # }
        # Sample data provided in the question is missing commas which makes it an invalid json 
        # So assuming it's a typing mistake and returning JSON
        # if it was a delebrate thing, we can return the data as a string to match that case.

    except ValueError: #in case theres no correspoding well data
        return jsonify({"error": f"Well data for {well_api_number} not found"}), 404
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500


@app.teardown_appcontext
def cleanup(exception=None):
    ## "SQLite objects created in a thread can only be used in that same thread."
    # making sure the db connection is closed after every req, so that if flask is ever to thread out,
    # or say a proper wsgi server like gunicorn is to be used ... it should make a big hustle

    DatabaseConnection.close_connection()

if __name__ == "__main__":
    #Running the flask server
    app.run(host="0.0.0.0", port=8080)

