# Citi Bike Over the Years

This is the code to build datasets to anaylsis Citibike over the years. To find the results of [this project check out the website displaying this data](https://www.gabrielhn.com/topics/citibike/)

This project uses python to make the data found in data that feeds into the graphs.

![website](/citibike_map.png)

# Installs
```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt 
```

Additionally, would need to create [a Mapbox Directions API to use found here](https://docs.mapbox.com/help/glossary/access-token/).


# Usage
Run the script

```
python main.py <command>

# To build the datasets locally
python main.py local

# To build the datasets within your configured AWS S3 bucket

python main.py s3

```