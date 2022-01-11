from farbprinter.farbprinter import Farbprinter
import pandas as pd
import sys
import os
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import regex
from bs4 import BeautifulSoup
from time import sleep
from random import randrange
from functools import reduce
import pickle
from random import shuffle
drucker = Farbprinter()
subtltles_symlink = "symlinkfilm"
foldersymlink = "symlinkordner"



def read_pkl(filename):
    with open(filename, 'rb') as f:
        data_pickle = pickle.load(f)
    return data_pickle
levels={}
levels['a1_1']=read_pkl(r"C:\Users\Gamer\anaconda3\envs\subtitlesmerger\a1_1_regex.pkl")
levels['a1_2']=read_pkl(r"C:\Users\Gamer\anaconda3\envs\subtitlesmerger\a1_2_regex.pkl")
levels['a2_1']=read_pkl(r"C:\Users\Gamer\anaconda3\envs\subtitlesmerger\a2_1_regex.pkl")
levels['a2_2']=read_pkl(r"C:\Users\Gamer\anaconda3\envs\subtitlesmerger\a2_2_regex.pkl")
levels['b1_1']=read_pkl(r"C:\Users\Gamer\anaconda3\envs\subtitlesmerger\b1_1_regex.pkl")
levels['b1_2']=read_pkl(r"C:\Users\Gamer\anaconda3\envs\subtitlesmerger\b1_2_regex.pkl")
levels['b2_1']=read_pkl(r"C:\Users\Gamer\anaconda3\envs\subtitlesmerger\b2_1_regex.pkl")
levels['b2_2']=read_pkl(r"C:\Users\Gamer\anaconda3\envs\subtitlesmerger\b2_2_regex.pkl")


def secondsToStr(t):
    return "%02d:%02d:%02d.%03d" % \
        reduce(lambda ll,b : divmod(ll[0],b) + ll[1:],
            [(round(t*1000),),1000,60,60])

def read_srt_files(issubtitle, pfad):
    if issubtitle is False:
        return np.nan
    try:
        with open(pfad, mode="rb") as f:
            dateiohnehtml = f.read()
        dateiohnehtml = (
            b"""<!DOCTYPE html><html><body><p>"""
            + dateiohnehtml
            + b"""</p></body></html>"""
        )
        soup = BeautifulSoup(dateiohnehtml, "lxml")
        soup = str(soup)
        soup = soup.strip()
        soup = regex.sub(r'\s*<!DOCTYPE html>\s*<html>\s*<body>\s*<p>\s*', '', soup, regex.DOTALL)
        soup = regex.sub(r'\s*</p>\s*</body>\s*</html>\s*', '', soup, regex.DOTALL)
        if len(soup) < 100:
            return np.nan
        print(soup)
        return soup
    except:
        return np.nan


def delete_symlink(filename):
    try:
        os.remove(filename)
    except:
        pass

def datei_auswaehlen_mit_tkinter(show_message):
    # global subtltles_symlink
    print(
        drucker.f.black.brightyellow.italic(show_message)
    )
    Tk().withdraw()
    subtitles_file_input = askopenfilename()
    ausgabeordner = regex.sub(r"/[^/]+\.\w+$", "", subtitles_file_input)
    dateiendung = regex.findall(r"\.([^.\\/]+)$", subtitles_file_input)[0]
    subtltles_symlink2 = subtltles_symlink + "." + dateiendung

    delete_symlink(subtltles_symlink2)
    os.symlink(subtitles_file_input, subtltles_symlink2)
    delete_symlink(foldersymlink)
    os.symlink(ausgabeordner, foldersymlink)
    return subtitles_file_input, ausgabeordner, subtltles_symlink2

def transpose_list_of_lists(listexxx):
    try:
        return [list(xaaa) for xaaa in zip(*listexxx)]
    except Exception as Fehler:
        print(Fehler)
        try:
            return np.array(listexxx).T.tolist()
        except Exception as Fehler:
            print(Fehler)
            return listexxx

def calculate_time(zeit):
    return (
        zeit.time().hour * 3600
        + zeit.time().minute * 60
        + zeit.time().second
        + zeit.time().microsecond / 1000000
    )

