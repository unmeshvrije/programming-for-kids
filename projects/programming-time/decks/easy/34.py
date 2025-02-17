# | computer memory      |
# |......................| 0  - 21
# |......................| 22 - 43
# |......................| 44 - 65
# |.2 1 194 174..........| 66 - 87
# |.^....................| 88 -109
# |.|....................| 110-131
# '-+--------------------'
#   |
# b-+  addr: 68
#
# Imagine each slot in the memory
# can occupy from 0 to 255, called
# one byte. The English alphabet
# is 26 symbols + 26 for upper case
# and we have the numbers and...
# we quickly run out of space.
# We store strings in UTF8 format.
# For example ® actually takes 2
# bytes to be stored, but its length
# is 1

b = '®'

print(len(b))
