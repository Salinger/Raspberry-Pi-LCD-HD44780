For HD44780 LCD on Raspberry Pi

Author : Salinger
Date   : 01/14/2013
Version: 1.1.0

[How to use]
1. Initialize
import lcd
l = lcd.HD44780()

2. Call string method 
l.string("Raspberry Pi",1)          # 1st line 
l.string(u"でPythonうごいたよー",2) # 2nd line

This program must run as "root" user like this.
$ sudo python lcd.py
 
If string over 16 chars, it cut off.
# Notice: "が" is 2 chars. ("か" + "゛")

If you want to know more info, please read source.


[History]
Version: 1.1.0 01/14/2013
  Add check length method in JapaneseCharacter class.

Version: 1.0.0 01/05/2013
  1st ver.
