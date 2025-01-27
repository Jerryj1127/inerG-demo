<p align="center">
  <h1 style="text-align: center;">inerG Flask Server Demo</h1>
</p>

****

---

## **Overview**

Flask server to retrive and return annual production data for oil, gas, and brine

---

## **Table of Contents**

1. [Overview](#overview)   
2. [Local Installation](#installation)  
3. [Database Schema](#Database_Schema)  
3. [Deployments](#Deployments)  



## **Installation**

To install this project, follow these steps:

Make sure git, python and pip are installed

Installation steps:
```bash
# Clone the repository
git clone https://github.com/Jerryj1127/inerG-demo.git 

cd inerG-demo/ 

# Install the dependencies
pip install -r requirements.txt

# Start the server
python3 main.py

```


## **Database_Schema**

> Excel data is normalised into different tables based on the below schema
<p align="center">
  <img src="https://raw.githubusercontent.com/Jerryj1127/inerG-demo/main/docs/images/db_schema.png" alt="DB Schema" width="900" />
</p>



## **Deployments**

  https://production-demo.onrender.com/data?well=34059242540000

  This is a working demo of this github repo, hosted on render.com

  >Note 1 : Since it's using free tier, the initial GET call might take upto a minute

  >Note 2:  There's no need to specify the port 8080 here as render.com redirects incoming https traffic on port 443 to open ports of the server, 8080 in this case.

