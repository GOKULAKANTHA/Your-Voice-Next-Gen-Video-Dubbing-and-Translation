import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
import ffmpeg
import os
import time
from tkinter import filedialog
import subprocess
import tkinter as tk
import assemblyai as aai
import threading
from deep_translator import GoogleTranslator
import pysrt
import tempfile
from pysubparser import parser
from pydub import AudioSegment as adseg, silence
from pydub import effects
from gtts import gTTS
import gtts

video_path=""
langx=""
lns={}
tsmp={}

def restart_program():
    print("restart")
    
    cat0 = Image.open("assets/cat.jpg")
    cat0 = cat0.resize((500, 500))  # Resize the image if needed
    new_tk_image0 = ImageTk.PhotoImage(cat0)
    image_label1.configure(image=new_tk_image0)
    image_label1.image = new_tk_image0
    
    complete.place_forget()
    network_error.place_forget()
    restart_button.place_forget()
    image_label.place(relx=0.85, rely=0.3, anchor="e")
    language_dropdown.place(relx=0.89, rely=0.7, anchor="e")

def parse(path:str)-> None:
    start_time = time.time()
    with open(path,"rb",buffering=512) as srt:
        srtstr=srt.read()#.decode("utf-8")
        # print(srtstr)
        if b"\n\r\n" in srtstr:
            subsplit=b"\n\r\n"
        elif b"\n\n" in srtstr:
            subsplit=b"\n\n"
        # print(b"Subsplit: "+subsplit)
        for subline in srtstr.split(subsplit):
            part=subline.split(b"\n")
            if len(part)>=3:
                tsmp[int(part[0])]=part[1].decode("utf-8")
                ln=b""
                for x in part[2:]:
                    ln+=b" "
                    ln+=x
                    # ln+b""
                lns[int(part[0])]=ln.decode("utf-8")
            else:
                print(part)
                print("Bad SRT.")

    print("--- %s seconds ---" % (time.time() - start_time))

def ttsx(x):
    global langx
    tamil_text = lns[x]
    tamil_speech = gtts.gTTS(tamil_text, lang=langx)
    tamil_speech.save(os.path.join(sppath, str(x) + ".mp3"))
    
def getTime(st:str,idx:int)->int:
    a=st.split(" --> ")[idx]
    hh=int(a.split(":")[0])
    mm=int(a.split(":")[1])
    ss=int(a.split(":")[2].replace(",",""))
    # print(hh,mm,ss)
    totalmillisecs=hh*60*60*1000+mm*60*1000+ss
    return totalmillisecs

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}\n', end = printEnd)
    if iteration == total: 
        print()

def speed_change(sound, speed=1.0):
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
         "frame_rate": int(sound.frame_rate * speed)
      })
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

def compile():
    nl=len(lns.keys())
    print("Compilation started") 
    holder=adseg.empty()
    lastime=0
    printProgressBar(0, 100, prefix = 'Compiling:', suffix = 'Complete', length = 50)
    newtime=getTime(tsmp[1],0)
    slc=adseg.silent(newtime)
    # lastime=getTime(parsesrt.tsmp[i+1],1)
    holder=holder.append(slc, crossfade=0)
    for i in range(1,nl+1):
        crsfade=0
        # lastime=getTime(parsesrt.tsmp[i+1],1)
        startime=getTime(tsmp[i],0)
        endtime=getTime(tsmp[i],1)
        sublength=endtime-startime
        if not i+1>nl:
            nextime=getTime(tsmp[i+1],0)
        if i==nl:
            nextime=endtime
        midlength=nextime-endtime
        # compensate=midlength*0.25
        part=remove_trailing_silence(adseg.from_file(os.path.join(sppath,str(i)+".mp3")))
        # if (len(part) + len(holder))>endtime:
        if len(part) > sublength:
            new_speed=len(part)/(sublength)
            part=part.speedup(new_speed,150,0)
        
        holder=holder.append(part, crossfade=crsfade)
        diff = nextime-len(holder)
        # blanktrack=nextime-endtime
        slc=adseg.silent(diff)
        holder=holder.append(slc, crossfade=crsfade)
        # compensate=(lastime-newtime)-len(part)
        # lastime-=compensate
        printProgressBar(i, nl, prefix = 'Compiling:', suffix = 'Complete', length = 50)

    holder.export("output.wav", format="wav")
    print("compilation finished")
# # for key in parsesrt.tsmp.keys():
# #     part=adseg.from_file(os.path.join(sppath,str(key)+".wav"))
# #     holder=holder.append(part)

def remove_trailing_silence(sound):
    endtrim=silence.detect_leading_silence(sound.reverse())
    return sound[:len(sound)-endtrim]

def time_to_ms(time):
    return (time.hour * 3600 + time.minute * 60 + time.second) * 1000 + time.microsecond / 1000

