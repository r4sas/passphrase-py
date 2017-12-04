#  ***************************************************************************
#  This file is part of Passphrase:
#  A cryptographically secure passphrase and password generator
#  Copyright (C) <2017>  <Ivan Ariel Barrera Oro>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***************************************************************************

from unittest import TestCase
from random import randint
from uuid import UUID

from passphrase.passphrase import Passphrase
from passphrase.aux import Aux

WORDS = [
    'vivacious',
    'frigidly',
    'condiment',
    'passive',
    'reverse',
    'brunt'
]
WORDS_ENTROPY = 2.58
WORDS_FILE = '/tmp/words.list'
with open(WORDS_FILE, mode='wt', encoding='utf-8') as wordfile:
    wordfile.write('\n'.join(WORDS))

WORDSD = [
    '123456\tvivacious',
    '163456\tfrigidly',
    '153456\tcondiment',
    '143456\tpassive',
    '133456\tpenpal',
    '113456\talarm'
]
WORDSD_FILE = '/tmp/wordsd.list'
with open(WORDSD_FILE, mode='wt', encoding='utf-8') as wordfile:
    wordfile.write('\n'.join(WORDSD))


class TestValidInputs(TestCase):

    def test_init(self):
        passp = Passphrase()
        self.assertIsInstance(passp, Passphrase)
        self.assertIsNone(passp.wordlist)

        passp = Passphrase(WORDS_FILE, False)
        self.assertIsInstance(passp, Passphrase)
        self.assertEqual(passp.wordlist, WORDS)

        passp = Passphrase(WORDSD_FILE, True)
        self.assertIsInstance(passp, Passphrase)
        self.assertEqual(passp.wordlist, [word.split()[1] for word in WORDSD])

        passp = Passphrase('internal')
        self.assertIsInstance(passp, Passphrase)
        self.assertEqual(len(passp.wordlist), 7776)

    def test_entropy_bits(self):
        self.assertAlmostEqual(
            Passphrase.entropy_bits(WORDS),
            WORDS_ENTROPY,
            places=2
        )
        self.assertAlmostEqual(
            Passphrase.entropy_bits((10.1, 1005)),
            9.96,
            places=2
        )

    def test_generate(self):
        for _ in range(0, 1000):
            amount_w = randint(0, 10)
            amount_n = randint(0, 10)
            uppercase = randint(1, 5)
            passp = Passphrase()
            passp.load_internal_wordlist()
            passp.amount_w = amount_w
            passp.amount_n = amount_n
            p = passp.generate(uppercase)
            self.assertIsInstance(p, list)
            self.assertEqual(len(p), amount_w + amount_n)
            if amount_w > 0:
                # Perhaps it was requested just 1 word, and many uppercase
                # chars, but the word happens to be just 3 chars long...
                chars = sum(
                    len(w) if (
                        isinstance(w, str) and w.isalpha()
                    ) else 0 for w in p
                )
                if chars < uppercase:
                    self.assertTrue(str(p).isupper())
                else:
                    self.assertEqual(
                        Aux.uppercase_count(p),
                        uppercase
                    )
                passp.generate(0)
                self.assertTrue(str(passp).isupper())

                lowercase = randint(-5, -1)
                p = passp.generate(lowercase)
                chars = sum(
                    len(w) if (
                        isinstance(w, str) and w.isalpha()
                    ) else 0 for w in p
                )
                if chars < (lowercase * -1):
                    self.assertTrue(str(p).islower())
                else:
                    self.assertEqual(
                        Aux.lowercase_count(p),
                        lowercase * -1
                    )

    def test_generate_password(self):
        length = randint(0, 10)
        passp = Passphrase()
        passp.passwordlen = length
        p = passp.generate_password()
        self.assertIsInstance(p, list)
        self.assertEqual(len(p), length)

    def test_generate_uuid4(self):
        passp = Passphrase()
        p = passp.generate_uuid4()
        self.assertIsInstance(p, list)
        self.assertEqual(len(p), 5)
        passp.separator = ''
        uuid4 = UUID(str(passp), version=4)
        self.assertEqual(str(passp), uuid4.hex)

    def test_import_words_from_file(self):
        passp = Passphrase()

        ret = passp.import_words_from_file(WORDS_FILE, False)
        self.assertIsNone(ret)
        self.assertEqual(passp.wordlist, WORDS)

        ret = passp.import_words_from_file(WORDSD_FILE, True)
        self.assertIsNone(ret)
        self.assertEqual(passp.wordlist, [word.split()[1] for word in WORDSD])

    def test_password_length_needed(self):
        passp = Passphrase()
        passp.entropy_bits_req = 128
        p_len = passp.password_length_needed()
        self.assertEqual(p_len, 20)

    def test_words_amount_needed(self):
        passp = Passphrase()
        passp.load_internal_wordlist()
        passp.entropy_bits_req = 77
        passp.amount_n = 0
        w = passp.words_amount_needed()
        self.assertEqual(w, 6)

        passp.import_words_from_file(WORDS_FILE, False)
        w = passp.words_amount_needed()
        self.assertEqual(w, 30)

    def test_entropy_bits_req(self):
        passp = Passphrase()
        passp.entropy_bits_req = 1
        self.assertEqual(passp.entropy_bits_req, 1)

    def test_randnum_min(self):
        passp = Passphrase()
        passp.randnum_min = 1
        self.assertEqual(passp.randnum_min, 1)

    def test_randnum_max(self):
        passp = Passphrase()
        passp.randnum_max = 1
        self.assertEqual(passp.randnum_max, 1)

    def test_amount_w(self):
        passp = Passphrase()
        passp.amount_w = 1
        self.assertEqual(passp.amount_w, 1)

    def test_amount_n(self):
        passp = Passphrase()
        passp.amount_n = 1
        self.assertEqual(passp.amount_n, 1)

    def test_passwordlen(self):
        passp = Passphrase()
        passp.passwordlen = 1
        self.assertEqual(passp.passwordlen, 1)

    def test_wordlist(self):
        passp = Passphrase()
        passp.wordlist = WORDS
        self.assertEqual(passp.wordlist, list(WORDS))

    def test_to_string(self):
        passp = Passphrase()
        passp.load_internal_wordlist()
        p = str(passp)
        self.assertEqual(len(p), 0)
        passp.amount_n = 1
        passp.amount_w = 1
        passp.generate()
        p = str(passp)
        self.assertIsInstance(p, str)
        self.assertTrue(len(p) > 0)

    def test_load_internal_wordlist(self):
        passp = Passphrase()
        self.assertIsNone(passp.wordlist)
        passp.load_internal_wordlist()
        self.assertTrue(passp.wordlist)
        self.assertEqual(len(passp.wordlist), 7776)

    def test_make_chars_uppercase(self):
        string = 'The quick brown fox jumps over the lazy dog 123456'
        upperstart = Aux.uppercase_count(string)
        uppercase = randint(0, 10)
        for _ in range(0, 1000):
            strupper = Passphrase.make_chars_uppercase(string, uppercase)
            self.assertIsInstance(strupper, str)
            self.assertEqual(
                Aux.uppercase_count(strupper),
                uppercase + upperstart
            )

        lst = list(string)
        lstupper = Passphrase.make_chars_uppercase(lst, uppercase)
        self.assertIsInstance(lstupper, list)
        self.assertEqual(
            Aux.uppercase_count(lstupper),
            uppercase + upperstart
        )

        uppercase = len(string) * 2
        strupper = Passphrase.make_chars_uppercase(string, uppercase)
        self.assertIsInstance(strupper, str)
        self.assertTrue(strupper.isupper())

        uppercase = randint(0, 2)
        lst = (
            [
                [[], ['b']],
                ['a'],
                {12, 'bsh', 0},
                ('f', 1, 2, 3, ((3, 4, ['v', 'bjk']), (['a', 4, 'p'])))
            ]
        )
        lstupper = Passphrase.make_chars_uppercase(lst, uppercase)
        self.assertIsInstance(lstupper, type(lst))
        self.assertEqual(
            Aux.uppercase_count(lstupper),
            uppercase
        )

    def test_generated_password_entropy(self):
        passp = Passphrase()
        passp.passwordlen = 1
        self.assertAlmostEqual(
            passp.generated_password_entropy(),
            6.55,
            places=2
        )

    def test_generated_passphrase_entropy(self):
        passp = Passphrase('internal')
        passp.amount_n = 1
        passp.amount_w = 1
        self.assertAlmostEqual(
            passp.generated_passphrase_entropy(),
            32.70,
            places=2
        )


