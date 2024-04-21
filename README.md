# CS437-FinalProject
YouTube Demo Link: https://youtu.be/Gpb6cuFjyJw

# Setup and Run Streamlit App Locally
Prerequisites 
- Raspberry Pi
- Raspberry Pi Camera
- Waveshare Infrared Sensor https://www.waveshare.com/wiki/Infrared_Temperature_Sensor
- Python 3.11
- External monitor, keyboard, and mouse

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
sudo apt install python3-smbus
```

5. Run the model_testing.ipynb notebook through the cell that includes
```
model2 = create_model2()

model2.fit(train_ds, epochs=10, validation_data=val_ds)

#save the model
model2.save("mask_compliance.h5")
```


6. Run the application
```
streamlit run final_project.py
```