def generate_audio(path):
    translation.place_forget()
    ttss.place(relx=0.93, rely=0.35, anchor="e")
    srtpath=path
    global sppath
    sppath="speech1"
    threads=[]
    parse(srtpath)
    if not os.path.exists(sppath):
        os.makedirs(sppath)
    print("TTS started")
    start_time = time.time()
    nl=len(lns.keys())

    printProgressBar(0, 100, prefix = 'TTS:', suffix = 'Converted', length = 50)
    for key in lns.keys():
        # print(key)
        ttsx(key) #--SKIP FOR TESTING
        printProgressBar(key, nl, prefix = 'TTS:', suffix = 'Converted', length = 50)

    print("tts finished")

    print("TTS converted in %s seconds " % (time.time() - start_time))

    start_time = time.time()

    compile()

    print("Compiled in %s seconds " % (time.time() - start_time))
    print("complete")
    if os.path.exists("video_with_newAudio.mp4"):
        os.remove("video_with_newAudio.mp4")
    global video_path
    # Input and output file paths
    #video_input = video_path
    video_input = 'testsample.mp4'
    audio_input = 'output.wav'
    subtitle_input = 'subtitles1.srt'
    output_file = 'video_with_newAudio.mp4'


    # FFmpeg command with subtitles
    ffmpeg_command = [
        'ffmpeg',
        '-i', video_input,
        '-i', audio_input,
        '-i', subtitle_input,
        '-map', '0:0',
        '-map', '1:0',
        '-map', '2:0',
        '-c:v', 'copy',
        '-c:a', 'libmp3lame', '-q:a', '1',
        '-c:s', 'mov_text',  # Subtitle codec
        '-shortest',
        output_file
    ]

    # Run FFmpeg command
 
    subprocess.Popen(ffmpeg_command, creationflags=subprocess.CREATE_NO_WINDOW)
    print("finished")
    ttss.place_forget()
    complete.place(relx=0.93, rely=0.35, anchor="e")
    
    cat5 = Image.open("assets/cat5.jpg")
    cat5 = cat5.resize((500, 500))  # Resize the image if needed
    new_tk_image5 = ImageTk.PhotoImage(cat5)
    image_label1.configure(image=new_tk_image5)
    image_label1.image = new_tk_image5
    
    language_dropdown.place_forget()
    restart_button.place(relx=0.85, rely=0.7, anchor="e")

    
def on_enter(event):
    upload_image_hover = Image.open("assets/uploadover.jpg")
    upload_image_hover = upload_image_hover.resize((300, 300))  # Resize the image if needed
    upload_image_tk_hover = ImageTk.PhotoImage(upload_image_hover)
    image_label.configure(image=upload_image_tk_hover)
    image_label.image = upload_image_tk_hover

def on_leave(event):
    image_label.configure(image=upload_image_tk)
    image_label.image = upload_image_tk

def format_time(time):
    return f"{time.hours:02d}:{time.minutes:02d}:{time.seconds:02d},{time.milliseconds:03d}"

def translate_subtitle(input_file, output_file, target_language):
    cat4 = Image.open("assets/cat4.jpg")
    cat4 = cat4.resize((500, 500))  # Resize the image if needed
    new_tk_image4 = ImageTk.PhotoImage(cat4)
    image_label1.configure(image=new_tk_image4)
    image_label1.image = new_tk_image4
    # Load the English subtitle file
    subs = pysrt.open(input_file)
    print("1")
    # Initialize an empty list to store translated subtitles
    translated_subs = []
    print("2")
    transcription_complete.place_forget()
    translating.place(relx=0.93, rely=0.35, anchor="e")
    # Translate each subtitle and append to the list
    for sub in subs:
        translated_text = GoogleTranslator(source='auto', target=target_language).translate(sub.text)
        translated_subs.append(pysrt.SubRipItem(index=sub.index, start=sub.start, end=sub.end, text=translated_text))
    print("3")
    # Save the translated subtitles to a new SRT file
    with open(output_file, 'w', encoding='utf-8') as f:
        for sub in translated_subs:
            f.write(str(sub.index) + '\n')
            f.write(f"{format_time(sub.start)} --> {format_time(sub.end)}\n")
            f.write(sub.text + '\n\n')
    print("4")
    translating.place_forget()
    translation.place(relx=0.90, rely=0.35, anchor="e")
    # Now, run another Python file
    subtitle_file_path = "test1.srt"
    if os.path.exists("temp.mp3"):
        os.remove("temp.mp3")
    if os.path.exists("output.wav"):
        os.remove("output.wav")    
    generate_audio(path=subtitle_file_path)


    