class TestInvalidInputs(TestCase):

    def test_init(self):
        self.assertRaises(
            FileNotFoundError,
            Passphrase,
            'nonexistent.file'
        )
        self.assertRaises(
            FileNotFoundError,
            Passphrase,
            'nonexistent.file',
            True
        )

    def test_entropy_bits(self):
        wrongtypes = (
            {1, 2},
            {'a': 1, 'b': 2},
            'aaaa',
            (1, 2, (3, 4)),
            {1, 2, 3, 4},
            1,
            1.1
        )
        for t in wrongtypes:
            self.assertRaises(
                TypeError,
                Passphrase.entropy_bits,
                t
            )
        self.assertRaises(
            ValueError,
            Passphrase.entropy_bits,
            (-1, 0)
        )

    def test_import_words_from_file(self):
        passp = Passphrase()
        self.assertRaises(
            FileNotFoundError,
            passp.import_words_from_file,
            'nonexistent.file',
            False
        )
        self.assertRaises(
            FileNotFoundError,
            passp.import_words_from_file,
            'nonexistent.file',
            True
        )

    def test_password_length_needed(self):
        passp = Passphrase()
        wrongtypes = (
            {1, 2},
            {'a': 1, 'b': 2},
            'aaaa',
            (1, 2, (3, 4)),
            {1, 2, 3, 4},
            [],
            ()
        )
        for t in wrongtypes:
            passp._entropy_bits_req = t
            with self.assertRaises(TypeError) as ct:
                passp.password_length_needed()
            self.assertIn(
                'entropybits can only be int or float',
                str(ct.exception)
            )

        passp._entropy_bits_req = -1
        with self.assertRaises(ValueError) as ct:
            passp.password_length_needed()
        self.assertIn(
            'entropybits should be greater than 0',
            str(ct.exception)
        )

    def test_entropy_bits_req(self):
        passp = Passphrase()
        wrongtypes = (
            {1, 2},
            {'a': 1, 'b': 2},
            'aaaa',
            (1, 2, (3, 4)),
            {1, 2, 3, 4},
            [],
            ()
        )
        for t in wrongtypes:
            with self.assertRaises(TypeError) as ct:
                passp.entropy_bits_req = t
            self.assertIn(
                'entropy_bits_req can only be int or float',
                str(ct.exception)
            )
        with self.assertRaises(ValueError) as ct:
            passp.entropy_bits_req = -1
        self.assertIn(
            'entropy_bits_req should be greater than 0',
            str(ct.exception)
        )

    def test_randnum_min(self):
        passp = Passphrase()
        wrongtypes = (
            {1, 2},
            {'a': 1, 'b': 2},
            'aaaa',
            (1, 2, (3, 4)),
            {1, 2, 3, 4},
            [],
            (),
            1.1
        )
        for t in wrongtypes:
            with self.assertRaises(TypeError) as ct:
                passp.randnum_min = t
            self.assertIn(
                'randnum_min can only be int',
                str(ct.exception)
            )
        with self.assertRaises(ValueError) as ct:
            passp.randnum_min = -1
        self.assertIn(
            'randnum_min should be greater than 0',
            str(ct.exception)
        )

    def test_randnum_max(self):
        passp = Passphrase()
        wrongtypes = (
            {1, 2},
            {'a': 1, 'b': 2},
            'aaaa',
            (1, 2, (3, 4)),
            {1, 2, 3, 4},
            [],
            (),
            1.1
        )
        for t in wrongtypes:
            with self.assertRaises(TypeError) as ct:
                passp.randnum_max = t
            self.assertIn(
                'randnum_max can only be int',
                str(ct.exception)
            )
        with self.assertRaises(ValueError) as ct:
            passp.randnum_max = -1
        self.assertIn(
            'randnum_max should be greater than 0',
            str(ct.exception)
        )

    def test_amount_w(self):
        passp = Passphrase()
        wrongtypes = (
            {1, 2},
            {'a': 1, 'b': 2},
            'aaaa',
            (1, 2, (3, 4)),
            {1, 2, 3, 4},
            [],
            (),
            1.1
        )
        for t in wrongtypes:
            with self.assertRaises(TypeError) as ct:
                passp.amount_w = t
            self.assertIn(
                'amount_w can only be int',
                str(ct.exception)
            )
        with self.assertRaises(ValueError) as ct:
            passp.amount_w = -1
        self.assertIn(
            'amount_w should be greater than 0',
            str(ct.exception)
        )

    def test_amount_n(self):
        passp = Passphrase()
        wrongtypes = (
            {1, 2},
            {'a': 1, 'b': 2},
            'aaaa',
            (1, 2, (3, 4)),
            {1, 2, 3, 4},
            [],
            (),
            1.1
        )
        for t in wrongtypes:
            with self.assertRaises(TypeError) as ct:
                passp.amount_n = t
            self.assertIn(
                'amount_n can only be int',
                str(ct.exception)
            )
        with self.assertRaises(ValueError) as ct:
            passp.amount_n = -1
        self.assertIn(
            'amount_n should be greater than 0',
            str(ct.exception)
        )

    def test_passwordlen(self):
        passp = Passphrase()
        wrongtypes = (
            {1, 2},
            {'a': 1, 'b': 2},
            'aaaa',
            (1, 2, (3, 4)),
            {1, 2, 3, 4},
            [],
            (),
            1.1
        )
        for t in wrongtypes:
            with self.assertRaises(TypeError) as ct:
                passp.passwordlen = t
            self.assertIn(
                'passwordlen can only be int',
                str(ct.exception)
            )
        with self.assertRaises(ValueError) as ct:
            passp.passwordlen = -1
        self.assertIn(
            'passwordlen should be greater than 0',
            str(ct.exception)
        )

    def test_wordlist(self):
        passp = Passphrase()
        wrongtypes = (
            {1, 2},
            {'a': 1, 'b': 2},
            'aaaa',
            {1, 2, 3, 4},
            1.1,
            1
        )
        for t in wrongtypes:
            with self.assertRaises(TypeError) as ct:
                passp.wordlist = t
            self.assertIn(
                'wordlist can only be list or tuple',
                str(ct.exception)
            )

    def test_generate(self):
        passp = Passphrase()
        self.assertRaises(ValueError, passp.generate)
        passp.amount_n = 0
        self.assertRaises(ValueError, passp.generate)
        passp.amount_w = 0
        self.assertRaises(ValueError, passp.generate)
        passp.load_internal_wordlist()
        self.assertEqual(passp.generate(), [])

        wrongtypes = (
            {1, 2},
            {'a': 1, 'b': 2},
            'aaaa',
            {1, 2, 3, 4},
            (1, 2),
            [1, 2],
            1.2
        )
        for t in wrongtypes:
            self.assertRaises(TypeError, passp.generate, t)

    def test_make_chars_uppercase(self):
        wrongtypes = (
            {'a': 1, 'b': 2},
            1.2,
            1
        )
        for t in wrongtypes:
            self.assertRaises(TypeError, Passphrase.make_chars_uppercase, t, 0)

        wrongtypes = (
            {1, 2},
            {'a': 1, 'b': 2},
            'aaaa',
            {1, 2, 3, 4},
            (1, 2),
            [1, 2],
            1.2
        )
        for t in wrongtypes:
            self.assertRaises(
                TypeError, Passphrase.make_chars_uppercase,
                [],
                t
            )
        self.assertRaises(ValueError, Passphrase.make_chars_uppercase, [], -1)

    def test_generated_password_entropy(self):
        pass

    def test_generated_passphrase_entropy(self):
        pass
