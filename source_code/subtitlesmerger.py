import subprocess

from scrapimdb import ImdbSpider
from farbprinter.farbprinter import Farbprinter
import pandas as pd
import sys
import os
import configparser
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import regex
from time import sleep
from random import randrange
from bs4 import BeautifulSoup
from einfuehrung import einfuehrung
import subliminal
import ffsubsync
cparser = configparser.ConfigParser()
drucker = Farbprinter()
filmsymlink = "symlinkfilm"
foldersymlink = "symlinkordner"


def create_empty_srt_files(name, f_dos, f_filename, f_issub, suffix):
    if f_issub is False:
        return np.nan
    neuerdateiname = (
        "\\".join(f_dos.split("\\")[:-1])
        + "\\"
        + regex.split("[\\/.]+", videodatei)[-2]
        + "."
        + str(name).zfill(5)
        + "_"
        + ".".join(f_filename.split(".")[1:-1])
        + "_"
        + suffix
        + ".srt"
    )
    os.close(os.open(neuerdateiname, os.O_CREAT))
    return neuerdateiname


def createsymlinkname(name, f_isfirst):
    try:
        if f_isfirst:
            return "0_" + str(name).zfill(6) + ".srt"
        if not f_isfirst:
            return "1_" + str(name).zfill(6) + ".srt"
    except:
        return np.nan


def subtitlesdefinieren(datei):
    if str(datei).endswith(".srt"):
        return True
    return False


def checken_ob_video_datei(pfad1, pfad2):
    pfad1 = pfad1.replace("\\", "/")
    pfad2 = pfad2.replace("\\", "/")
    if pfad1 == pfad2:
        return True
    return False


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


def first_or_second_subtitle(f_filename, f_issub):
    if f_issub is False:
        return np.nan
    neuersub = regex.sub("-[A-Z]{2}", "", f_filename)
    neuersub = neuersub.split(".")
    if neuersub[-2] == first_language_generell:
        return True
    if neuersub[-2] == second_language_generell:
        return False
    return np.nan


def getListOfFiles(dirName):
    listOfFile = os.listdir(dirName)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isdir(fullPath):
            pass
        else:
            allFiles.append(fullPath)
    alleinfos = [
        [
            str(x).replace("/", "\\"),
            str(x).split("\\")[-1],
            str(x).split("\\")[-1].split(".")[-1],
            x,
        ]
        for x in allFiles
    ]
    dateiendf = pd.DataFrame.from_records(alleinfos)
    dateiendf.columns = ["f_dos", "f_filename", "f_suffix", "f_pathv"]
    dateiendf["f_issub"] = dateiendf.f_filename.apply(subtitlesdefinieren)
    dateiendf["f_isvideo"] = dateiendf.f_dos.apply(
        lambda x: checken_ob_video_datei(x, videodatei)
    )
    dateiendf = pd.concat(
        [
            dateiendf.loc[dateiendf.f_issub == True].copy(),
            dateiendf.loc[dateiendf.f_isvideo == True].copy(),
        ]
    )
    dateiendf.reset_index(inplace=True, drop=True)
    dateiendf["f_isfirst"] = dateiendf.apply(
        lambda x: first_or_second_subtitle(x.f_filename, x.f_issub), axis=1
    )
    dateiendf["f_symlinksrt"] = dateiendf.apply(
        lambda x: createsymlinkname(x.name, x.f_isfirst), axis=1
    )
    for ind, row in dateiendf.iterrows():
        delete_symlink(row.f_symlinksrt)
        os.symlink(row.f_dos, row.f_symlinksrt)
    dateiendf["f_srt_with_audiotok"] = dateiendf.apply(
        lambda x: create_empty_srt_files(
            x.name, x.f_dos, x.f_filename, x.f_issub, "with_auditok"
        ),
        axis=1,
    )
    dateiendf["f_srt_without_audiotok"] = dateiendf.apply(
        lambda x: create_empty_srt_files(
            x.name, x.f_dos, x.f_filename, x.f_issub, "without_auditok"
        ),
        axis=1,
    )
    dateiendf["f_srt_without_audiotok_symlink"] = dateiendf.apply(
        lambda x: createsymlinkname(x.name, x.f_isfirst), axis=1
    )
    dateiendf["f_srt_without_audiotok_symlink"] = dateiendf[
        "f_srt_without_audiotok_symlink"
    ].str.replace("\.srt$", "_without.srt", regex=True)
    dateiendf["f_srt_with_audiotok_symlink"] = dateiendf.apply(
        lambda x: createsymlinkname(x.name, x.f_isfirst), axis=1
    )
    dateiendf["f_srt_with_audiotok_symlink"] = dateiendf[
        "f_srt_with_audiotok_symlink"
    ].str.replace("\.srt$", "_with.srt", regex=True)

    for ind, row in dateiendf.loc[dateiendf.f_issub == True].iterrows():
        delete_symlink(row.f_srt_without_audiotok_symlink)
        os.symlink(row.f_srt_without_audiotok, row.f_srt_without_audiotok_symlink)
        delete_symlink(row.f_srt_with_audiotok_symlink)
        os.symlink(row.f_srt_with_audiotok, row.f_srt_with_audiotok_symlink)

    return dateiendf


