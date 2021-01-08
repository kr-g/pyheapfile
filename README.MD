
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


# pyheapfile - heap file storage

`pyheapfile` is a file persistent heap structure (single linked list)


# memory / file layout

## general node layout

| name | size / value | description |
| --- | --- | --- | 
| magik | 4 byte 0x_2_bad_dead | header magic number byte sequence for node structure |
| aloc | 6 byte | length of heap node |
| used | 6 byte | length of data in heap node |
| data | x bytes | data area |

the internal structure is a calculated single linked list. 
there are no absolute file positions stored. 
all is relative.
navigation is just possible in one direction the method `read_next()`.

when reading continuesly with `read_next()` the not persited values `prev`, 
and `succ` are calculated and available in the `Node` instance. 
these are only "values"; no linking of `Node` objects at this place.

because of this the `free()` method merges only (continuesly read) nodes properly.

`Node` objects are not cached at any place.
calling `read_node()` multiple time creates multiple Node objects.
in case one of them change the others are unaware of the change.


## limitation

the internal structure allows a maximum node data area of 
2^48 = 281.474.976.710.656 bytes 
= 268.435.456 MB
= 256 GB (all of them calc on 2^10 base)

the max size is per node / block in the heap file.

the total number of nodes is limited only by the used filesystem 
(on the server running this software module).


## continuesly node layout

the following shows an example layout inside a file. 
described as tuple values

(0x2baddead,aloc=16,used=5,"hello"),(0x2baddead,aloc=10,used=5,"world"),(0x2baddead,aloc=10,used=1,"!"),


## hexdump of sample heap file 

the test case `test_realloc_append` creates following heap file (as of release v0.0.1).

the first node is reallocated and marked as free. 
the content of the data block is copied by `realloc()` to the new node.
the data section of the free node is not wiped with 0.
only the `used` value is set to 0 to indicate that the node contains no data.
the marker 0x55 is created by `alloc_append()` only when the used data area size
is less than the `aloc` (allocated) range. 


    00000000  2b ad de ad 00 00 00 00  00 0a 00 00 00 00 00 00  |+...............|
    00000010  68 65 6c 6c 6f 00 00 00  00 55 2b ad de ad 00 00  |hello....U+.....|
    00000020  00 00 00 0a 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000030  00 00 00 55 2b ad de ad  00 00 00 00 00 14 00 00  |...U+...........|
    00000040  00 00 00 05 77 6f 72 6c  64 00 00 00 00 00 00 00  |....world.......|
    00000050  00 00 00 00 00 00 00 55  2b ad de ad 00 00 00 00  |.......U+.......|
    00000060  00 14 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000070  00 00 00 00 00 00 00 00  00 00 00 55 2b ad de ad  |...........U+...|
    00000080  00 00 00 00 00 32 00 00  00 00 00 01 21 00 00 00  |.....2......!...|
    00000090  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    000000a0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    000000b0  00 00 00 00 00 00 00 00  00 00 00 00 00 55 2b ad  |.............U+.|
    000000c0  de ad 00 00 00 00 00 c8  00 00 00 00 00 05 68 65  |..............he|
    000000d0  6c 6c 6f 00 00 00 00 00  00 00 00 00 00 00 00 00  |llo.............|
    000000e0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    000000f0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000100  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000110  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000120  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000130  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000140  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000150  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000160  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000170  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000180  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000190  00 00 00 00 00 55                                 |.....U|
    00000196


## remark on bash tooling

under linux you can use `hexdump -Cv filename.hpf` from bash
to explore the content of a heap file.


# how to use

the heap file class offers various methods to manipulate the heap. 
e.g. such as:
- alloc
- free
- realloc

refer to [`sample.py`](https://github.com/kr-g/pyheapfile/blob/main/sample.py)

refer also to test cases in [`tests`](https://github.com/kr-g/pyheapfile/blob/main/tests)


# Platform

Tested on Python3, and Linux.


# development status

alpha state.
the API or logical call flow might change without prior notice.

read [`CHANGELOG`](https://github.com/kr-g/pyheapfile/blob/main/CHANGELOG.MD)
for latest, or upcoming news.


# installation
    
available on pypi. install with:

    python3 -m pip install pyheapfile
    