def srttext_to_dataframe(f_srttext):
    try:
        gesplittetertext = regex.split(
            r"([\n\v\s\t\r]+?\d+?[\t\r\n\v\s]+?\d\d:\d\d:\d\d,\d+[^\n\v]+)",
            "\n\n" + f_srttext.lstrip(),
        )
        gesplittetertext = [x for x in gesplittetertext if len(x) > 0]
        text = []
        zeit = []
        for ini, texte in enumerate(gesplittetertext):
            if ini % 2 == 0:
                text.append(texte.strip())
            elif ini % 2 != 0:
                zeit.append(texte.strip())
        text = transpose_list_of_lists([regex.split("\n", x) for x in text])
        df = pd.DataFrame(list(zip(text[0], text[1], zeit)))
        df.columns = ["number", "keyframe", "text"]
        df["f_beginning"] = df.keyframe.str.extract(r"^(\d\d:\d\d:\d\d,\d+)")
        df["f_ending"] = df.keyframe.str.extract(
            r"^\d\d:\d\d:\d\d,\d+\s*--(?:(?:>)|(?:\s*&gt;))\s*(\d\d:\d\d:\d\d,\d+)"
        )

        df["f_beginning_seconds"] = df.f_beginning.astype("datetime64")
        df["f_beginning_seconds"] = df["f_beginning_seconds"].apply(calculate_time)

        df["f_ending_seconds"] = df.f_ending.astype("datetime64")
        df["f_ending_seconds"] = df["f_ending_seconds"].apply(calculate_time)

        return df.copy()
    except Exception as Fehler:
        print(Fehler)
        return np.nan


def touch(dateipfad, symlink, mitendung=True):
    dateipfadendung = dateipfad.split('.')[-1]
    os.close(os.open(dateipfad, os.O_CREAT))
    try:
        os.remove(symlink)
    except:
        pass
    if mitendung is True:
        symlink = symlink + '.' + dateipfadendung
    os.symlink(dateipfad, symlink)
    return symlink



def neuentextformatieren(text, listewoerter, wievielewoerterfehlen=2):
    shuffle(listewoerter)
    try:
        try:
            gelbertext = regex.findall(r'<font color="#ffff00"><i>(.*?)</i>', text, regex.DOTALL)[0]
        except Exception as Fehler:
            print(Fehler)
            return np.nan
        try:
            whitetext = regex.findall(r'<font color="#ffffff">(.*?)</font>', text, regex.DOTALL)[0]
        except Exception as Fehler:
            print(Fehler)
            return np.nan
        if yellow_or_whitetext == '1':
            if any(listewoerter):
                for indi,kleinertext in enumerate(listewoerter):
                    whitetext = whitetext.replace(kleinertext, f'_____ <font size="1">{kleinertext}</font>')
                    if indi==wievielewoerterfehlen:
                        break
        if yellow_or_whitetext == '2':
            if any(listewoerter):
                for indi,kleinertext in enumerate(listewoerter):
                    gelbertext = gelbertext.replace(kleinertext, f'_____ <font size="1">{kleinertext}</font>')
                    if indi==wievielewoerterfehlen:
                        break
        komplettertext = f'<font color="#ffff00"><i>{gelbertext}</i></font>\n<font color="#ffffff">{whitetext}</font>'
        return komplettertext

    except Exception as Fehler:
        print(Fehler)
        return np.nan

u_subtitles_file_input, u_subtitles_ausgabeordner, u_subtitles_symlink = datei_auswaehlen_mit_tkinter(show_message='Please select the subtitles you want to use to create the exercises')
u_video_file_input, v_video_ausgabeordner, v_video_symlink= datei_auswaehlen_mit_tkinter(show_message='Please select the corresponding movie')
df = pd.DataFrame([[u_subtitles_file_input, u_subtitles_ausgabeordner, u_subtitles_symlink, True], [u_video_file_input, v_video_ausgabeordner, v_video_symlink, False]], columns=['f_dos', 'f_folder', 'f_symlink', 'f_issubtitle'])
df["f_srttext"] = df.apply(
    lambda x: read_srt_files(x.f_issubtitle, x.f_symlink), axis=1
)
df["f_strdf"] = df.f_srttext.apply(srttext_to_dataframe)
textindataframe = df.loc[~df.f_strdf.isna()].f_strdf.iloc[0].copy()

while True:
    yellow_or_whitetext = input('Use\n' + drucker.f.black.brightwhite.normal('\n1) white text for exercises\n ') +  drucker.f.black.brightyellow.normal('\n2) yellow text for exercises\n\n'))
    yellow_or_whitetext = yellow_or_whitetext.strip()
    if yellow_or_whitetext == '1' or yellow_or_whitetext =='2':
        break

