# Original code
The starting point of this project was the code from https://github.com/Holzhaus/serato-tags

# Disclaimer
This software is provided as-is without active support and without providing any warranty. If you decide to
use it, make sure to back up your files as I take no responsibility for any loss of data. I built & use this software
for my own personal use, so I am testing it, however there might be cases that I haven't covered with my testing.

# How to use
1. Make sure you have Python 3.11 installed on your computer
2. Export the rekordbox.xml file from Rekordbox, open the file `import.py` and replace `tests/fixtures/rekordbox.xml` with the path of your file.
3. **MAKE A BACKUP OF YOUR MUSIC FILES**
4. Analyze your files in Serato and add the beatgrid marker labeled 1 at the same position as in Rekordbox
5. Run `make install`
6. Run `make`

# What it does
The application will copy the CUE and LOOPS from Rekordbox to Serato.

To prevent doing too much, it's restricted (for now) to only 1 playlist, so you will need to create a playlist with the
tracks that you want to have synced, and then you will need to select the playlist from the CLI prompt when it is asked for.

### How it does it:
* CUE points will be overwritten if they are on the same position as in RB:
  * if you have a CUE on position 1 in RB as well as in Serato, it will be overwritten in Serato
  * if you have a CUE on position 1 in RB but not in Serato, it will be created in Serato
  * if you have a CUE on position 1 in RB, a CUE on position 2 in Serato, you will get 2 CUE points: pos 1 from RB and pos 2 will be preserved
* LOOPS points will be overwritten if they are on the same position as in RB:
  * if the LOOP is LOCKED in Serato, it _will not be overwritten_ (not even the name)
  * it will be created if the loop does not exist in the given position

For the application to properly set the CUEs and LOOPs ***it's very important*** to first have the beatgrid setup in Serato
as the app will use the beatgrid information to calculate the offsets between the RB beatgrid and the Serato beatgrid.

**Actually** you don't even need to set the entire beatgrid for Serato. You **just need the first marker** to match the
one from Rekordbox, as the software will use that one to calculate the offset.

## License

As example file I used [Perséphone - Retro Funky (SUNDANCE remix)](https://soundcloud.com/sundancemusic/pers-phone-retro-funky), 
which is licensed under the term of the [Creative Commons Attribution 3.0 Unported (CC BY 3.0) license](https://creativecommons.org/licenses/by/3.0/).

The software in the app directory are published under the [GPL-3.0 license ](LICENSE).
Everything else is licensed as described [HERE](https://github.com/Holzhaus/serato-tags#license) in the original repository
