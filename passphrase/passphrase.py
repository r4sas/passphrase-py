"""Passphrase: Generates cryptographically secure passphrases and passwords

Passphrases are built by picking from a word list using cryptographically
secure random number generator. Passwords are built from printable characters.
"""

from os.path import isfile
from .secrets import randchoice, randhex, randbetween
from .calc import entropy_bits as calc_entropy_bits
from .calc import entropy_bits_nrange as calc_entropy_bits_nrange
from .calc import password_length_needed as calc_password_length_needed
from .calc import words_amount_needed as calc_words_amount_needed
from .settings import MIN_NUM, MAX_NUM

__author__ = "HacKan"
__license__ = "GNU GPL 3.0+"
__version__ = "0.5.0"


class Passphrase():
    """Generates cryptographically secure passphrases and passwords.

    Attributes:
        wordlist: A list of words to be consumed by the passphrase generator.
        amount_w: Amount of words to be generated by the passphrase generator.
        amount_n: Amount of numbers to be generated by the passphrase
                  generator.
        randnum_min: Minimum value for the random number in the passphrase.
        randnum_max: Maximum value for the random number in the passphrase.
        passwordlen: Length of the password.
        last_result: The last generated passphrase or password.
        entropy_bits_req: The entropy bits required to satisfy (for
                          calculations).
        password_use_digits: Set the use of digits for password generation.
        password_use_lowercase: Set the use of lower case alphabet for password
                                generation.
        password_use_uppercase: Set the use of upper case alphabet for password
                                generation.
        password_use_punctuation: Set the use of punctuation symbols for
                                  password generation.
    """

    _passwordlen = None
    _amount_n = None
    _amount_w = None
    last_result = None
    _randnum_min = MIN_NUM
    _randnum_max = MAX_NUM
    _entropy_bits_req = None
    _wordlist = None
    _wordlist_entropy_bits = None
    _external_wordlist = None
    _separator = ' '
    _password_use_lowercase = True
    _password_use_uppercase = True
    _password_use_digits = True
    _password_use_punctuation = True

    @property
    def entropy_bits_req(self):
        return self._entropy_bits_req

    @entropy_bits_req.setter
    def entropy_bits_req(self, entropybits: float) -> None:
        if not isinstance(entropybits, (int, float)):
            raise TypeError('entropy_bits_req can only be int or float')
        if entropybits < 0:
            raise ValueError('entropy_bits_req should be greater than 0')
        self._entropy_bits_req = float(entropybits)

    @property
    def randnum_min(self):
        return self._randnum_min

    @randnum_min.setter
    def randnum_min(self, randnum: int) -> None:
        if not isinstance(randnum, int):
            raise TypeError('randnum_min can only be int')
        if randnum < 0:
            raise ValueError('randnum_min should be greater than 0')
        self._randnum_min = randnum

    @property
    def randnum_max(self):
        return self._randnum_max

    @randnum_max.setter
    def randnum_max(self, randnum: int) -> None:
        if not isinstance(randnum, int):
            raise TypeError('randnum_max can only be int')
        if randnum < 0:
            raise ValueError('randnum_max should be greater than 0')
        self._randnum_max = randnum

    @property
    def amount_w(self):
        return self._amount_w

    @amount_w.setter
    def amount_w(self, amount: int) -> None:
        if not isinstance(amount, int):
            raise TypeError('amount_w can only be int')
        if amount < 0:
            raise ValueError('amount_w should be greater than 0')
        self._amount_w = amount

    @property
    def amount_n(self):
        return self._amount_n

    @amount_n.setter
    def amount_n(self, amount: int) -> None:
        if not isinstance(amount, int):
            raise TypeError('amount_n can only be int')
        if amount < 0:
            raise ValueError('amount_n should be greater than 0')
        self._amount_n = amount

    @property
    def passwordlen(self):
        return self._passwordlen

    @passwordlen.setter
    def passwordlen(self, length: int) -> None:
        if not isinstance(length, int):
            raise TypeError('passwordlen can only be int')
        if length < 0:
            raise ValueError('passwordlen should be greater than 0')
        self._passwordlen = length

    @property
    def separator(self):
        return self._separator

    @separator.setter
    def separator(self, sep: str) -> None:
        if not isinstance(sep, str):
            raise TypeError('separator can only be string')
        self._separator = sep

    @property
    def wordlist(self):
        return self._wordlist

    @wordlist.setter
    def wordlist(self, words: list) -> None:
        if not isinstance(words, (list, tuple)):
            raise TypeError('wordlist can only be list or tuple')
        self._wordlist = list(words)
        self._external_wordlist = True

    @property
    def password_use_lowercase(self):
        return self._password_use_lowercase

    @password_use_lowercase.setter
    def password_use_lowercase(self, use_lowercase: bool) -> None:
        self._password_use_lowercase = bool(use_lowercase)

    @property
    def password_use_uppercase(self):
        return self._password_use_uppercase

    @password_use_uppercase.setter
    def password_use_uppercase(self, use_uppercase: bool) -> None:
        self._password_use_uppercase = bool(use_uppercase)

    @property
    def password_use_digits(self):
        return self._password_use_digits

    @password_use_digits.setter
    def password_use_digits(self, use_digits: bool) -> None:
        self._password_use_digits = bool(use_digits)

    @property
    def password_use_punctuation(self):
        return self._password_use_punctuation

    @password_use_punctuation.setter
    def password_use_punctuation(self, use_punctuation: bool) -> None:
        self._password_use_punctuation = bool(use_punctuation)

    def __init__(
        self,
        inputfile: str = None,
        is_diceware: bool = False
    ) -> None:
        """Generates cryptographically secure passphrases and passwords.

        Keyword arguments:
        inputfile -- A string with the path to the wordlist file to load, or
        the value 'internal' to load the internal one.
        is_diceware -- True if the wordlist is diceware-like (not needed for
        internal).
        """

        if inputfile == 'internal':
            self.load_internal_wordlist()
        elif inputfile is not None:
            self.import_words_from_file(inputfile, is_diceware)

    def __str__(self) -> str:
        if not self.last_result:
            return ''

        separator_len = len(self.separator)
        rm_last_separator = -separator_len if separator_len > 0 else None
        return "".join(
            '{}{}'.format(w, self.separator) for w in map(
                str,
                self.last_result
            )
        )[:rm_last_separator:]

    def load_internal_wordlist(self) -> None:
        """Load internal wordlist."""

        from json import loads as json_loads
        from pkg_resources import resource_string

        wordlist = json_loads(resource_string(
            'passphrase',
            'wordlist.json'
        ).decode('utf-8'))
        self.wordlist = wordlist['wordlist']
        self._wordlist_entropy_bits = wordlist['entropy_bits']
        self._external_wordlist = False

    @staticmethod
    def entropy_bits(lst: list) -> float:
        """Calculate the entropy of a wordlist or a numerical range.

        Keyword arguments:
        lst -- A wordlist as list or tuple, or a numerical range as a list:
               (minimum, maximum)

        Returns: float
        """

        if not isinstance(lst, (tuple, list)):
            raise TypeError('lst must be a list or a tuple')

        size = len(lst)
        if (
            size == 2
            and isinstance(lst[0], (int, float)) is True
            and isinstance(lst[1], (int, float)) is True
        ):
            return calc_entropy_bits_nrange(lst[0], lst[1])

        return calc_entropy_bits(lst)

    @staticmethod
    def _read_words_from_wordfile(inputfile: str) -> list:
        if isfile(inputfile) is False:
            raise FileNotFoundError('Input file does not exists: '
                                    '{}'.format(inputfile))

        return [
            word.strip() for word in open(inputfile, mode='rt')
        ]

    @staticmethod
    def _read_words_from_diceware(inputfile: str) -> list:
        if isfile(inputfile) is False:
            raise FileNotFoundError('Input file does not exists: '
                                    '{}'.format(inputfile))

        return [
            word.split()[1] for word in open(inputfile, mode='rt')
        ]

    def _get_password_characters(self) -> str:
        from string import (
            digits,
            ascii_lowercase,
            ascii_uppercase,
            punctuation
        )

        characters = ''

        if self.password_use_lowercase:
            characters += ascii_lowercase
        if self.password_use_uppercase:
            characters += ascii_uppercase
        if self.password_use_digits:
            characters += digits
        if self.password_use_punctuation:
            characters += punctuation

        return characters

    def import_words_from_file(self,
                               inputfile: str,
                               is_diceware: bool) -> None:
        if is_diceware is True:
            self.wordlist = self._read_words_from_diceware(inputfile)
        else:
            self.wordlist = self._read_words_from_wordfile(inputfile)

    def password_length_needed(self) -> int:
        """Calculate the needed password length to satisfy the entropy number
        for the given character set."""

        characters = self._get_password_characters()
        if (
            self.entropy_bits_req is None
            or not characters
        ):
            raise ValueError('Can\'t calculate the password length needed: '
                             'entropy_bits_req isn\'t set or the character '
                             'set is empty')

        return calc_password_length_needed(
            self.entropy_bits_req,
            characters
        )

    def words_amount_needed(self) -> int:
        """Calculate the needed amount of words to satisfy the entropy number
        for the given wordlist."""

        if (
            self.entropy_bits_req is None
            or self.amount_n is None
            or not self.wordlist
        ):
            raise ValueError('Cant\' calculate the words amount needed: '
                             'wordlist is empty or entropy_bits_req or '
                             'amount_n isn\'t set')

        # Thanks to @julianor for this tip to calculate default amount of
        # entropy: minbitlen/log2(len(wordlist)).
        # I set the minimum entropy bits and calculate the amount of words
        # needed, cosidering the entropy of the wordlist.
        # Then: entropy_w * amount_w + entropy_n * amount_n >= ENTROPY_BITS_MIN
        entropy_n = self.entropy_bits((self.randnum_min, self.randnum_max))

        # The entropy for EFF Large Wordlist is ~12.9, no need to calculate
        if self._external_wordlist is False:
            entropy_w = self._wordlist_entropy_bits
        else:
            entropy_w = self.entropy_bits(self.wordlist)

        return calc_words_amount_needed(
            self.entropy_bits_req,
            entropy_w,
            entropy_n,
            self.amount_n
        )

    def generate(self) -> list:
        """Generates a list of words randomly chosen from a wordlist."""

        if (
            self.amount_n is None
            or self.amount_w is None
            or not self.wordlist
        ):
            raise ValueError('Can\'t generate passphrase: '
                             'wordlist is empty or amount_n or '
                             'amount_w isn\'t set')

        passphrase = []
        for _ in range(0, self.amount_w):
            passphrase.append(randchoice(self.wordlist))

        for _ in range(0, self.amount_n):
            passphrase.append(randbetween(MIN_NUM, MAX_NUM))

        self.last_result = passphrase
        return passphrase

    def generate_password(self) -> list:
        """Generates a list of random characters."""

        password = []
        characters = self._get_password_characters()
        if (
            self.passwordlen is None
            or not characters
        ):
            raise ValueError('Can\'t generate password: character set is '
                             'empty or passwordlen isn\'t set')

        for _ in range(0, self.passwordlen):
            password.append(randchoice(characters))

        self.last_result = password
        return password

    def generate_uuid4(self) -> list:
        """Generates a list of parts of a UUID version 4 string.

        Usually, these parts are concatenated together using dashes.
        """

        # uuid4: 8-4-4-4-12: xxxxxxxx-xxxx-4xxx-{8,9,a,b}xxx-xxxxxxxxxxxx
        # instead of requesting small amounts of bytes, it's better to do it
        # for the full amount of them.
        hexstr = randhex(30)

        uuid4 = []
        uuid4.append(hexstr[:8])
        uuid4.append(hexstr[8:12])
        uuid4.append('4' + hexstr[12:15])
        uuid4.append('{:x}{}'.format(randbetween(8, 11), hexstr[15:18]))
        uuid4.append(hexstr[18:])

        self.last_result = uuid4
        return uuid4