def sleeprandom():
    sleep(randrange(5, 50) / 10)


def delete_symlink(filename):
    try:
        os.remove(filename)
    except:
        pass


def datei_auswaehlen_mit_tkinter():
    global filmsymlink
    print(
        drucker.f.black.brightyellow.italic(
            "\n\nPlease tell me where your movie file is located!\nI will synchronize the audio and the subtitle!\nI will create several subtitle files using a variety of algorithms to have at least one great result!\nThe subtitle files I am going to create, \nwill be saved in the movie folder!\n\n"
        )
    )
    Tk().withdraw()
    videodatei = askopenfilename()
    ausgabeordner = regex.sub(r"/[^/]+\.\w+$", "", videodatei)
    dateiendung = regex.findall(r"\.([^.\\/]+)$", videodatei)[0]
    print(videodatei, ausgabeordner)
    filmsymlink = filmsymlink + "." + dateiendung

    delete_symlink(filmsymlink)
    os.symlink(videodatei, filmsymlink)
    delete_symlink(foldersymlink)
    os.symlink(ausgabeordner, foldersymlink)
    return videodatei, ausgabeordner


def get_filepath(filename):
    try:
        sprachensuchen = list(
            dict.fromkeys(
                [
                    x + "\\" + filename
                    for x in sys.path
                    if os.path.exists(x + "\\" + filename) and "/" not in x
                ]
            )
        )[0]
        print(sprachensuchen)
        return sprachensuchen
    except Exception as Fehler:
        print(Fehler)
        print(drucker.f.brightred.black.normal(f"{filename} not found"))


def get_language_variations(langname, languages, chosen_language):
    if chosen_language in languages:
        return chosen_language + "-" + langname
    return np.nan


def read_srt_files(isvideo, pfad):
    if isvideo is True:
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
        soup = soup.text
        soup = soup.strip()
        if len(soup) < 100:
            return np.nan
        print(soup)
        return soup
    except:
        return np.nan


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
            r"^\d\d:\d\d:\d\d,\d+\s*-->\s*(\d\d:\d\d:\d\d,\d+)"
        )

        df["f_beginning_seconds"] = df.f_beginning.astype("datetime64")
        df["f_beginning_seconds"] = df["f_beginning_seconds"].apply(calculate_time)

        df["f_ending_seconds"] = df.f_ending.astype("datetime64")
        df["f_ending_seconds"] = df["f_ending_seconds"].apply(calculate_time)

        return df.copy()
    except Exception as Fehler:
        print(Fehler)
        return np.nan


