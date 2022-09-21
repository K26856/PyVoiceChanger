# -*- coding:utf-8 -*-

from tkinter import *
from tkinter import ttk
import pyaudio
from threading import Thread
import pyworld as pw
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt

# 固定値
SAMPLE_RATE = 44100
BUFFER_SIZE = 220 * 150

# PyAudioで使うグローバル変数
p = pyaudio.PyAudio()
play_device_list = []
record_device_list = []
play_device_index = 0
record_device_index = 1
audio_stream = None

# GUIパーツ関連
main_window = None
frame = None
record_device_selector_selected = None
record_device_label = None
record_device_selector = None
play_device_selector_selected = None
play_device_label = None
play_device_selector = None
volum_slider_label_value= None
volum_slider_label = None
volum_slider_value = None
volum_slider = None
pitch_slider_label_value= None
pitch_slider_label = None
pitch_slider_value = None
pitch_slider = None
forum_slider_label_value= None
forum_slider_label = None
forum_slider_value = None
forum_slider = None

# オーディオデバイスリストを取得して、再生と録音に振り分ける
def get_audio_device_list() :
    global p
    global play_device_list
    global record_device_list
    global play_device_index
    global record_device_index
    for index in range(0, p.get_device_count()) :
        tmp = p.get_device_info_by_index(index)
        print(tmp)
        if tmp['maxInputChannels'] > 0 :
            record_device_list.append(str(index) + ':' + str(tmp['name']))
        elif tmp['maxOutputChannels'] > 0 :
            play_device_list.append(str(index) + ':' + str(tmp['name']))
    play_device_index = int(play_device_list[0][0])
    record_device_index = int(record_device_list[0][0])

# 録音デバイスのStream処理
def open_audio_stream(play_device_index, record_device_index) :
    global audio_stream
    close_audio_stream()
    print('open audio device : ' + str(play_device_index) + ', ' + str(record_device_index))
    audio_stream = p.open(
        format = pyaudio.paInt16,
        rate = SAMPLE_RATE,
        channels = 1,
        input_device_index = record_device_index,
        input = True,
        output_device_index = play_device_index,
        output = True,
        frames_per_buffer = BUFFER_SIZE,
        stream_callback = callback_signal_processing
    )
    return

def close_audio_stream() :
    global audio_stream
    if audio_stream != None :
        try :
            print('close record device')
            audio_stream.stop_stream()
            audio_stream.close()
            audio_stream = None
        except Exception as e:
            print(e)
            audio_stream.close()
            audio_stream = None
    return

def callback_signal_processing(in_data, frame_count, time_info, status) :
    try :
        record_data = np.frombuffer(in_data, dtype=np.int16).astype(np.float64) 

        # f0 基本周波数, sp スペクトル包絡, ap 非周期性指標
        _f0, t = pw.dio(record_data, SAMPLE_RATE)
        f0 = pw.stonemask(record_data, _f0, t, SAMPLE_RATE)
        sp = pw.cheaptrick(record_data, f0, t, SAMPLE_RATE)
        ap = pw.d4c(record_data, f0, t, SAMPLE_RATE)
        
        # 各パラメータの調整
        modified_f0 = f0 * pitch_slider_value.get()
        modified_sp = sp * forum_slider_value.get()
        modified_ap = ap * 1.0
    
        # アウトプット
        processed_data = pw.synthesize(modified_f0, modified_sp, modified_ap, SAMPLE_RATE)
        processed_data = processed_data * volum_slider_value.get()
        out_data = processed_data.astype(np.int16).tobytes()

        # データ確認用
        # print('f0 : ' + str(f0) + ',   sp : ' + str(sp) + ',   ap : ' + str(ap))
        # print(str(f0.shape) + ', ' + str(sp.shape) + ', ' + str(ap.shape))
        # plt.imshow(sp, cmap=plt.cm.jet, interpolation='nearest')
        # plt.plot()
        # plt.pause(0.01)
        #plt.cla()
        return (out_data, pyaudio.paContinue)
    except Exception as e:
        print(e)
        return (None, pyaudio.paContinue)


# GUI操作のイベント処理
def change_record_device(change_event) :
    global record_device_selector_selected
    global record_device_index
    global play_device_index
    record_device_index = int(record_device_selector_selected.get().split(':')[0])
    open_audio_stream(play_device_index, record_device_index)

def change_play_device(change_event) :
    global play_device_selector_selected
    global play_device_index
    global record_device_index
    play_device_index = int(play_device_selector_selected.get().split(':')[0])
    open_audio_stream(play_device_index, record_device_index)

def change_volum_slider(change_event) :
    global volum_slider_label_value
    global volum_slider_label
    global volum_slider_value
    global volum_slider
    volum_slider_label_value.set('音量(' + str(round(volum_slider_value.get(),2)) + ')')

