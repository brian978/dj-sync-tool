# V1 Tags
    Each entry data looks something like (it's the same for CUE & LOOP):
    b'\x00\x00\x01\x0b\xff\xff\xff\xff\x00\xff\xff\xff\xff\x00\xcc\x00\x00\x01\x00'
    
    The data is split like this:
    Field 1 (start_position):   4 bytes
    Field 2 (end_position):     4 bytes
    Field 3 (NULL byte):        1 byte
    Field 4 (padding):          4 bytes
    Field 3 (NULL byte):        1 byte
    Field 5 (color):            3 bytes
    Field 5 (type):             1 bytes -- EntryType
    Field 6 (boolean):          1 byte -- can only be True for loops
    
    start_position & end_position default to 4294967295 if the entry is not used (eg: not cue or loop is set)
    end_position has a different value than the default only for loops


## Empty EntryModel (mp3)
    CUE
    EntryModel(start_position_set=False, start_position=None, end_position_set=False, end_position=None, field5=b'\x00\x7f\x7f\x7f\x7f\x7f', color=b'\x00\x00\x00', type=<EntryType.INVALID: 0>, is_locked=False)

    LOOP
    EntryModel(start_position_set=False, start_position=None, end_position_set=False, end_position=None, field5=b'\x00\x7f\x7f\x7f\x7f\x7f', color=b'\x00\x00\x00', type=<EntryType.LOOP: 3>, is_locked=False)

    COLOR
    ColorModel(color=b'\xff\xff\xff', type=<EntryType.COLOR: 90>)


## Empty EntryModel (mp4)
    CUE
    EntryModel(start_position_set=False, start_position=4294967295, end_position_set=False, end_position=4294967295, field5=None, color=b'\x00\x00\x00', type=<EntryType.CUE: 1>, is_locked=False)

    LOOP
    EntryModel(start_position_set=False, start_position=4294967295, end_position_set=False, end_position=4294967295, field5=None, color=b'\x00\x00\x00', type=<EntryType.LOOP: 3>, is_locked=False)

    COLOR
    ColorModel(color=b'\x00\xff\xff\xff', type=<EntryType.COLOR: 90>)


# V2 Tags
    STUCTURE                                    >B      c       I                   I               5s                      3s              >B      ?       
    NAME    NULL    STRUCT LEN          NULL    INDEX   POS START           POS END         SOMETHING               COLOR                   LOCKED  NAME        NULL
    LOOP    \x00    \x00\x00\x00\x1f    \x00    \x00    \x00\x00\x00\xfe    \x00\x00\t%     \xff\xff\xff\xff\x00'   \xaa\xe1        \x00    \x00    first loop  \x00
    
    Locked loop
    LOOP    \x00    \x00\x00\x00\x1f    \x00    \x00    \x00\x00\x00\xfe    \x00\x00\t%     \xff\xff\xff\xff\x00'   \xaa\xe1        \x00    \x01    first loop  \x00
    
    Non-locked loop on second bar at index 0
    LOOP    \x00    \x00\x00\x00\x1f    \x00    \x00    \x00\x00\t%         \x00\x00\x11L   \xff\xff\xff\xff\x00'   \xaa\xe1        \x00    \x00    first loop  \x00
    
    Loop on second bar but at index 1
    LOOP    \x00    \x00\x00\x00\x1f    \x00    \x01    \x00\x00\t%         \x00\x00\x11L   \xff\xff\xff\xff\x00'   \xaa\xe1        \x00    \x00    first loop  \x00
    
    Loop on second bar but at last
    LOOP    \x00    \x00\x00\x00\x15    \x00    \x07    \x00\x00\x00\xfe    \x00\x00\x11L   \xff\xff\xff\xff\x00'   \xaa\xe1        \x00    \x00                \x00
    CUE     \x00    \x00\x00\x00\x16    \x00    \x00    \x00\x00\x00\xfe    \x00                                    \xc0&&          \x00    \x00    first bar   \x00
    CUE     \x00    \x00\x00\x00\x17    \x00    \x01    \x00\x00\t%         \x00                                    \x1d \xbe\xbd   \x00    \x00    second bar  \x00
    CUE     \x00    \x00\x00\x00\x16    \x00    \x02    \x00\x00\x11\x84    \x00                                    \x1f\xad&       \x00    \x00    third bar   \x00
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------
    CUE     \x00    \x00\x00\x00\x16    \x00    \x00    \x00\x00\x00\xfe    \x00                                    \xc0&&          \x00    \x00    first bar   \x00
    CUE     \x00    \x00\x00\x00\x17    \x00    \x01    \x00\x00\t%         \x00                                    \x1d\xbe\xbd    \x00    \x00    second bar  \x00
    CUE     \x00    \x00\x00\x00\x16    \x00    \x02    \x00\x00\x11\x84    \x00                                    \x1f\xad&       \x00    \x00    third bar   \x00
    
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------
    Unlocked
    BPMLOCK \x00    \x00\x00\x00\x01                                                                                                        \x00                \x00
    
    Locked
    BPMLOCK \x00    \x00\x00\x00\x01                                                                                                        \x01                \x00