def save_all_final_subtitles(allesubtitlecombinations):
    for indimain, combi in enumerate(allesubtitlecombinations):
        firstversion = ""
        secondversion = ""
        for indi, row in combi.iterrows():
            index = str(row.number_de)
            time_1st = str(row.keyframe_de)
            time_2nd = str(row.keyframe_pt)
            text_1st_language = str(row.text_de)
            text_2nd_language = str(row.text_pt)
            if str(index) == '1':
                text_1st_language = text_1st_language + ' Subtitles Merger by www.queroestudaralemao.com.br '

            firstversion = (
                firstversion
                + str(index)
                + "\n"
                + time_1st
                + "\n"
                + '<font color="#ffff00"><i>'
                + text_1st_language.strip('''\'" "''')
                + "</i></font>"
                + "\n"
                + '<font color="#ffffff">'
                + text_2nd_language.strip('''\'" "''')
                + "</font>"
                + "\n\n"
            )
            secondversion = (
                secondversion
                + str(index)
                + "\n"
                + time_2nd
                + "\n"
                + '<font color="#ffffff">'
                + text_2nd_language.strip('''\'" "''')
                + "</font>"
                + "\n"
                + '<font color="#ffee00"><i>'
                + text_1st_language.strip('''\'" "''')
                + "</i></font>"
                + "\n\n"
            )
        save_first_srtfile = (
            ".".join(videodatei.split(".")[:-1])
            + "."
            + str(indimain).zfill(5)
            + "_v1"
            + ".srt"
        )
        save_second_srtfile = (
            ".".join(videodatei.split(".")[:-1])
            + "."
            + str(indimain).zfill(5)
            + "_v2"
            + ".srt"
        )

        with open(save_first_srtfile, mode="w", encoding="utf-8") as f:
            f.write(firstversion)
        with open(save_second_srtfile, mode="w", encoding="utf-8") as f:
            f.write(secondversion)

        simlinkfinalsub = "subtitlesfinal.srt"
        delete_symlink(simlinkfinalsub)
        try:
            os.symlink(save_first_srtfile, simlinkfinalsub)
        except:
            pass
        os.system(
            fr"""ffs {filmsymlink} -i subtitlesfinal.srt -o subtitlesfinal.srt --max-offset-seconds 300 --gss"""
        )

        delete_symlink(simlinkfinalsub)
        try:
            os.symlink(save_second_srtfile, simlinkfinalsub)
        except:
            pass
        os.system(
            fr"""ffs {filmsymlink} -i subtitlesfinal.srt -o subtitlesfinal.srt --max-offset-seconds 300 --gss"""
        )
        delete_symlink(simlinkfinalsub)


def delete_tempfiles(dateiendf, dirName):
    for key, row in dateiendf.iterrows():
        try:
            os.remove(row.f_srt_without_audiotok_symlink)
        except:
            pass
        try:
            os.remove(row.f_srt_with_audiotok_symlink)
        except:
            pass
        try:
            os.remove(row.f_symlinksrt)
        except:
            pass
        try:
            if row.f_dos.endswith(".srt"):
                try:
                    os.remove(row.f_dos)
                except:
                    pass
        except:
            pass
        listOfFile = os.listdir(dirName)
        allFiles = list()
        for entry in listOfFile:
            fullPath = os.path.join(dirName, entry)
            if os.path.isdir(fullPath):
                pass
            else:
                allFiles.append(fullPath)
        allFiles = [x for x in allFiles if ".srt" in x and "auditok" in x]
        for file in allFiles:
            try:
                os.remove(file)
            except:
                pass

einfuehrung(name='Subtitlesmerger')
inidatei = get_filepath("findsubtitles.ini")
cparser.read(inidatei)
addic7ed_password = cparser["DEFAULT"]["addic7ed_password"].strip(''' \n\t"''')
legendastv_password = cparser["DEFAULT"]["legendastv_password"].strip(''' \n\t"''')
opensubtitles_password = cparser["DEFAULT"]["opensubtitles_password"].strip(
    ''' \n\t"'''
)
username_auf_subtitles_plattformen = cparser["DEFAULT"]["opensubtitles_username"].strip(
    ''' \n\t"'''
)
username_auf_legendastv_plattformen = cparser["DEFAULT"]["legendastv_username"].strip(
    ''' \n\t"'''
)
username_auf_addic7ed_plattformen = cparser["DEFAULT"]["addic7ed_username"].strip(
    ''' \n\t"'''
)
gesuchterfilm = input(
    drucker.f.black.brightyellow.italic("\nWhat movie are you looking for?\n\nIf you are not yet registered on www.opensubtitles.org / www.legendas.tv / www.addic7ed.com , register first,\ncome back and write") + drucker.f.black.brightred.italic(" editconfig ") + drucker.f.black.brightyellow.italic("to edit the config file\n\n")
)

