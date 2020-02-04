# -------------------
# ----- Imports -----
# -------------------

from __future__ import unicode_literals, print_function
from prompt_toolkit import print_formatted_text as print, HTML

from os import system, get_terminal_size
from time import sleep
import youtube_dl as ytdl

from sys import exit
from struct import calcsize
from os.path import dirname, realpath, exists, join, splitext
from shutil import rmtree
from tqdm import tqdm
from requests import get
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from re import compile

from readchar import readkey

from tkinter import Tk
from tkinter.filedialog import askdirectory


# -------------------
# ----- Globals -----
# -------------------

# For FFMPEG #

# Evaluates to 64 for x64 architecture, and 32 for x86 architecture.
arch = calcsize("P") * 8

# We derive the architecture in order to then determine which version (32 or 64 bit) of FFMPEG we
# can download.
ffmpeg_filename = f"ffmpeg-latest-win{arch}-static.zip"
ffmpeg_dl_url = f"https://ffmpeg.zeranoe.com/builds/win{arch}/static/{ffmpeg_filename}"

# A global that stores the real directory pointing to the actual python file being run.
current_dir = dirname(realpath(__file__))

# A global that points to where ffmpeg should be if it was downloaded and extracted correctly.
ffmpeg_dir_path = join(current_dir, splitext(ffmpeg_filename)[0])

# Menu options:
# URL/s to MP3
# URL/s to MP4
# Custom CMD

menu_str = [
    "",
    '<b>`7MM"""Mq.                                                       <ansired>mm     db         </ansired></b>',  # noqa
    "<b>  MM   `MM.                                                      <ansired>MM                </ansired></b>",  # noqa
    '<b>  MM   ,M9`7MMpMMMb.  .gP"Ya`7MM  `7MM <ansired>`7MMpMMMb.pMMMb.  ,6"Yb.mmMMmm `7MM  ,p6"bo </ansired></b>',  # noqa
    "<b>  MMmmdM9   MM    MM ,M'   Yb MM    MM   <ansired>MM    MM    MM 8)   MM  MM     MM 6M'  OO </ansired></b>",  # noqa
    '<b>  MM        MM    MM 8M"""""" MM    MM   <ansired>MM    MM    MM  ,pm9MM  MM     MM 8M      </ansired></b>',  # noqa
    "<b>  MM        MM    MM YM.    , MM    MM   <ansired>MM    MM    MM 8M   MM  MM     MM YM.    ,</ansired></b>",  # noqa
    "<b>.JMML.    .JMML  JMML.`Mbmmd' `Mbod\"YML.<ansired>JMML  JMML  JMML`Moo9^Yo.`Mbmo.JMML.YMbmd' </ansired></b>",  # noqa
    "",
    "<ansiblue>Created by Brittank88 | Inspired by Mahlarian</ansiblue>",
    "",
    "╭──────────────────────────────────────────────────────╮",
    "│           URL >> MP3            URL >> MP4           │",
    "├───────────────\\/────────────────────\\/───────────────┤",
    "│            Press: 1              Press: 2            │",
    "╰──────────────────────────────────────────────────────╯",
    "          ⁞       <ansired>To quit, press Q / X</ansired>       ⁞          ",
    "          ╰──────────────────────────────────╯          ",
    "",
]

# -------------------
# ----- Classes -----
# -------------------


class Logger(object):
    def debug(self, msg):
        print(HTML(f"<ansibrightgreen>{msg.replace('&','&amp;')}</ansibrightgreen>"))

    def warning(self, msg):
        print(HTML(f"<ansiyellow>{msg.replace('&','&amp;')}</ansiyellow>"))

    def error(self, msg):
        print(HTML(f"<ansibrightred>{msg.replace('&','&amp;')}</ansibrightred>"))


# Create an intance of the logger.
logger = Logger()


# ---------------------
# ----- Functions -----
# ---------------------

# Little function to make formatted user input queries easier.
def input_formatted(msg):
    print(msg, end="")
    return input()


def dl_ffmpeg():
    # Checking if the directory exists already.
    if exists(ffmpeg_dir_path):
        logger.debug(f"{ffmpeg_filename} found. Skipping download.\n")
        # Exit the function - there's no point continuing here.
        return
    else:
        logger.warning(f"{ffmpeg_filename} is missing! Downloading & extracting...\n")

    # GET request to download the file, in the form of a memory stream we can iterate over.
    get_req = get(ffmpeg_dl_url, stream=True)

    # The request header tells us how big the file is, which we provide to tqdm to enable its
    # predictive features.
    total_size = int(get_req.headers["content-length"])

    # Create a bytearray object to store the bytes we are downloading in.
    zip_bytes = bytearray()

    # Creating the loading bar incremented manually as we iterate over byte chunks.
    dl_bar = tqdm(total=total_size, unit="iB", unit_scale=True)

    # Iterate through 32768 (32 * 1024) byte chunks at a time.
    for data in get_req.iter_content(32768):
        # Update the bar percentage.
        dl_bar.update(len(data))
        # Append the new bytes to our bytearray.
        zip_bytes.extend(data)

    # Parse our completed bytearray as a BytesIO (file-like) object, and extract / close.
    with ZipFile(BytesIO(zip_bytes), "r", ZIP_DEFLATED) as zfl:
        zfl.extractall(path=current_dir)
        zfl.close()

    # Close the loading bar instance.
    dl_bar.close()

    # We want to ensure we downloaded exactly as much as we anticipated
    # (content-length from the request header).
    if dl_bar.n != total_size:
        # Log the error to the console.
        logger.error(
            "\nSomething went wrong during the download process!\n"
            + f"Expected: {total_size}\n"
            + f"Actual: {dl_bar.n}\n\n"
            + "Please:\n"
            + f"> Download {ffmpeg_filename} from <u>{ffmpeg_dl_url}</u>."
            + f"> Extract {ffmpeg_filename} to the same folder as this application is located.\n"
        )
        # Delete the directory path, as the files are potentially malformed.
        rmtree(ffmpeg_dir_path)
        # Allow user to read message before exiting.
        input("Press any key to exit.")
        # Exit.
        exit(-1)