maxniveau = 'b1_1'
textindataframe['moeglicheaufgaben'] = ''
for indi,row in textindataframe.iterrows():
    alleergebnisse = []
    for niveau, reggi in levels.items():
        gefunden=reggi.findall(row.text)
        if any(gefunden):
            for wort in gefunden:
                alleergebnisse.append(wort)
        if niveau == maxniveau:
            break
    alleergebnisse = list(dict.fromkeys(alleergebnisse))
    alleergebnisse = [x for x in alleergebnisse if len(x) > 1]
    textindataframe.at[indi,'moeglicheaufgaben'] = alleergebnisse


abziehen = 0
anfangvomuntertitel=0
endevomuntertitel=0
indexneuesubs=1
nachwievielensekundenvideoschneiden = 100
stringschreiben=''
ffmpeg_anfangzeit = 0
durchnummeriert = 0
hinzufuegenamende=''
for indi, row in textindataframe.iterrows():

    anfangvomuntertitel = row.f_beginning_seconds - abziehen
    endevomuntertitel = row.f_ending_seconds - abziehen
    # if durchnummeriert !=-0:
    #     anfangvomuntertitel = anfangvomuntertitel
    #     endevomuntertitel = endevomuntertitel

    textfueruntertitel = str(row.text)
    stringschreiben = stringschreiben + str(indexneuesubs) + '\n' + secondsToStr(anfangvomuntertitel) + ' --> ' + secondsToStr(endevomuntertitel) + '\n' + textfueruntertitel + '\n\n'
    zeitwegmachen = secondsToStr(anfangvomuntertitel) + ' --> ' + secondsToStr(endevomuntertitel)
    letzteuhrzeit = secondsToStr(endevomuntertitel)
    indexneuesubs = indexneuesubs + 1
    if any(row.moeglicheaufgaben):
        if anfangvomuntertitel >= nachwievielensekundenvideoschneiden:

            print('------------------------------------------------------------------')
            abziehen = row.f_beginning_seconds
            hinzufuegenamende = row.text
            aufgabensatz = neuentextformatieren(row.text, row.moeglicheaufgaben)
            neuzeit = secondsToStr(anfangvomuntertitel) + ' --> ' + secondsToStr(endevomuntertitel).strip()
            stringschreiben = stringschreiben.replace(zeitwegmachen, '').strip()
            stringschreiben = stringschreiben + neuzeit
            stringschreiben = stringschreiben.replace(row.text, '').strip()
            stringschreiben = stringschreiben + '\n'+ aufgabensatz
            stringschreiben = regex.sub('\n+(\d\d?)\n+', '\n\n\g<1>\n', stringschreiben)
            print(stringschreiben)
            ffmpeg_endezeit = row.f_ending_seconds
            drucker.p.black.brightgreen.italic(ffmpeg_endezeit)

            indexneuesubs=1
            durchnummeriert = durchnummeriert+1
            v_video_ausgabeordner_symlinkvorbereitung = v_video_ausgabeordner + '/aufgaben'
            if not os.path.exists(v_video_ausgabeordner_symlinkvorbereitung):
                os.makedirs(v_video_ausgabeordner_symlinkvorbereitung)
            v_video_ausgabeordner_symlinkvorbereitung = v_video_ausgabeordner_symlinkvorbereitung + '/' + str(durchnummeriert).zfill(6) + '.avi'
            v_video_ausgabeordner_srt = regex.sub('\.avi$', '.srt', v_video_ausgabeordner_symlinkvorbereitung)
            stringschreiben = stringschreiben.replace(letzteuhrzeit, '23:00:00.999')
            with open(v_video_ausgabeordner_srt, mode='w', encoding='utf-8') as f:
                f.write(stringschreiben)
            stringschreiben = ''
            drucker.p.black.brightgreen.italic(stringschreiben)
            print(v_video_ausgabeordner_symlinkvorbereitung)
            symlinkvideoschreiben = touch(v_video_ausgabeordner_symlinkvorbereitung, f'tXeXmXpXvXiXdXeXo{str(durchnummeriert).zfill(6)}', mitendung=True)
            #os.system(f'''ffmpeg -y -ss {secondsToStr(ffmpeg_anfangzeit)} -to {secondsToStr(ffmpeg_endezeit+5)} -i "{v_video_symlink}" -c copy "{symlinkvideoschreiben}"''')
            os.system(f'''ffmpeg -y -ss {secondsToStr(ffmpeg_anfangzeit)} -to {secondsToStr(ffmpeg_endezeit+5)} -i "{v_video_symlink}" -c:v libx264 -preset ultrafast "{symlinkvideoschreiben}"''')

            symlinksrtkorrigieren ='symlinksrt.srt'
            delete_symlink(symlinksrtkorrigieren)
            os.symlink(v_video_ausgabeordner_srt, symlinksrtkorrigieren)
            # os.system(                fr"""ffs {v_video_symlink} -i {symlinksrtkorrigieren} -o {symlinksrtkorrigieren} --max-offset-seconds 60  --vad=auditok --gss"""            )
            #
            # os.system(                fr"""ffs {v_video_symlink} -i {symlinksrtkorrigieren} -o {symlinksrtkorrigieren} --max-offset-seconds 60 --gss"""            )
            try:
                os.remove(symlinkvideoschreiben)
            except Exception as Fehler:
                print(Fehler)
            try:
                os.remove(symlinksrtkorrigieren)
            except Exception as Fehler:
                print(Fehler)
            ffmpeg_anfangzeit = row.f_beginning_seconds



