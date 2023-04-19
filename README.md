# Original code
The starting point of this project was the code from https://github.com/Holzhaus/serato-tags

# How to use
1. Make sure you have Python 3.11 installed on your computer
2. Export the rekordbox.xml file from Rekordbox and place it into a `var/` folder right at the root of the project
3. **Make a backup of your music files**
4. Run `make install`
5. Run `make`

# What it does
The application will copy the CUE and LOOPS from Rekordbox to Serato.

### How it does it:
* CUE points will be overwritten if they are on the same position as in RB:
  * if you have a CUE on position 1 in RB as well as in Serato, it will be overwritten in Serato
  * if you have a CUE on position 1 in RB but not in Serato, it will be created in Serato
  * if you have a CUE on position 1 in RB, a CUE on position 2 in Serato, you will get 2 CUE points: pos 1 from RB and pos 2 will be preserved
* LOOPS points will be overwritten if they are on the same position as in RB:
  * if the LOOP is LOCKED in Serato, it _will not be overwritten_ (not even the name)
  * it will be created if the loop does not exist in the given position
  * additionally a CUE point will be created for the LOOP, ONLY IF the CUE point position is empty

For the application to properly set the CUEs and LOOPs ***it's very important*** to first have the beatgrid properly setup in Serato
as the app will use the beatgrid information to calculate the offsets between the RB beatgrid and the Serato beatgrid.

## License

As example file I used [Perséphone - Retro Funky (SUNDANCE remix)](https://soundcloud.com/sundancemusic/pers-phone-retro-funky), 
which is licensed under the term of the [Creative Commons Attribution 3.0 Unported (CC BY 3.0) license](https://creativecommons.org/licenses/by/3.0/).

The software in the app directory are published under the [GPL-3.0 license ](LICENSE).
Everything else is licensed as described [HERE](https://github.com/Holzhaus/serato-tags#license) in the original repository