if gesuchterfilm.strip().lower() == 'editconfig':
    subprocess.Popen(['notepad.exe', inidatei], stdout=subprocess.PIPE)
    input('Please restart the app!')
    sys.exit()


gesuchterfilm = gesuchterfilm.strip('''\'" \n\t"''')
im = ImdbSpider(gesuchterfilm)
rating = im.get_rating()
originaltitle = im.get_original_title()
year = im.get_year()
ergebnis = {
    "Your search": gesuchterfilm,
    "Original title": originaltitle,
    "Rating": rating,
    "Year": year,
}

drucker.p_pandas_list_dict(ergebnis)
sprachendf = pd.read_pickle(get_filepath("sprachen.pkl"))
sprachendf = sprachendf[["label", "wmCode"]]
sprachendf.columns = ["language", "code"]
sprachendf.sort_values(by="language", inplace=True)
sprachendf.reset_index(inplace=True, drop=True)
drucker.p_pandas_list_dict(sprachendf)
first_language = input(drucker.f.brightcyan.black.normal("1st language code: "))
first_language = first_language.strip().lower()
first_language_generell = first_language
second_language = input(drucker.f.brightgreen.black.normal("2nd language code: "))
second_language = second_language.strip().lower()
second_language_generell = second_language

countriesdf = pd.read_pickle(get_filepath("countries.pkl"))
countriesdf["languagevariations"] = countriesdf.apply(
    lambda x: get_language_variations(x.name, x.languages, first_language), axis=1
)
language1_variations = countriesdf.loc[
    ~countriesdf.languagevariations.isna()
].languagevariations.to_list()
language1_variations.append(first_language)
drucker.p_pandas_list_dict(language1_variations)
first_language = input(
    drucker.f.black.red.normal(
        'I found some variations for the 1st language! Write the name of the variation as it is written (spelling!!) in the list!\nIf I don\'t find the variation, I will use the last language in the list (your choice) as a "backup"!'
    )
)
first_language = first_language.strip()

countriesdf["languagevariations"] = countriesdf.apply(
    lambda x: get_language_variations(x.name, x.languages, second_language), axis=1
)
language2_variations = countriesdf.loc[
    ~countriesdf.languagevariations.isna()
].languagevariations.to_list()
language2_variations.append(second_language)
drucker.p_pandas_list_dict(language2_variations)
second_language = input(
    drucker.f.black.red.bold(
        'I found some variations for the 2nd language! Write the name of the variation as it is written (spelling!!) in the list\nIf I don\'t find the variation, I will use the last language in the list (your choice) as a "backup"!'
    )
)
second_language = second_language.strip()
videodatei, ausgabeordner = datei_auswaehlen_mit_tkinter()

print(videodatei)
print(ausgabeordner)
print(filmsymlink)
print(foldersymlink)
print(first_language)
print(second_language)


name_vom_film_suchen = regex.sub(r"\s+", "_", ergebnis["Original title"]).strip(" _")
sprache = first_language
ausgabeordnersym = foldersymlink
runterladen = lambda: os.system(
    rf"""subliminal --addic7ed {username_auf_addic7ed_plattformen} {addic7ed_password} --legendastv {username_auf_legendastv_plattformen} {legendastv_password} --opensubtitles {username_auf_subtitles_plattformen} {opensubtitles_password}  --debug download {name_vom_film_suchen} -l {sprache} -d {ausgabeordnersym} -p opensubtitles -p legendastv -p podnapisi -p shooter -p thesubdb -p tvsubtitles"""
)
runterladen()
sleeprandom()
sprache = second_language
runterladen()
sleeprandom()
sprache = first_language_generell
runterladen()
sleeprandom()
sprache = second_language_generell
runterladen()
sleeprandom()
name_vom_film_suchen = regex.sub(r"\s+", "_", ergebnis["Your search"]).strip(" _")
sprache = first_language
runterladen()
sleeprandom()
sprache = second_language
runterladen()
sleeprandom()
sprache = first_language_generell
runterladen()
sleeprandom()
sprache = second_language_generell
runterladen()
sleeprandom()
dateiendf = getListOfFiles(ausgabeordner)

