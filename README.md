# Original code
The starting point of this project was the code from https://github.com/Holzhaus/serato-tags

# Disclaimer
This software is provided “as is” without any warranties or guarantees of any kind. **By using this software, you acknowledge that you do so at your own risk.** 
I strongly recommend backing up your files before using it, as I am not responsible for any loss or corruption of data. While I have tested this tool, 
it is primarily developed for personal use, and certain scenarios may not have been thoroughly tested.

# How to use
1. Make sure you have Python 3.11 installed on your computer
2. Export the rekordbox.xml file from Rekordbox
3. Rename the `.env.dist` file to `.env`
4. Edit the `.env` file and the `RB_XML` directive to the place where your Rekordbox XML file is located (for Windows make sure it's the full path)
   * For Windows make sure it's the full path
   * For MacOS you can either use the full path or user the `~` sign to replace the `/Users/<your_username>` from the path
5. **MAKE A BACKUP OF YOUR MUSIC FILES**
6. Analyze your files in Serato and add the beatgrid marker labeled 1 at the same position as in Rekordbox
7. Run `make install`
8. Run `make`

#### If using Windows
In this case the `make` commands will probably not work for you, but you can just write the normal commands:
Instead of `make install` you can do
```
python3.exe -m venv venv
venv/bin/pip3.exe install -r requirements.txt
```
and instead of `make` you have `venv/bin/python3.exe import.py`

I don't have access to a Windows machine, at the time of the writing, so you may need to adjust the executable path or maybe remove the `.exe` extension when running the commands.

# What it does
The application will copy the CUE and LOOPS from Rekordbox v6 to Serato v3.
Probably will work with older versions of the software, but I have not tested and I never will.

To prevent doing too much, it's restricted (for now) to only 1 playlist, so you will need to create a playlist with the
tracks that you want to have synced, and then you will need to select the playlist from the CLI prompt when it is asked for.

### How it does it:
* _HOT CUE_ points will be overwritten if they are on the same position as in RB:
  * if you have a CUE on position 1 in RB as well as in Serato, it will be overwritten in Serato
  * if you have a CUE on position 1 in RB but not in Serato, it will be created in Serato
  * if you have a CUE on position 1 in RB, a CUE on position 2 in Serato, you will get 2 CUE points: pos 1 from RB and pos 2 will be preserved

* _LOOPS_ points will be overwritten if they are on the same position as in RB:
  * if the LOOP is LOCKED in Serato, it _will not be overwritten_ (not even the name)
  * it will be created if the loop does not exist in the given position

* _MEMORY_ cues will be copied to Serato in the empty cue point locations
  * all the memory cues will be prefixed with `M: ` (notice the "space" after ":") and they will either have the name or a number
  * IF you have 5 *HOT CUE*s and 5 _MEMORY_ cues, only the first 3 memory cues will be synced as you can only have 8 *HOT CUE*s in Serato
  * they will have a default color of RED because the XML does not contain color information for them

For the application to properly set the CUEs and LOOPs ***it's very important*** to first have the beatgrid setup in Serato
as the app will use the beatgrid information to calculate the offsets between the RB beatgrid and the Serato beatgrid.

**Actually** you don't even need to set the entire beatgrid for Serato. You **just need the first marker** to match the
one from Rekordbox, as the software will use that one to calculate the offset.

**NOTE:** if the HOT CUE, LOOP or MEMORY CUE has a name, it will be copied over as well

## IF you enjoy the software
...it's useful to you and you feel that I earned it, feel free to [buy me a coffee](https://www.buymeacoffee.com/qj2rcyvc5wM) as I really enjoy them (for real...not just saying it for donations 😅).

# License

As example file I used [Perséphone - Retro Funky (SUNDANCE remix)](https://soundcloud.com/sundancemusic/pers-phone-retro-funky), 
which is licensed under the term of the [Creative Commons Attribution 3.0 Unported (CC BY 3.0) license](https://creativecommons.org/licenses/by/3.0/).

The software in the app directory are published under the [GPL-3.0 license ](LICENSE).
Everything else is licensed as described [HERE](https://github.com/Holzhaus/serato-tags#license) in the original repository
