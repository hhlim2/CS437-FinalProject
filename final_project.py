#LIbrary imports
import streamlit as st
import numpy as np
import smbus
import time
import cv2
import tensorflow as tf
from PIL import Image
import os
import numpy as np
import pytextnow
from dotenv import load_dotenv

#load user credentials from .env file
load_dotenv()

#fix encoding issue - may also need to enter export 'PYTHONUTF8'=1 in terminal
os.environ['PYTHONUTF8']='1'

st.title('Mask compliance and temperature check')

#allow user to select their NetID
contact = st.selectbox('NetID', placeholder='Select your NetID', options = ['hhlim2', 'stud_1', 'stud_2', 'stud_3', 'stud_4'], index=None)


col1, col2 = st.columns(2)

#using documentation for temperature sensor from https://www.waveshare.com/wiki/Infrared_Temperature_Sensor
class MLX90614():

    MLX90614_RAWIR1=0x04
    MLX90614_RAWIR2=0x05
    MLX90614_TA=0x06
    MLX90614_TOBJ1=0x07
    MLX90614_TOBJ2=0x08

    MLX90614_TOMAX=0x20
    MLX90614_TOMIN=0x21
    MLX90614_PWMCTRL=0x22
    MLX90614_TARANGE=0x23
    MLX90614_EMISS=0x24
    MLX90614_CONFIG=0x25
    MLX90614_ADDR=0x0E
    MLX90614_ID1=0x3C
    MLX90614_ID2=0x3D
    MLX90614_ID3=0x3E
    MLX90614_ID4=0x3F

    comm_retries = 5
    comm_sleep_amount = 0.1

    def __init__(self, address=0x5a, bus_num=1):
        self.bus_num = bus_num
        self.address = address
        self.bus = smbus.SMBus(bus=bus_num)

    def read_reg(self, reg_addr):
        err = None
        for i in range(self.comm_retries):
            try:
                return self.bus.read_word_data(self.address, reg_addr)
            except IOError as e:
                err = e
                #"Rate limiting" - sleeping to prevent problems with sensor
                #when requesting data too quickly
                time(self.comm_sleep_amount)
        #By this time, we made a couple requests and the sensor didn't respond
        #(judging by the fact we haven't returned from this function yet)
        #So let's just re-raise the last IOError we got
        raise err

    #return temperature in deg F
    def data_to_temp(self, data):
        temp = (data *0.02) - 273.15 
        return temp*1.8 + 32
    def get_amb_temp(self):
        data = self.read_reg(self.MLX90614_TA)
        return self.data_to_temp(data)

    def get_obj_temp(self):
        data = self.read_reg(self.MLX90614_TOBJ1)
        return self.data_to_temp(data)

#initalize the temperature sensor
temp_sensor = MLX90614()

#load the image classification button
if "model" not in st.session_state:
    model = tf.keras.models.load_model('mask_compliance.h5')
    st.session_state.model = model


#Initalize variables 
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

if 'count' not in st.session_state:
    st.session_state.count = 0
    
if 'user_tmp' not in st.session_state:
    st.session_state.user_tmp = 0



#set to true or false depending if you want to send the compliance text message (need a TextNow account & credentials)
if 'send_message' not in st.session_state:
    st.session_state.send_message = False

#webcam source
source_webcam = 0

if 'st_frame' not in st.session_state:
    st.session_state.st_frame = st.empty()


def change_state():
    st.session_state.button_clicked = True
    
if contact:       
    with col2:
        #initalize button to take photo and temperature reading
        st.button(label = "Take Photo", key='photo', on_click = change_state)


    with col1:
        
        #remove previous user image
        if 'temp.jpg' in os.listdir():
            os.remove('temp.jpg')
        
        #streamlit camera input is very grainy, we reuse some of the picamera code from the car lab
        vid_cap = cv2.VideoCapture(source_webcam)
        vid_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 256)
        vid_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 256)

        while (vid_cap.isOpened()):
            
            success, image = vid_cap.read()

            if st.session_state.button_clicked:
                
                #write the current frame to an image
                cv2.imwrite('temp.jpg', image)
        
                st.session_state.st_frame.image('temp.jpg')
                
                #read user's temperature
                st.session_state.user_tmp = temp_sensor.get_obj_temp()
                st.write('User Temperature: ', str(round(st.session_state.user_tmp, 2)))
                temp_check = False
                if st.session_state.user_tmp > 90 and st.session_state.user_tmp < 99:
                    st.write('Temperature check passed')
                    temp_check = True
                else: 
                    st.write('Temperature check failed')
                    


                #pass image to model, get mask compliance results
                img = Image.open('temp.jpg')
                img = np.array(img)
                prob = st.session_state.model.predict(img[None, :, :, :])
  
                st.session_state.count += 1
                
                if np.argmax(prob) == 0:
                    st.write('Mask wearing is confirmed')
                else:
                    st.write('Please put on a mask and try again')
                

                #if temperature and mask are within compliance, send text message to administrator
                if np.argmax(prob) == 0 and temp_check:
                    st.success('Mask compliance and temperature check passed, thank you!')
                    #send  message with confirmation
                    if st.session_state.send_message:
                        text_client = pytextnow.Client(os.getenv('username'), os.getenv('sid'), os.getenv('csrf'))
                        user_temp_send = str(round(st.session_state.user_tmp, 2))
                        text_client.send_sms(os.getenv('phone'), f'{contact} has passed their health check. Their temperature is {user_temp_send}. An image of their mask check is attached.')
                        text_client.send_mms(os.getenv('phone'), 'temp.jpg')   
                    
                else: 
                    st.error('Mask compliance or temperature check failed, please try again or return when healthy')

                st.session_state.button_clicked = False
           
            #display user photo instead of picamera feed
            elif success and st.session_state.count == 0:
                st.session_state.st_frame.image(image)
            
            elif success and st.session_state.count > 0:
                st.session_state.st_frame.image('temp.jpg')

                    


        
        
            
                
  








    
    



