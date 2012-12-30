#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# For HD44780 LCD on Raspberry Pi
#
# Author : Salinger
# Date   : 01/05/2013
# Ver.   : 1.1.0

#
# How to use this module in main().
#


# The wiring for the LCD is as follows:
# 1 : GND
# 2 : 5V
# 3 : Contrast (0-5V)*
# 4 : RS (Register Select)
# 5 : R/W (Read Write)       - GROUND THIS PIN
# 6 : Enable or Strobe
# 7 : Data Bit 0             - NOT USED
# 8 : Data Bit 1             - NOT USED
# 9 : Data Bit 2             - NOT USED
# 10: Data Bit 3             - NOT USED
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Backlight +5V**
# 16: LCD Backlight GND

import RPi.GPIO as GPIO
import time
import re

class HD44780(object):
    # Define GPIO to LCD mapping
    LCD_RS = 7
    LCD_E  = 8
    LCD_D4 = 25 
    LCD_D5 = 24
    LCD_D6 = 23
    LCD_D7 = 18

    # Define some device constants
    LCD_WIDTH = 16  #Maximum characters per line
    LCD_CHR = True
    LCD_CMD = False

    LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line 

    # Timing constants
    E_PULSE = 0.00005
    E_DELAY = 0.00005

    # Re object
    re_en = re.compile(
        r"[a-zA-Z0-9 !@#$%^&*()\-_=+\\|`[\]{};:'\",\.<>]"
        )

    def __init__(self):
        # Initialise GPIO
        GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
        GPIO.setup(self.LCD_E, GPIO.OUT)  # E
        GPIO.setup(self.LCD_RS, GPIO.OUT) # RS
        GPIO.setup(self.LCD_D4, GPIO.OUT) # DB4
        GPIO.setup(self.LCD_D5, GPIO.OUT) # DB5
        GPIO.setup(self.LCD_D6, GPIO.OUT) # DB6
        GPIO.setup(self.LCD_D7, GPIO.OUT) # DB7

        # Initialise display
        self.byte(0x33,self.LCD_CMD)
        self.byte(0x32,self.LCD_CMD)
        self.byte(0x28,self.LCD_CMD)
        self.byte(0x0C,self.LCD_CMD)
        self.byte(0x06,self.LCD_CMD)
        self.byte(0x01,self.LCD_CMD)
        return

    def string(self,message,column = 1):
        # Send string to display
        # column = 1:line1 2:line2
        if column == 1:
            line = self.LCD_LINE_1
        elif column == 2:
            line = self.LCD_LINE_2
        else:
            raise AttributeError, "Please set correct column (1 or 2)."
        self.byte(line, self.LCD_CMD)
        message = message.ljust(self.LCD_WIDTH," ")  
        for i in range(self.LCD_WIDTH):
            # English
            if self.re_en.match(message[i]):
                self.byte(ord(message[i]),self.LCD_CHR)
            # Japanese
            elif message[i] in JapaneseCharacter.zen_to_han:
                self.byte(
                    JapaneseCharacter.zen_to_han[message[i]],
                    self.LCD_CHR
                    )
                # For dakuon and handakuon
                if message[i] in JapaneseCharacter.dakuon:
                    self.byte(
                        JapaneseCharacter.zen_to_han[u'゛'],
                        self.LCD_CHR
                        )
                elif message[i] in JapaneseCharacter.handakuon: 
                    self.byte(
                        JapaneseCharacter.zen_to_han[u'゜'],
                        self.LCD_CHR
                        )
            # Unknown Character
            else:
                raise ValueError, 'Unknown character:"' + message[i] + '"'
        return

    def byte(self,bits,mode):
        # Send byte to data pins
        # bits = data
        # mode = True  for character
        #        False for command
        GPIO.output(self.LCD_RS, mode) # RS

        # High bits
        GPIO.output(self.LCD_D4, False)
        GPIO.output(self.LCD_D5, False)
        GPIO.output(self.LCD_D6, False)
        GPIO.output(self.LCD_D7, False)
        if bits&0x10==0x10:
            GPIO.output(self.LCD_D4, True)
        if bits&0x20==0x20:
            GPIO.output(self.LCD_D5, True)
        if bits&0x40==0x40:
            GPIO.output(self.LCD_D6, True)
        if bits&0x80==0x80:
            GPIO.output(self.LCD_D7, True)

        # Toggle 'Enable' pin
        time.sleep(self.E_DELAY)
        GPIO.output(self.LCD_E, True)  
        time.sleep(self.E_PULSE)
        GPIO.output(self.LCD_E, False)  
        time.sleep(self.E_DELAY)

        # Low bits
        GPIO.output(self.LCD_D4, False)
        GPIO.output(self.LCD_D5, False)
        GPIO.output(self.LCD_D6, False)
        GPIO.output(self.LCD_D7, False)
        if bits&0x01==0x01:
            GPIO.output(self.LCD_D4, True)
        if bits&0x02==0x02:
            GPIO.output(self.LCD_D5, True)
        if bits&0x04==0x04:
            GPIO.output(self.LCD_D6, True)
        if bits&0x08==0x08:
            GPIO.output(self.LCD_D7, True)

        # Toggle 'Enable' pin
        time.sleep(self.E_DELAY)    
        GPIO.output(self.LCD_E, True)  
        time.sleep(self.E_PULSE)
        GPIO.output(self.LCD_E, False)  
        time.sleep(self.E_DELAY)
        return

