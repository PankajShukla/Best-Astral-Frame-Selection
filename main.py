

# -------------------------------------------------
# Loading Library
# -------------------------------------------------


import os
import pandas as pd
import time
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import datetime

import streamlit as st
import streamlit.components.v1 as components
from streamlit_image_select import image_select

import cv2
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import *
import mediapy as media
import ffmpeg
from PIL import Image
from io import BytesIO
import random


# -------------------------------------------------
# Set up for streamlit
# -------------------------------------------------

st.set_page_config(
    page_title="Home",
    page_icon="👋",
    layout="wide"
)

st.markdown(f'<p style="color:#9bdaf1;font-size:50px;border-radius:2%;"> Best Capture 🪐🔭</p>', unsafe_allow_html=True)

st.markdown(f'<p style="color:#d6d7d9;font-size:20px;border-radius:2%;"> This application helps to choose the best frames of the sky objects from a video captured over a camera</p>', unsafe_allow_html=True)


# -------------------------------------------------
# Set up for folders
# -------------------------------------------------



def set_up_emailid():
    try:
        c1, c2 = st.columns(2)
        with c1:
            dt = st.date_input("Pick video Capture date", datetime.date.today() - datetime.timedelta(0))

        with c2:
            id = st.text_input(label='Enter a valid email address', value = "" )
            id = id.replace(".", "|")

        return id, dt
    except:
        pass