delete_symlink(v_video_symlink)
delete_symlink(u_subtitles_symlink)

# textindataframe['formatierte_aufgaben'] = textindataframe.apply(lambda x: neuentextformatieren(x.text, x.moeglicheaufgaben),axis=1)
# zaehler = 0
# anfangvomuntertitel = 0
# endevomuntertitel = 0
# schnittzeit_anfang=0
# abziehen = 0
# videoteil = 0
# untertitelschnitt =''
# indexneuesubs = 0
# for indi, row in textindataframe.iterrows():
#     anfangvomuntertitel = anfangvomuntertitel + row.f_beginning_seconds - abziehen
#     endevomuntertitel = endevomuntertitel +  row.f_ending_seconds - abziehen
#     drucker.p.brightred.black.bold(secondsToStr(anfangvomuntertitel))
#     drucker.p.brightblue.black.bold(secondsToStr(endevomuntertitel))
#     indexneuesubs = indexneuesubs+1
#     # print(indi)
#     # print(row)
#     untertitelschnitt = untertitelschnitt + str(indexneuesubs) + '\n' + secondsToStr(anfangvomuntertitel) + ' --> ' + secondsToStr(endevomuntertitel) + '\n' + row.text + '\n\n'
#
#     zaehler = zaehler +  row.f_ending_seconds -  row.f_beginning_seconds
#     if zaehler > 100:
#         endevomvideoschnitt  = secondsToStr(row.f_ending_seconds)
#         anfangvomvideoschnitt = secondsToStr(schnittzeit_anfang)
#         drucker.p.brightyellow.black.bold(endevomvideoschnitt)
#         schnittzeit_anfangffmpeg = schnittzeit_anfang - abziehen
#         schnittzeit_endeffmpeg = endevomvideoschnitt - abziehen
#         drucker.p.magenta.black.bold(anfangvomvideoschnitt)
#         zaehler = 0
#         anfangvomuntertitel = 0
#         endevomuntertitel = 0
#         # abziehen = row.f_ending_seconds
#         print(row)
#         drucker.p.black.brightred.italic(row.formatierte_aufgaben)
#         schnittzeit_anfang = row.f_beginning_seconds
#         ffmpegbefehl = rf'''ffmpeg.exe -y -i "{v_video_symlink}" -ss {schnittzeit_anfangffmpeg} -to {schnittzeit_endeffmpeg} -c:v libx264 -crf 30 "{str(videoteil).zfill(5)}"'''
#         videoteil = videoteil+ 1
#         untertitelschnitt = untertitelschnitt + str(indexneuesubs) + '\n' + secondsToStr(
#             anfangvomuntertitel) + ' --> ' + secondsToStr(endevomuntertitel) + '\n' + row.formatierte_aufgaben + '\n\n'
#         drucker.p.black.brightred.bold(ffmpegbefehl)
#         drucker.p.black.brightwhite.bold(untertitelschnitt)
#
#         abziehen = schnittzeit_anfang
#
#         untertitelschnitt = str(indexneuesubs) + '\n' + secondsToStr(
#             anfangvomuntertitel)+ ' --> ' + secondsToStr(endevomuntertitel) + '\n' + row.formatierte_aufgaben + '\n\n'
#         indexneuesubs = 1
#         continue
#     drucker.p.black.brightcyan.italic(row.text)





