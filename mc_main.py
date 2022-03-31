"""Translate ASCII to morse code."""
import config
import functools
import pandas
from typing import Tuple

debug = True


class MorseMain:

    @functools.cached_property
    def ascii_character_index(self):
        return [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
            'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ' ', ',', '.', '?', ';', ':',
            "'", '-', '/', '\\', '(', ')', '_', '!',
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
                    {"\\": "\\"}, {'(': '-.--.-'}, {')': '-.--.-'}, {'_': '..--.-'}, {'!': '-.-.--'}],
            "MORSE":
                [
                    {'.-': 'A'}, {'-...': 'B'}, {'-.-.': 'C'}, {'-..': 'D'}, {'.': 'E'}, {'..-.': 'F'}, {'--.': 'G'},
                    {'....': 'H'}, {'..': 'I'}, {'.---': 'J'}, {'-.-': 'K'}, {'.-..': 'L'}, {'--': 'M'}, {'-.': 'N'},
                    {'---': 'O'}, {'.--.': 'P'}, {'--.-': 'Q'}, {'.-.': 'R'}, {'...': 'S'}, {'-': 'T'}, {'..-': 'U'},
                    {'...-': 'V'}, {'.--': 'W'}, {'-..-': 'X'}, {'-.--': 'Y'}, {'--..': 'Z'}, {'-----': '0'},
                    {'.----': '1'}, {'..---': '2'}, {'...--': '3'}, {'....-': '4'}, {'.....': '5'}, {'-....': '6'},
                    {'--...': '7'}, {'---..': '8'}, {'----.': '9'}, {' ': ' '}, {'--..--': ','}, {'.-.-.-': '.'},
                    {'..--..': '?'}, {'-.-.-.': ';'}, {'---...': ':'}, {'.----.': "'"}, {'-....-': '-'}, {'-..-.': '/'},
                    {"\\": "\\"}, {'-.--.-': '('}, {'-.--.-': ')'}, {'..--.-': '_'}, {'-.-.--': '!'}
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
        return \
            "{" \
            f"ascii: {value}," \
            f"ascii_binary: {self.string_to_binary(value)}," \
            f"morse: {v}," \
            f"morse_binary: {self.string_to_binary(v)}" \
            "}"

    def api_output_ascii(self, value: str) -> str:
        """Output ASCII for dash app debug."""
        if config.debug:
            print(len(value))
        if len(value) > 0 and value[len(value) - 1] == '\n':
            new_line = True
        else:
            new_line = False
        if new_line:
            v = self.get_ascii(value[:len(value) - 1:]) + '\n'
        else:
            v = self.get_ascii(value)
        return \
            "{" \
            f"ascii: {v}," \
            f"ascii_binary: {self.string_to_binary(v)}\"," \
            f"morse: {value}\"," \
            f"morse_binary: {self.string_to_binary(value)}\"" \
            "}"