def upload_raw_video(videopath):

    c3, c4 = st.columns(2)
    with c3:
        uploaded_file = st.file_uploader("Upload raw video ", type=["mp4", "mpeg"])
        with open(os.path.join(videopath, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        filename = os.path.join(videopath, uploaded_file.name)

    with c4:
        st.empty()

    return filename


def input_folder_initialise(id, dt):

    base_path = os.path.join(os.getcwd(), 'Newtonion_6inch_telescope')
    base_path_date = os.path.join(base_path, str(dt))
    base_path_date_id = os.path.join(base_path, str(dt), id)
    base_path_date_id_raw = os.path.join(base_path_date_id, 'Raw')

    try:
        os.mkdir(base_path)
    except FileExistsError:
        pass

    try:
        os.mkdir(base_path_date)
    except FileExistsError:
        pass

    try:
        os.mkdir(base_path_date_id)
    except FileExistsError:
        pass

    try:
        os.mkdir(base_path_date_id_raw)
    except FileExistsError:
        pass

    return base_path, base_path_date_id, base_path_date_id_raw




def target_folder_initialise(videopath):
    frame_path = videopath.replace('Raw', 'Modified')
    trimmed_video_path = videopath.replace('Raw', 'Trimmed')
    best_frame_path = videopath.replace('Raw', 'Best')

    try:
        os.mkdir(frame_path)
        os.mkdir(trimmed_video_path)
        os.mkdir(best_frame_path)
    except FileExistsError:
        pass
    return frame_path, trimmed_video_path, best_frame_path


def splitVideo_intoFrames(filepath, frame_path):
    # -------------------------------------------------
    # Split Video into Frames
    # -------------------------------------------------
    _name = filepath.split("/")[-1]
    _name = _name.replace(".mp4", "")
    vidObj = cv2.VideoCapture(filepath)
    count = 0
    success = 1
    while success:
        try:
            success, image = vidObj.read()
            cv2.imwrite(frame_path+"/"+_name+"_frame%d.jpg" % count, image)
            count += 1
        except:
            pass





def show_frames(_filelocation):
    # -------------------------------------------------
    # View Frames
    # -------------------------------------------------

    try:

        df_frames = pd.DataFrame(columns=['image', 'path'])
        imglist = os.listdir(_filelocation)
        for _img in imglist:
            data = {'image': [_img], 'path': [_filelocation]}
            df_frames = pd.concat([df_frames, pd.DataFrame(data)])

        df_frames['image_path'] = df_frames['path'] + '/' + df_frames['image']
        _img_file = list(df_frames['image_path'].unique())

        img = image_select(
            label='Frames',
            images=_img_file,
            use_container_width=False
        )
        return img

    except:
        pass



def image_crop(image_file, centre):
    # -------------------------------------------------
    # Image Cropping
    # -------------------------------------------------
    width, height = image_file.size
    # Setting the points for cropped image
    if centre != 0:
        height_mid = centre
    else:
        height_mid = height / 2

    left = 0
    top = height_mid - height_mid / 1.7
    right = width
    bottom = height_mid + height_mid / 2

    return left, top, right, bottom, height_mid



def image_save(image_path, image_file):
    # -------------------------------------------------
    # Image Saving
    # -------------------------------------------------
    image_file.save(image_path)

def image_download(image_path, image_file):
    # -------------------------------------------------
    # Image Downloading
    # -------------------------------------------------
    buf = BytesIO()
    image_file.save(buf, format="JPEG")
    byte_im = buf.getvalue()
    return byte_im



def trimVideo(video_filename, start_sec, end_sec):
    # -------------------------------------------------
    # Trimming Video
    # -------------------------------------------------
    trimmed_filename = video_filename.replace('.mp4', '')+"_"+str(start_sec)+"-"+str(end_sec)+".mp4"
    trimmed_filename = trimmed_filename.replace('Raw', 'Trimmed')
    ffmpeg_extract_subclip(video_filename, start_sec, end_sec, targetname=trimmed_filename)
    print('Trimmed Successfully. Filename is ', trimmed_filename)



def text_to_ranges(_text):
    # -------------------------------------------------
    # Input Text to ranges for video trimming
    # -------------------------------------------------
    text_list = _text.replace(' ', '').split(';')
    int_list = []
    for _ranges in text_list:
        if _ranges != "":
            val = _ranges.split('-')
            int_list.append(val)
    st.write(int_list)
    return int_list




# -------------------------------------------------
# UI - Section 0 :
# -------------------------------------------------
# -------------------------------------------------
# Select Raw Video
# -------------------------------------------------


try:
    id, dt = set_up_emailid()
    base_path, base_path_date_id, base_path_date_id_raw = input_folder_initialise(id, dt)
    filename = upload_raw_video(base_path_date_id_raw)
    frame_path, trimmed_video_path, best_frame_path = target_folder_initialise(base_path_date_id_raw)
except:
    pass





# -------------------------------------------------
# UI - Section 1 :
# -------------------------------------------------


st.markdown(f'<p style="color:#ffc375;font-size:20px;border-radius:2%;"> A. View the Video </p>', unsafe_allow_html=True)


try:
    con_video = st.container(height=850)

    with con_video:

        video_file = open(filename, 'rb')
        video_bytes = video_file.read()

        vcol1, vcol2, vcol3 = st.columns(3)

        with vcol1:
            st.video(video_bytes)
        with vcol2:
            st.video(video_bytes)
            # st.empty()
        with vcol3:
            st.video(video_bytes)
            # st.empty()
except:
    pass



# -------------------------------------------------
# UI - Section 2 :
# -------------------------------------------------

st.markdown(f'<p style="color:#ffc375;font-size:20px;border-radius:2%;"> B. Choose the best video clips </p>', unsafe_allow_html=True)

try:
    video_trimming_text_input = st.text_input('Enter video ranges to trim in this format : 1-2 ; 4-5 ; 4-11;')
except:
    pass


st.markdown(f'<p style="color:#ffc375;font-size:20px;border-radius:2%;"> C. Split the best video clip into Frames </p>', unsafe_allow_html=True)

try:
    with st.form("TrimVideo"):
        trimmed = st.form_submit_button("Trim now")
        if trimmed:
            ranges_list = text_to_ranges(video_trimming_text_input)
            for r in ranges_list:
                try:
                    trimVideo(filename, int(r[0]), int(r[1]))
                except:
                    pass
            st.write('Video Trimming complete!')
except:
    pass

# -------------------------------------------------
# UI - Section 3 :
# -------------------------------------------------


st.markdown(f'<p style="color:#ffc375;font-size:20px;border-radius:2%;"> D. Choose the best frame and save it </p>', unsafe_allow_html=True)


try:
    trimmed_video_list = list(os.listdir(trimmed_video_path))

    trimmed_file_suffix_list = []
    for t in trimmed_video_list:
        t = t.replace(base_path_date_id, '')
        trimmed_file_suffix_list.append(t)

    selected_trimmed_video = st.selectbox(label='Select the trimmed video', options=trimmed_file_suffix_list)

    with st.form("FrameSplitting"):
        submitted = st.form_submit_button("Split now")
        if submitted:
            trimmed_video_filename_for_splitting = os.path.join(base_path_date_id, 'Trimmed', selected_trimmed_video)
            splitVideo_intoFrames(trimmed_video_filename_for_splitting, frame_path)
            st.write('Frame splitting complete!')

except:
    pass




# -------------------------------------------------
# UI - Section 4 :
# -------------------------------------------------
con_height = 950
con = st.container(height=con_height)

# -------------------------------------------------
# UI - Section 4A :
# -------------------------------------------------





with con:

    col1, col2 = st.columns(2)
    with col1:
        con1 = st.container(height=con_height)
        with con1:
            st.markdown("Frame Selection")

            try:
                img_pth = show_frames(frame_path)
            except:
                pass


    # -------------------------------------------------
    # UI - Section 4B :
    # -------------------------------------------------

    with col2:

        try:
            st.markdown("Selected frame")
            image = Image.open(img_pth)
            best_image_path = img_pth.replace('Modified', 'Best')
            centre = st.number_input('Update the center of image', min_value=0)
            left, top, right, bottom, height_mid = image_crop(image, centre)
            st.write('current centre for image is :' + str(height_mid))
            image = image.crop((left, top, right, bottom))
            st.image(image)

            download_name = best_image_path.split('/')[-1]

            c_save, c_download = st.columns(2)

            with c_save:
                # with st.form("SaveImage"):
                #     save_pressed = st.form_submit_button()
                save_button = st.button("Save Image")
                if save_button:
                    image_save(best_image_path, image)
                    st.write('Image was saved successfully!')

            with c_download:
                dwd_button = st.download_button(
                    label="Download Image",
                    data=image_download(best_image_path, image),
                    file_name=download_name,
                    mime="image/jpeg",
                )
                if dwd_button:
                    st.write('Image was download successfully!')

        except:
            pass