def change_pitch_slider(change_event) :
    global pitch_slider_label_value
    global pitch_slider_label
    global pitch_slider_value
    global pitch_slider
    pitch_slider_label_value.set('ピッチ(' + str(round(pitch_slider_value.get(),2)) + ')')

def change_forum_slider(change_event) :
    global forum_slider_label_value
    global forum_slider_label
    global forum_slider_value
    global forum_slider
    forum_slider_label_value.set('フォルマント補正(' + str(round(forum_slider_value.get(),2)) + ')')

def close_window() :
    global main_window
    global p
    p.terminate()
    main_window.quit()

def init_gui() :
    global main_window
    global frame
    global record_device_selector_selected
    global record_device_label
    global record_device_selector
    global play_device_selector_selected
    global play_device_label
    global play_device_selector
    global volum_slider_label_value
    global volum_slider_label
    global volum_slider_value
    global volum_slider
    global pitch_slider_label_value
    global pitch_slider_label
    global pitch_slider_value
    global pitch_slider
    global forum_slider_label_value
    global forum_slider_label
    global forum_slider_value
    global forum_slider

    # オーディオデバイスの取得処理
    get_audio_device_list()
    open_audio_stream(play_device_index, record_device_index)

    # ウィンドウ作成
    main_window = Tk()
    main_window.title('voice changer')
    main_window.protocol('WM_DELETE_WINDOW', close_window)
    frame = ttk.Frame(main_window, padding=10)
    frame.grid()

    # 録音デバイス選択リスト作成
    record_device_selector_selected = StringVar()
    record_device_label = ttk.Label(
        frame,
        text='録音デバイス',
        foreground='#000000',
        padding=(5, 10),
        width=20,
        anchor=E
        )
    record_device_label.grid(row=0, column=0, sticky=E)
    record_device_selector = ttk.Combobox(
        frame, 
        textvariable=record_device_selector_selected, 
        values=record_device_list,
        width=75
        )
    record_device_selector.bind('<<ComboboxSelected>>', change_record_device)
    record_device_selector.set(record_device_list[0])
    record_device_selector.grid(row=0, column=1, sticky=W)

    # 再生デバイス選択リスト作成
    play_device_selector_selected = StringVar()
    play_device_label = ttk.Label(
        frame,
        text='再生デバイス',
        foreground='#000000',
        padding=(5, 10),
        width=20,
        anchor=E
        )
    play_device_label.grid(row=1, column=0, sticky=E)
    play_device_selector = ttk.Combobox(
        frame, 
        textvariable=play_device_selector_selected, 
        values=play_device_list, 
        width=75
        )
    play_device_selector.bind('<<ComboboxSelected>>', change_play_device)
    play_device_selector.set(play_device_list[0])
    play_device_selector.grid(row=1, column=1, sticky=W)

    # 音量スライダー
    volum_slider_label_value = StringVar()
    volum_slider_value = DoubleVar()
    volum_slider_label = ttk.Label(
        frame,
        textvariable=volum_slider_label_value,
        foreground='#000000',
        padding=(5, 10)
    )
    volum_slider_label_value.set('音量(1.0)')
    volum_slider_label.grid(row=2, column=0, sticky=E)
    volum_slider = ttk.Scale(
        frame,
        variable=volum_slider_value,
        from_=0.4,
        to=2.5,
        length=200,
        command=change_volum_slider
        )
    volum_slider.set(1.0)
    volum_slider.grid(row=2, column=1, sticky=W)

    # ピッチスライダー
    pitch_slider_label_value = StringVar()
    pitch_slider_value = DoubleVar()
    pitch_slider_label = ttk.Label(
        frame,
        textvariable=pitch_slider_label_value,
        foreground='#000000',
        padding=(5, 10)
    )
    pitch_slider_label_value.set('ピッチ(1.0)')
    pitch_slider_label.grid(row=3, column=0, sticky=E)
    pitch_slider = ttk.Scale(
        frame,
        variable=pitch_slider_value,
        from_=0.4,
        to=2.5,
        length=200,
        command=change_pitch_slider
        )
    pitch_slider.set(1.0)
    pitch_slider.grid(row=3, column=1, sticky=W)

    # フォルマントスライダー
    forum_slider_label_value = StringVar()
    forum_slider_value = DoubleVar()
    forum_slider_label = ttk.Label(
        frame,
        textvariable=forum_slider_label_value,
        foreground='#000000',
        padding=(5, 10)
    )
    forum_slider_label_value.set('フォルマント補正(1.0)')
    forum_slider_label.grid(row=4, column=0, sticky=E)
    forum_slider = ttk.Scale(
        frame,
        variable=forum_slider_value,
        from_=0.4,
        to=2.5,
        length=200,
        command=change_forum_slider
        )
    forum_slider.set(1.0)
    forum_slider.grid(row=4, column=1, sticky=W)


if __name__ == '__main__' :
    # GUI初期化
    init_gui()

    # GUIループ処理
    main_window.mainloop()