def api_call():
    try:
        aai.settings.api_key = "7d19c17c68104072bca45aa788bb7d67"
        print("HI")
        # Check if subtitles1.srt exists and delete it
        if os.path.exists("subtitles1.srt"):
            os.remove("subtitles1.srt")

        transcript = aai.Transcriber().transcribe("audio.wav")

        subtitles = transcript.export_subtitles_srt()
        # subtitles = transcript.export_subtitles_srt(chars_per_caption=100)

        f = open("subtitles1.srt", "a")
        f.write(subtitles)
        f.close()
        audio_extracted.place_forget()
        transcription_complete.place(relx=0.90, rely=0.35, anchor="e")
        print("hi")
        flag=1
        
    except Exception as e:
        flag=0
        #print(f"Error: {e}")
        audio_extracted.place_forget() 
        network_error.place(relx=0.93, rely=0.35, anchor="e")
        language_dropdown.place_forget()
        restart_button.place(relx=0.85, rely=0.7, anchor="e")

  
        cat2 = Image.open("assets/cat2.jpg")
        cat2 = cat2.resize((500, 500))  # Resize the image if needed
        new_tk_image2 = ImageTk.PhotoImage(cat2)
        image_label1.configure(image=new_tk_image2)
        image_label1.image = new_tk_image2
        
    if flag==1:
        input_file = 'subtitles1.srt'
        if os.path.exists("test1.srt"):
            os.remove("test1.srt")
        output_file = 'test1.srt'
        global langx
        target_language = langx  # 'ta' for Tamil, 'hi' for Hindi, 'te' for Telugu, etc.

        # Translate the subtitle file and save as SRT
        translate_subtitle(input_file, output_file, target_language)
        
def extract_audio_from_video():
    def select_video_file():
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        image_label.place_forget()
        selected_language = language_var.get()
        lang_unicode = lang_mapping.get(selected_language, "")
        global langx
        langx = lang_unicode
        
        #selectvideo
        select_video.place(relx=0.93, rely=0.35, anchor="e")
        cat1 = Image.open("assets/cat1.jpg")
        cat1 = cat1.resize((500, 500))  # Resize the image if needed
        new_tk_image1 = ImageTk.PhotoImage(cat1)
        image_label1.configure(image=new_tk_image1)
        image_label1.image = new_tk_image1

        # Ask the user to select a video file
        video_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4;*.avi;*.mkv;*.mov"), ("All files", "*.*")]
        )

        return video_path
    global video_path
    video_path = select_video_file()

    if not video_path:
        print("No video file selected. Exiting.")
        select_video.place_forget()
        image_label.place(relx=0.85, rely=0.3, anchor="e")
        
        cat0 = Image.open("assets/cat.jpg")
        cat0 = cat0.resize((500, 500))  # Resize the image if needed
        new_tk_image0 = ImageTk.PhotoImage(cat0)
        image_label1.configure(image=new_tk_image0)
        image_label1.image = new_tk_image0
        
        return
    
    select_video.place_forget()

    #extract_audio
    extract_audio.place(relx=0.93, rely=0.35, anchor="e")

    cat3 = Image.open("assets/cat3.jpg")
    cat3 = cat3.resize((500, 500))  # Resize the image if needed
    new_tk_image3 = ImageTk.PhotoImage(cat3)
    image_label1.configure(image=new_tk_image3)
    image_label1.image = new_tk_image3

    audio_path = 'audio.wav'

    # Check if the audio file already exists and delete it
    if os.path.exists(audio_path):
        os.remove(audio_path)
        print(f"Deleted existing {audio_path}")

    # Extract audio from video using ffmpeg
    cmd = f'ffmpeg -i "{video_path}" -vn -acodec pcm_s16le -ar 44100 -ac 2 "{audio_path}"'
    subprocess.run(cmd, shell=True, check=True)

    extract_audio.place_forget()
    #audio_extracted
    audio_extracted.place(relx=0.93, rely=0.35, anchor="e")
    print(f"Audio extraction completed. Audio file saved at {audio_path}")
    api_thread = threading.Thread(target=api_call)
    api_thread.start()
    
    
# Create the main window
window = tk.Tk()

# Set the window title
window.title("YOUR VOICE")

# Get the screen width and height
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Set the window size to fill the screen
window.geometry(f"{screen_width}x{screen_height}+0+0")

# Set the window state to maximized
window.state('zoomed')

# Add a border to the top and left sides
window.configure(highlightthickness=20, highlightcolor="#6437a0")

# Choose a specific font style (e.g., Arial, bold) for "YOUR VOICE"
voice_font = font.Font(family="Comic Sans MS", size=80, weight="bold")

# Set background color for the window
window.configure(bg="#171717")

# Create a label for "YOUR VOICE" with increased font size, bold, specific font style, and color
label_voice = tk.Label(window, text="YOUR VOICE", font=voice_font, fg="#ffffff", bg="#171717")