class JapaneseCharacter(object):
    # Lists and dictionary for Japanese
    handakuon= [
        u'ぱ',  u'ぴ',  u'ぷ',  u'ぺ',  u'ぽ',
        u'パ',  u'ピ',  u'プ',  u'ペ',  u'ポ'
        ]
    dakuon = [
        u'が',  u'ぎ',  u'ぐ',  u'げ',  u'ご',
        u'ざ',  u'じ',  u'ず',  u'ぜ',  u'ぞ',
        u'だ',  u'ぢ',  u'づ',  u'で',  u'ど',
        u'ば',  u'び',  u'ぶ',  u'べ',  u'ぼ',
        u'ガ',  u'ギ',  u'グ',  u'ゲ',  u'ゴ',
        u'ザ',  u'ジ',  u'ズ',  u'ゼ',  u'ゾ',
        u'ダ',  u'ヂ',  u'ヅ',  u'デ',  u'ド',
        u'バ',  u'ビ',  u'ブ',  u'ベ',  u'ボ'
        ]
    zen_to_han  =  {
        u'ア':0xB1,  u'イ':0xB2,  u'ウ':0xB3,  u'エ':0xB4,  u'オ':0xB5,
        u'カ':0xB6,  u'キ':0xB7,  u'ク':0xB8,  u'ケ':0xB9,  u'コ':0xBA,
        u'サ':0xBB,  u'シ':0xBC,  u'ス':0xBD,  u'セ':0xBE,  u'ソ':0xBF,
        u'タ':0xC0,  u'チ':0xC1,  u'ツ':0xC2,  u'テ':0xC3,  u'ト':0xC4,
        u'ナ':0xC5,  u'ニ':0xC6,  u'ヌ':0xC7,  u'ネ':0xC8,  u'ノ':0xC9,
        u'ハ':0xCA,  u'ヒ':0xCB,  u'フ':0xCC,  u'ヘ':0xCD,  u'ホ':0xCE,
        u'マ':0xCF,  u'ミ':0xD0,  u'ム':0xD1,  u'メ':0xD2,  u'モ':0xD3,
        u'ヤ':0xD4,  u'ユ':0xD5,  u'ヨ':0xD6,  u'゜':0xDF,  u'゛':0xDE,
        u'ラ':0xD7,  u'リ':0xD8,  u'ル':0xD9,  u'レ':0xDA,  u'ロ':0xDB,
        u'ワ':0xDC,  u'ン':0xDD,  u'「':0xA2,  u'」':0xA3,  u'。':0xA1,
        u'、':0xA4,  u'・':0xA5,  u'ァ':0xA7,  u'ィ':0xA8,  u'ゥ':0xA9,
        u'ェ':0xAA,  u'ォ':0xAB,  u'ャ':0xAC,  u'ュ':0xAD,  u'ョ':0xAE,
        u'ガ':0xB6,  u'ギ':0xB7,  u'グ':0xB8,  u'ゲ':0xB9,  u'ゴ':0xBA,
        u'ザ':0xBB,  u'ジ':0xBC,  u'ズ':0xBD,  u'ゼ':0xBE,  u'ゾ':0xBF,
        u'ダ':0xC0,  u'ヂ':0xC1,  u'ヅ':0xC2,  u'デ':0xC3,  u'ド':0xC4,
        u'バ':0xCA,  u'ビ':0xCB,  u'ブ':0xCC,  u'ベ':0xCD,  u'ボ':0xCE,
        u'パ':0xCA,  u'ピ':0xCB,  u'プ':0xCC,  u'ペ':0xCD,  u'ポ':0xCE,
        u'ヴ':0xB3,  u'ッ':0xAF,  u'ヲ':0xA6,
        u'あ' :0xB1, u'い' :0xB2, u'う' :0xB3, u'え' :0xB4, u'お' :0xB5,
        u'か' :0xB6, u'き' :0xB7, u'く' :0xB8, u'け' :0xB9, u'こ' :0xBA,
        u'さ' :0xBB, u'し' :0xBC, u'す' :0xBD, u'せ' :0xBE, u'そ' :0xBF,
        u'た' :0xC0, u'ち' :0xC1, u'つ' :0xC2, u'て' :0xC3, u'と' :0xC4,
        u'な' :0xC5, u'に' :0xC6, u'ぬ' :0xC7, u'ね' :0xC8, u'の' :0xC9,
        u'は' :0xCA, u'ひ' :0xCB, u'ふ' :0xCC, u'へ' :0xCD, u'ほ' :0xCE,
        u'ま' :0xCF, u'み' :0xD0, u'む' :0xD1, u'め' :0xD2, u'も' :0xD3,
        u'や' :0xD4, u'ゆ' :0xD5, u'よ' :0xD6, u'゜' :0xDF, u'゛' :0xDE,
        u'ら' :0xD7, u'り' :0xD8, u'る' :0xD9, u'れ' :0xDA, u'ろ' :0xDB,
        u'わ' :0xDC, u'ん' :0xDD, u'っ' :0xAF, u'　' :0xA0, u' ' :0xA0,
        u'、' :0xA4, u'・' :0xA5, u'ぁ' :0xA7, u'ぃ' :0xA8, u'ぅ' :0xA9,
        u'ぇ' :0xAA, u'ぉ' :0xAB, u'ゃ' :0xAC, u'ゅ' :0xAD, u'ょ' :0xAE,
        u'が' :0xB6, u'ぎ' :0xB7, u'ぐ' :0xB8, u'げ' :0xB9, u'ご' :0xBA,
        u'ざ' :0xBB, u'じ' :0xBC, u'ず' :0xBD, u'ぜ' :0xBE, u'ぞ' :0xBF,
        u'だ' :0xC0, u'ぢ' :0XC1, u'づ' :0xC2, u'で' :0xC3, u'ど' :0xC4,
        u'ば' :0xCA, u'び' :0xCB, u'ぶ' :0xCC, u'べ' :0xCD, u'ぼ' :0xCE,
        u'ぱ' :0xCA, u'ぴ' :0xCB, u'ぷ' :0xCC, u'ぺ' :0xCD, u'ぽ' :0xCE,
        u'を' :0xA6 ,u'ー' :0xB0
        }

    def check_length(self,string):
        # Return Japanese string length on LCD.
        # If some character can't output, return False.
        counter = 0
        for c in string:
            if c in self.handakuon or c in self.dakuon:
                counter += 2
            elif c in self.zen_to_han:
                counter += 1
            else:
                return False
        return counter

def main():
    # [How to use]
    # 1. Initialize
    lcd = HD44780()
    # 2. Call string method 
    lcd.string("Raspberry Pi",1)          # 1st line 
    lcd.string(u"でPythonうごいたよー",2) # 2nd line

    # This program must run as "root" user like this.
    # $ sudo python lcd.py
 
    # If string over 16 chars, it cut off.
    # Notice: "が" is 2 chars. ("か" + "゛")

if __name__ == "__main__":
    main()