# split dataframe in first and second language

firstlanguagedf = dateiendf.loc[
    dateiendf.f_symlinksrt.str.contains("^0_.*", regex=True, na=False)
].copy()
firstlanguagedf = firstlanguagedf.loc[firstlanguagedf.f_issub == True]
secondlanguagedf = dateiendf.loc[
    dateiendf.f_symlinksrt.str.contains("^1_.*", regex=True, na=False)
].copy()
secondlanguagedf = secondlanguagedf.loc[secondlanguagedf.f_issub == True]


# synchronize first subtitles (--vad=auditok) for older movies
for ind, row in firstlanguagedf.iterrows():
    originalsrt = row.f_symlinksrt
    srt_without_audiotok_symlink = row.f_srt_without_audiotok_symlink
    srt_with_audiotok_symlink = row.f_srt_with_audiotok_symlink
    os.system(
        fr"""ffs {filmsymlink} -i {originalsrt} -o {srt_with_audiotok_symlink} --max-offset-seconds 300 --gss --vad=auditok"""
    )
    os.system(
        fr"""ffs {filmsymlink} -i {originalsrt} -o {srt_without_audiotok_symlink} --max-offset-seconds 300 --gss"""
    )


# synchronize 2nd subtitles with 1st subtitles (base)
ersteuntertitelohneaudiotok = firstlanguagedf.f_srt_without_audiotok_symlink.to_list()
ersteuntertitelmitaudiotok = firstlanguagedf.f_srt_with_audiotok_symlink.to_list()
for untertitel in ersteuntertitelohneaudiotok:
    for untertitel2leer, untertitel2_voll in zip(
        secondlanguagedf.f_srt_without_audiotok_symlink.to_list(),
        secondlanguagedf.f_symlinksrt,
    ):
        os.system(
            rf"""ffsubsync {untertitel} -i {untertitel2_voll} -o {untertitel2leer} --max-offset-seconds 300 --gss"""
        )
for untertitel in ersteuntertitelmitaudiotok:
    for untertitel2leer, untertitel2_voll in zip(
        secondlanguagedf.f_srt_with_audiotok_symlink.to_list(),
        secondlanguagedf.f_symlinksrt,
    ):
        os.system(
            rf"""ffsubsync {untertitel} -i {untertitel2_voll} -o {untertitel2leer} --max-offset-seconds 300 --vad=auditok --gss"""
        )


# readsubtitles
dateiendf["f_srttext"] = dateiendf.apply(
    lambda x: read_srt_files(x.f_isvideo, x.f_srt_with_audiotok_symlink), axis=1
)
dateiendf["f_strdf"] = dateiendf.f_srttext.apply(srttext_to_dataframe)

firstlanguage_ready_to_merge = dateiendf.loc[
    ~dateiendf.f_strdf.isna() & dateiendf.f_isfirst == True
]
secondlanguage_ready_to_merge = dateiendf.loc[
    ~dateiendf.f_strdf.isna() & dateiendf.f_isfirst == False
]

allesubtitlecombinations = []
for df1 in firstlanguage_ready_to_merge.f_strdf:
    print(df1)
    for df2 in secondlanguage_ready_to_merge.f_strdf.to_list():
        if str(df2).lower() != "nan":
            print(df2)
            df = pd.merge_asof(
                df1,
                df2,
                on="f_beginning_seconds",
                direction="nearest",
                tolerance=200,
                suffixes=("_de", "_pt"),
            ).copy()
            allesubtitlecombinations.append(df.copy())

save_all_final_subtitles(allesubtitlecombinations)
delete_tempfiles(dateiendf, ausgabeordner)