# Credits: http://granitosaurus.rocks/getting-terminal-size.html#making%20it%20work!
def get_cli_size(fallback=(80, 24)):
    for i in range(3):
        try:
            columns, rows = get_terminal_size(i)
        except OSError:
            continue
        break
    # Set default if the loop completes which means all failed.
    else:
        return fallback
    return columns, rows


def ytdl_hook(d):
    if d["status"] == "finished":
        logger.debug(
            "\nDownload complete! <b>Please wait for any conversions to finish</b>.\n"
        )


def download(opts):
    while True:
        # Clear screen.
        system("cls")

        # Get the URL from the user.
        url = input_formatted(
            HTML(
            """
            <b>Paste in your link and hit enter.</b>

            Playlists links are supported!
            Searching is also supported! Just prefix your query with:
                - <b>'ytsearch:'</b>, for <ansired>YouTube</ansired>
                - <b>'scsearch:'</b>, for <orange>Soundcloud</orange> (MP3 only!)

            <ansired>You can also exit back to the main menu using <b>'Q'</b> or <b>'X'</b>.</ansired>

            """  # noqa
            )
        )
        if url.upper() in ("Q", "X"):
            break

        # Set some opts that should always be set this way. #
        # Prefer FFMPEG.
        opts["prefer_ffmpeg"] = True
        # Points towards the FFMPEG we downloaded.
        opts["ffmpeg_location"] = join(ffmpeg_dir_path, "bin")
        # Restrict to safe filenames.
        opts["restrict_filenames"] = True
        # Sets our logger for any information from youtube-dl.
        opts["logger"] = logger
        # Sets our hook that is called whenever youtube-dl makes any progress downloading a file.
        opts["progress_hooks"] = [ytdl_hook]

        # Create a root Tkinter window that we will instantly hide.
        root = Tk()
        # Hide the window.
        root.withdraw()
        # Ask for a save directory.
        opts["outtmpl"] = join(
            askdirectory(mustexist=True, initialdir=current_dir), "%(title)s.%(ext)s"
        )
        # Destroy the hidden root window once we are done with it.
        root.destroy()

        with ytdl.YoutubeDL(opts) as ydl:
            try:
                print()
                ydl.download([url])
                break
            except ytdl.utils.DownloadError:
                # Wait a little so they can read the above.
                sleep(5)
                # Reset menu.
                continue


def url_mp3():
    download(
        {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }
    )


def url_mp4():
    download(
        {
            "format": "bestvideo+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
        }
    )


def close_program():
    system("cls")
    exit(0)


menu_functions = {"Q": close_program, "X": close_program, "1": url_mp3, "2": url_mp4}


def mainMenuLoop():
    while True:
        # Clear screen.
        system("cls")

        # Regex to match against content enclosed in '<>'.
        match_tags = compile(r"<.*?>")
        # Centre the multiline string line by line.
        for line in menu_str:
            # Calculate how much length in HTML-like tags we are to account for.
            remove_len = len("".join(match_tags.findall(line)))
            # Center the line, accounting for the length we just calculated.
            print(HTML(line.center(get_cli_size()[0] + remove_len)))

        try:
            # Little arrow that prefixes the CMD cursor.
            print("\t> ", end="")
            # Read the key, without requiring an enter press.
            usr_in = readkey()
            # Lookup the input in our dictionary and call the appropriate command if there is a
            # corresponding key.
            menu_functions[usr_in.upper()]()
        except KeyError:
            # Let the user know their input was invalid.
            input_quote = f" '{usr_in}'" if usr_in else ""
            print(
                HTML(
                    f"<ansired><b>Invalid input{input_quote}. Please try again.</b></ansired>\n"
                )
            )
            # Wait a little so they can read the above.
            sleep(2)
            # Reset menu.
            continue


# -----------------------
# ----- Driver Code -----
# -----------------------


if __name__ == "__main__":
    # Clear screen.
    system("cls")

    # Always check we have FFMPEG on startup.
    dl_ffmpeg()

    # Wait a second.
    sleep(1)

    # Display main menu and await input.
    # Automatically clears screen.
    mainMenuLoop()