# Pack the "YOUR VOICE" label into the window with reduced top padding
label_voice.pack(padx=40, pady=(100, 0), anchor="w")

# Choose a specific font style for "NEXT GEN"
next_gen_font = font.Font(family="Comic Sans MS", size=40)

#fontg

fontg = font.Font(family="Courier New", size=30)
# Create a label for "NEXT GEN" with smaller font size and blue color
label_next_gen = tk.Label(window, text="NEXT-GEN DUBBING STUDIO", font=next_gen_font, fg="#6437a0", bg="#171717")

# Pack the "NEXT GEN" label into the window with left padding
label_next_gen.pack(padx=40, pady=0, anchor="w")

# Load a JPEG image using Pillow
image = Image.open("assets/cat.jpg")
image = image.resize((500, 500))  # Resize the image if needed

# Convert the Pillow image to a Tkinter PhotoImage
tk_image = ImageTk.PhotoImage(image)

# Create a label to display the image
image_label1 = tk.Label(window, image=tk_image, bg="#171717")

# Pack the image label below the "NEXT-GEN DUBBING STUDIO" label
image_label1.pack(padx=(175, 0), pady=(0, 50), anchor="w")

# Load a new image for "UPLOAD"
upload_image = Image.open("assets/upload.jpg")
upload_image = upload_image.resize((300, 300))  # Resize the image if needed

# Convert the Pillow image to a Tkinter PhotoImage
upload_image_tk = ImageTk.PhotoImage(upload_image)

# Create a label for the image, and bind it to the click event
image_label = tk.Label(window, image=upload_image_tk, bg="#171717")
image_label.image = upload_image_tk  # Keep a reference to the image to prevent it from being garbage collected
image_label.bind("<Button-1>", lambda event: extract_audio_from_video())
image_label.bind("<Enter>", on_enter)
image_label.bind("<Leave>", on_leave)

# Create a label for "Uploading" initially hidden
select_video = tk.Label(window, text="Select Your Video 🔍", font=fontg, fg="#ffffff", bg="#171717")
select_video.place_forget()

extract_audio = tk.Label(window, text="Extracting Audio...👨‍🔧", font=fontg, fg="#ffffff", bg="#171717")
extract_audio.place_forget()

audio_extracted = tk.Label(window, text="Transcripting...⛏️", font=fontg, fg="#ffffff", bg="#171717")
audio_extracted.place_forget()

transcription_complete = tk.Label(window, text="Transcription\nComplete!!!", font=fontg, fg="#ffffff", bg="#171717")
transcription_complete.place_forget()

network_error = tk.Label(window, text="☠️ Network Issue ☠️\nCheck Your Connection", font=fontg, fg="#ffffff", bg="#171717")
network_error.place_forget()

translating = tk.Label(window, text="Translating...🈵", font=fontg, fg="#ffffff", bg="#171717")
translating.place_forget()

translation = tk.Label(window, text="Translation\n Complete!!!", font=fontg, fg="#ffffff", bg="#171717")
translation.place_forget()

ttss = tk.Label(window, text="TTS processing 💬->🗣", font=fontg, fg="#ffffff", bg="#171717")
ttss.place_forget()

complete = tk.Label(window, text="Completed 💯🥳  ", font=fontg, fg="#ffffff", bg="#171717")
complete.place_forget()


# Place the image label in the same position as the button
image_label.place(relx=0.85, rely=0.3, anchor="e")

fontl = font.Font(family="Arial", size=40)
restart_button = tk.Button(window, text="Restart", font=fontl, fg="#ffffff", bg="#171717", command=restart_program)
#restart_button.place(relx=0.89, rely=0.7, anchor="e")
restart_button.place_forget()
# Language selection options
languages = ["Chinese", "French", "Hindi", "Japanese", "Kannada", "Korean", "Malayalam", "Russian", "Tamil", "Telugu"]

# Create a StringVar to store the selected language
language_var = tk.StringVar(window)

# Set the default language
language_var.set("Tamil")  # Default

# Create the language selection dropdown
language_dropdown = tk.OptionMenu(window, language_var, *languages)
language_dropdown.config(font=fontl, bg="#171717", fg="#ffffff", width=10)
language_dropdown["menu"].config(bg="#171717", fg="#ffffff")

# Place the language dropdown in the window
language_dropdown.place(relx=0.89, rely=0.7, anchor="e")
lang_mapping = {
    "Chinese": "zh-CN",
    "French": "fr",
    "Hindi": "hi",
    "Japanese": "ja",
    "Kannada": "kn",
    "Korean": "ko",
    "Malayalam": "ml",
    "Russian": "ru",
    "Tamil": "ta",
    "Telugu": "te",
}


# Run the Tkinter event loop
window.mainloop()
