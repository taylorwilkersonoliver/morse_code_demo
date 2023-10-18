"""Translate ASCII to morse code."""
import config
import functools
import pandas
from typing import Tuple
import json
import binascii
import pyaudio
import math

debug = False


class MorseMain:
    """Translate ASCII to morse code and generate tones.

    Typical usage:
        mm = MorseMain()
        mm.api_output_tone(mm.get_morse('hello world')
        '...._/._/.-.._/.-.._/---_/ /.--_/---_/.-._/.-.._/-.._/'
        # use all caps if you don't need to differentiate between upper and lower case letters:
        mm.api_output_tone(mm.get_morse('HELLO WORLD')
        '...././.-../.-../---/ /.--/---/.-./.-../-../'

    """

    @functools.cached_property
    def ascii_character_index(self):
        return [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
            'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ' ', ',', '.', '?', ';', ':',
            "'", "\"", '-', '/', '\\', '(', ')', '_', '!',
        ]

    @functools.cached_property
    def translation_frame(self):
        return {
            "ASCII":
                [
                    {'A': '.-'}, {'B': '-...'}, {'C': '-.-.'}, {'D': '-..'}, {'E': '.'}, {'F': '..-.'}, {'G': '--.'},
                    {'H': '....'}, {'I': '..'}, {'J': '.---'}, {'K': '-.-'}, {'L': '.-..'}, {'M': '--'}, {'N': '-.'},
                    {'O': '---'}, {'P': '.--.'}, {'Q': '--.-'}, {'R': '.-.'}, {'S': '...'}, {'T': '-'}, {'U': '..-'},
                    {'V': '...-'}, {'W': '.--'}, {'X': '-..-'}, {'Y': '-.--'}, {'Z': '--..'}, {'0': '-----'},
                    {'1': '.----'}, {'2': '..---'}, {'3': '...--'}, {'4': '....-'}, {'5': '.....'}, {'6': '-....'},
                    {'7': '--...'}, {'8': '---..'}, {'9': '----.'}, {' ': ' '}, {',': '--..--'}, {'.': '.-.-.-'},
                    {'?': '..--..'}, {';': '-.-.-.'}, {':': '---...'}, {"'": '.----.'}, {'-': '-....-'}, {'/': '-..-.'},
                    {"\\": "\\"}, {'(': '-.--.-'}, {')': '-.--.-'}, {'_': '..--.-'}, {'!': '-.-.--'}, {"\"": '........'}
                ],
            "MORSE":
                [
                    {'.-': 'A'}, {'-...': 'B'}, {'-.-.': 'C'}, {'-..': 'D'}, {'.': 'E'}, {'..-.': 'F'}, {'--.': 'G'},
                    {'....': 'H'}, {'..': 'I'}, {'.---': 'J'}, {'-.-': 'K'}, {'.-..': 'L'}, {'--': 'M'}, {'-.': 'N'},
                    {'---': 'O'}, {'.--.': 'P'}, {'--.-': 'Q'}, {'.-.': 'R'}, {'...': 'S'}, {'-': 'T'}, {'..-': 'U'},
                    {'...-': 'V'}, {'.--': 'W'}, {'-..-': 'X'}, {'-.--': 'Y'}, {'--..': 'Z'}, {'-----': '0'},
                    {'.----': '1'}, {'..---': '2'}, {'...--': '3'}, {'....-': '4'}, {'.....': '5'}, {'-....': '6'},
                    {'--...': '7'}, {'---..': '8'}, {'----.': '9'}, {' ': ' '}, {'--..--': ','}, {'.-.-.-': '.'},
                    {'..--..': '?'}, {'-.-.-.': ';'}, {'---...': ':'}, {'.----.': "'"}, {'-....-': '-'}, {'-..-.': '/'},
                    {"\\": "\\"}, {'-.--.-': '('}, {'-.--.-': ')'}, {'..--.-': '_'}, {'-.-.--': '!'}, {"\"": '........'}
                ]
        }

    @functools.cached_property
    def df(self) -> pandas.DataFrame:
        """Shortcut to a dataframe with the morse and ascii values."""
        return self.pd.DataFrame(self.translation_frame, index=self.ascii_character_index)

    def __init__(self):
        """These values are just here to make changes easier."""
        self.pd = pandas
        self.ascii_text = ''
        self.morse_text = ''
        self._dot = '.'
        self._dash = '-'
        self._lower = "_/"
        self._upper = "/"
        self._pass_through = "/"
        self._new_line = '\n'
        self._space = ' /'

    def string_to_binary(self, message_string):
        """Convert bytes to binary."""
        outstring = ""
        if type(message_string) == str:
            return ''.join(format(ord(x), 'b') for x in message_string)
        return outstring

    def get_morse(self, string: str) -> str:
        """Convert a string of ASCII characters to the the morse code equivalent using "." and "-"."""
        _morse: str = ""

        for char in string:
            if len(char) > 0:
                if char == self._new_line:
                    _morse += self._new_line
                if char == self._space:
                    _morse += self._space
                else:
                    if char.isalpha():
                        if char.islower():
                            c = char.upper()
                            _morse += self.df['ASCII'][c][c] + self._lower
                        if char.isupper():
                            c = char
                            _morse += self.df['ASCII'][c][c] + self._upper
                    else:
                        c = char
                        _morse += self.df['ASCII'][c][c] + self._pass_through
        return _morse

    def get_ascii(self, string: str) -> str:
        """Convert a string of morse code  using "." and "-" and receive the ASCII equivalent.
        This also handles uppercase and lowercase letters."""
        ascii_text = []
        morse_sequence = ""
        output = ""
        make_lower = False
        for char in string:
            if char != '/' and char != '_':
                morse_sequence += char
            if char == '_':
                make_lower = True
            if char == '/':
                for i in self.translation_frame['MORSE']:
                    if i.get(morse_sequence) is not None:
                        try:
                            if make_lower and i.get(morse_sequence).isalpha():
                                ascii_text.append(i.get(morse_sequence).lower())
                                make_lower = False
                            else:
                                ascii_text.append(i.get(morse_sequence))
                        except KeyError as error:
                            print(error)
                            pass
                morse_sequence = ''
        for i in ascii_text:
            output += i
        return output

    def _delete_character(self, text_in: Tuple[str, str]) -> Tuple:
        """Delete the last ASCII character, and morse equivalent, from a tuple containing corresponding strings."""
        last_morse_char = text_in[0][len(text_in[0]) - 1]
        utext = text_in[0][:-1]
        morse_utext = text_in[1][:-len(self.get_morse(last_morse_char))]
        return utext, morse_utext

    def api_output_morse(self, value):
        """Output morse for dash app debug."""
        if config.debug:
            print(len(value))
        if len(value) > 0 and value[len(value) - 1] == '\n':
            new_line = True
        else:
            new_line = False
        if new_line:
            v = self.get_morse(value[:len(value) - 1:]) + '\n'
        else:
            v = self.get_morse(value)
        return json.dumps(
            {
                "ascii": value,
                "ascii_binary": self.string_to_binary(value),
                "morse": v,
                "morse_binary": self.string_to_binary(v),
                "ascii_base64": binascii.b2a_base64(value.encode('utf-8'), newline=False).decode('utf-8'),
                "ascii_binary_base64": binascii.b2a_base64(self.string_to_binary(value).encode('utf-8'), newline=False).decode('utf-8'),
                "morse_base64": binascii.b2a_base64(v.encode('utf-8'), newline=False).decode('utf-8'),
                "morse_binary_base64": binascii.b2a_base64(self.string_to_binary(v).encode('utf-8'), newline=False).decode('utf-8')
            }
        )

    def api_output_ascii(self, value: str) -> str:
        """Output ASCII for dash app debug."""
        if config.debug:
            print(value[len(value) - 2] + value[len(value) - 1])
        if len(value) > 0 and value[len(value) - 2] + value[len(value) - 1] == '\n':
            new_line = True
        else:
            new_line = False
        if new_line:
            v = self.get_ascii(value[:len(value) - 1:]) + '\n'
        else:
            v = self.get_ascii(value)
        return json.dumps(
            {
                "ascii": v,
                "ascii_binary": self.string_to_binary(v),
                "morse": value,
                "morse_binary": self.string_to_binary(value),
                "ascii_base64": binascii.b2a_base64(v.encode('utf-8'), newline=False).decode('utf-8'),
                "ascii_binary_base64": binascii.b2a_base64(self.string_to_binary(v).encode('utf-8'),
                                                           newline=False).decode('utf-8'),
                "morse_base64": binascii.b2a_base64(value.encode('utf-8'), newline=False).decode('utf-8'),
                "morse_binary_base64": binascii.b2a_base64(self.string_to_binary(value).encode('utf-8'),
                                                           newline=False).decode('utf-8')
            }
        )

    def api_output_tone(self, morse):
        pa = pyaudio.PyAudio
        bitrate = 5000
        fq = 641
        cw = []
        for dahdit in morse:
            if dahdit == ".":
                dit_dur = .25  # seconds to play sound
                if fq > bitrate:
                    bitrate = fq + 100
                dit_frame = int(bitrate * dit_dur)
                dit_rest_frame = dit_frame % bitrate
                wave_data = ''
                for x in range(dit_frame):
                    wave_data = wave_data + chr(int(math.sin(x / ((bitrate / fq) / math.pi)) * 127 + 128))
                for x in range(dit_rest_frame):
                    wave_data = wave_data + chr(128)
                cw.append(wave_data)
            elif dahdit == "-":
                dah_dur = .75  # seconds to play sound
                if fq > bitrate:
                    bitrate = fq + 100
                dah_frame = int(bitrate * dah_dur)
                dah_rest_frame = dah_frame % bitrate
                wave_data = ''
                for x in range(dah_frame):
                    wave_data = wave_data + chr(int(math.sin(x / ((bitrate / fq) / math.pi)) * 127 + 128))
                for x in range(dah_rest_frame):
                    wave_data = wave_data + chr(128)
                cw.append(wave_data)
            elif dahdit == "/":
                letter_dur = 1  # seconds to play sound
                if fq > bitrate:
                    bitrate = fq + 100
                letter_frame = int(bitrate * letter_dur)
                letter_rest_frame = letter_frame % bitrate
                wave_data = ''
                for x in range(letter_frame):
                    wave_data = wave_data + chr(int(math.sin(x / ((bitrate / .01) / math.pi)) * 127 + 128))
                for x in range(letter_rest_frame):
                    wave_data = wave_data + chr(128)
                cw.append(wave_data)

        p = pa()
        stream = p.open(format=p.get_format_from_width(1), channels=2, rate=bitrate, output=True)
        for i in cw:
            stream.write(i)
        stream.stop_stream()
        stream.close()
        p.terminate()

    def api_output_tone_fscw(self, morse, extend_duration=0):
        pa = pyaudio.PyAudio
        bitrate = 19600
        fq = 641
        fq_shift = 100
        fq_raise = 300
        dah_fq = fq + fq_raise - fq_shift
        dit_fq = fq + fq_raise + fq_shift
        dah_dur = .15 + extend_duration
        dit_dur = .15 + extend_duration
        letter_dur = .15 + extend_duration
        cw = []
        for dahdit in morse:
            if dahdit == ".":
                if fq > bitrate:
                    bitrate = fq + 100
                dit_frame = int(bitrate * dit_dur)
                dit_rest_frame = dit_frame % bitrate
                wave_data = ''
                for x in range(dit_frame):
                    wave_data = wave_data + chr(int(math.sin(x / ((bitrate / dit_fq) / math.pi)) * 127 + 128))
                for x in range(dit_rest_frame):
                    wave_data = wave_data + chr(128)
                cw.append(wave_data)
            elif dahdit == "-":
                if fq > bitrate:
                    bitrate = fq + 100
                dah_frame = int(bitrate * dah_dur)
                dah_rest_frame = dah_frame % bitrate
                wave_data = ''
                for x in range(dah_frame):
                    wave_data = wave_data + chr(int(math.sin(x / ((bitrate / dah_fq) / math.pi)) * 127 + 128))
                for x in range(dah_rest_frame):
                    wave_data = wave_data + chr(128)
                cw.append(wave_data)
            elif dahdit == "/":
                if fq > bitrate:
                    bitrate = fq + 100
                letter_frame = int(bitrate * letter_dur)
                letter_rest_frame = letter_frame % bitrate
                wave_data = ''
                for x in range(letter_frame):
                    wave_data = wave_data + chr(int(math.sin(x / ((bitrate / fq) / math.pi)) * 127 + 128))
                for x in range(letter_rest_frame):
                    wave_data = wave_data + chr(128)
                cw.append(wave_data)

        p = pa()
        stream = p.open(format=p.get_format_from_width(1), channels=2, rate=bitrate, output=True)
        for i in cw:
            stream.write(i)
        stream.stop_stream()
        stream.close()
        p.terminate()

    def api_output_tone_fscw(self, morse, extend_duration=0):
        pa = pyaudio.PyAudio
        bitrate = 19600
        fq = 641
        fq_shift = 100
        fq_raise = 300
        dah_fq = fq + fq_raise - fq_shift
        dit_fq = fq + fq_raise + fq_shift
        dah_dur = .15 + extend_duration
        dit_dur = .15 + extend_duration
        letter_dur = .15 + extend_duration
        cw = []
        for dahdit in morse:
            if dahdit == ".":
                if fq > bitrate:
                    bitrate = fq + 100
                dit_frame = int(bitrate * dit_dur)
                dit_rest_frame = dit_frame % bitrate
                wave_data = ''
                for x in range(dit_frame):
                    wave_data = wave_data + chr(int(math.sin(x / ((bitrate / dit_fq) / math.pi)) * 127 + 128))
                for x in range(dit_rest_frame):
                    wave_data = wave_data + chr(128)
                cw.append(wave_data)
            elif dahdit == "-":
                if fq > bitrate:
                    bitrate = fq + 100
                dah_frame = int(bitrate * dah_dur)
                dah_rest_frame = dah_frame % bitrate
                wave_data = ''
                for x in range(dah_frame):
                    wave_data = wave_data + chr(int(math.sin(x / ((bitrate / dah_fq) / math.pi)) * 127 + 128))
                for x in range(dah_rest_frame):
                    wave_data = wave_data + chr(128)
                cw.append(wave_data)
            elif dahdit == "/":
                if fq > bitrate:
                    bitrate = fq + 100
                dah_frame = int(bitrate * letter_dur)
                dah_rest_frame = dah_frame % bitrate
                wave_data = ''
                for x in range(dah_frame):
                    wave_data = wave_data + chr(int(math.sin(x / ((bitrate / fq) / math.pi)) * 127 + 128))
                for x in range(dah_rest_frame):
                    wave_data = wave_data + chr(128)
                cw.append(wave_data)

        p = pa()
        stream = p.open(format=p.get_format_from_width(1), channels=2, rate=bitrate, output=True)
        for i in cw:
            stream.write(i)
        stream.stop_stream()
        stream.close()
        p.terminate()
