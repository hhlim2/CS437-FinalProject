# CS437-FinalProject
YouTube Demo Link:

# Setup and Run Streamlit App Locally
Prerequisites 
- Raspberry Pi
- Raspberry Pi Camera
- Waveshare Infared Sensor https://www.waveshare.com/wiki/Infrared_Temperature_Sensor
- Python 3.11

1. Clone this repository
```
git clone https://github.com/hhlim2/CS437-FinalProject.git
```

2. Create a virtual environment within the repository directory
```
cd CS437-FinalProject
python3 -m venv env
```

3. Activate the virtual environment
```
source env/bin/activate
```

4. Upgrade pip and install all dependencies
```
pip install --upgrade pip
pip install -r requirements.txt
```

5. Run the application
```
streamlit run final_project.py
```
