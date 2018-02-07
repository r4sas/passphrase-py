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

"""Passphrase - Generates cryptographically secure passphrases and passwords

Passphrases are built by picking from a word list using cryptographically
secure random number generator. Passwords are built from printable characters.
by HacKan (https://hackan.net) under GNU GPL v3.0+
"""

from sys import version_info, exit as sys_exit
from os import strerror as os_strerror
import argparse
from .settings import ENTROPY_BITS_MIN, SYSTEM_ENTROPY_BITS_MIN
from .passphrase import Passphrase
from .aux import Aux

__author__ = 'HacKan'
__license__ = 'GNU GPL 3.0+'
__version__ = '1.0.0rc2'
__version_string__ = (
    'Passphrase v{}\nby HacKan (https://hackan.net) FOSS '
    'under GNU GPL v3.0 or newer'.format(__version__)
)

assert (version_info >= (3, 2)), 'This script requires Python 3.2+'


def bigger_than_zero(value: int) -> int:
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(
            '{} should be bigger than 0'.format(ivalue)
        )
    return ivalue


def main():
    passphrase = Passphrase()

    # Set defaults
    passphrase.entropy_bits_req = ENTROPY_BITS_MIN
    passwordlen_default = passphrase.password_length_needed()
    amount_n_default = 0
    passphrase.amount_n = amount_n_default
    # To avoid loading the wordlist unnecessarily, I'm hardcoding this value
    # It's ok, it's only used to show help information
    amount_w_default = 6

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='{version_string}\n\n'
        'Generates a cryptographically secure passphrase, based on '
        'a wordlist, or a\npassword, and prints it to standard output.\n'
        'By default, it uses an embedded EFF Large Wordlist for passphrases.\n'
        'Passphrases with less than {wordsamountmin} words are considered '
        'insecure. A safe bet is \nbetween {wordsamountmin} and 7 words, '
        'plus at least a number.\n'
        'For passwords, use at least {passwdmin} characters, but prefer '
        '{passwdpref} or more, using the\ncomplete characters set.\n\n'
        'Instead of words and numbers, a password (random string of '
        'printable\ncharacters from Python String standard) can be generated '
        'by\n-p | --password, specifying the length. It uses uppercase, '
        'lowercase, digits\nand punctuation characters unless otherwise '
        'specified.\n'
        'Also, a UUID v4 string can be generated by --uuid4.\n'
        'A custom wordlist can be specified by -i | --input, the format must '
        'be: \nsingle column, one word per line. If -d | --diceware is used, '
        'the input\nfile is treated as a diceware wordlist (two columns).'
        '\nOptionally, -o | --output can be used to specify an output file '
        '(existing \nfile is overwritten).\n'
        'The number of words is {wordsamountmin} by default, but it '
        'can be changed by -w | --words.\n'
        'The number of numbers is {numsamountmin} by default, but it can be '
        'changed by\n-n | --numbers. The generated numbers are between '
        '{minnum} and {maxnum}.\n'
        'The default separator is a blank space, but any character or '
        'character\nsequence can be specified by -s | --separator.\n'
        '\nExample output:\n'
        '\tDefault parameters:\tchalice sheath postcard modular cider size\n'
        '\tWords=3, Numbers=2:\tdepraved widow office 184022 320264\n'
        '\tPassword, 20 chars:\tsF#s@B+iR#ZIL-yUWKPR'.format(
            version_string=__version_string__,
            minnum=passphrase.randnum_min,
            maxnum=passphrase.randnum_max,
            wordsamountmin=amount_w_default,
            numsamountmin=amount_n_default,
            passwdmin=passwordlen_default,
            passwdpref=passwordlen_default + 4
        )
    )

    parser.add_argument(
        '--version',
        action='store_true',
        help='print program version and licensing information and exit'
    )
    parser.add_argument(
        '--insecure',
        action='store_true',
        default=False,
        help="force password/passphrase generation even if the system's "
             "entropy is too low"
    )
    parser.add_argument(
        '--no-newline',
        action='store_true',
        default=False,
        help="don't print newline at the end of the passphrase/password"
    )
    parser.add_argument(
        '-m',
        '--mute',
        action='store_true',
        default=False,
        help="muted mode: it won't print output, only informational, warning "
             "or error messages (usefull with -o | --output)"
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        default=False,
        help='print additional information (can coexist with -m | --mute)'
    )
    parser.add_argument(
        '-e',
        '--entropybits',
        type=bigger_than_zero,
        default=ENTROPY_BITS_MIN,
        help='specify the number of bits to use for entropy calculations '
             '(defaults to {})'.format(ENTROPY_BITS_MIN)
    )
    parser.add_argument(
        '--uuid4',
        action='store_true',
        default=False,
        help='generate an UUID v4 string'
    )
    parser.add_argument(
        '-p',
        '--password',
        type=bigger_than_zero,
        const=-1,
        nargs='?',
        help='generate a password of the specified length from all printable '
             'or selected characters'
    )
    parser.add_argument(
        '--use-uppercase',
        type=bigger_than_zero,
        const=0,
        nargs='?',
        help='use uppercase characters for password generation or give the '
             'amount of uppercase characters in the passphrase: zero or no '
             'input for all uppercase or any number of uppercase '
             'characters wanted (the rest are lowercase)'
    )
    parser.add_argument(
        '--use-lowercase',
        type=bigger_than_zero,
        const=0,
        nargs='?',
        help='use lowercase characters for password generation or give the '
             'amount of lowercase characters in the passphrase: zero or no '
             'input for all lowercase (default) or any number of lowercase '
             'characters wanted (the rest are uppercase)'
    )
    parser.add_argument(
        '--use-digits',
        action='store_true',
        default=False,
        help='use digits for password generation'
    )
    parser.add_argument(
        '--use-alphanumeric',
        action='store_true',
        default=False,
        help='use lowercase and uppercase characters, and digits for password '
             'generation (equivalent to --use-lowercase --use-uppercase '
             '--use-digits)'
    )
    parser.add_argument(
        '--use-punctuation',
        action='store_true',
        default=False,
        help='use punctuation characters for password generation'
    )
    parser.add_argument(
        '-w',
        '--words',
        type=bigger_than_zero,
        help='specify the amount of words (0 or more)'
    )
    parser.add_argument(
        '-n',
        '--numbers',
        type=bigger_than_zero,
        default=amount_n_default,
        help='specify the amount of numbers (0 or more)'
    )
    parser.add_argument(
        '-s',
        '--separator',
        type=str,
        default=' ',
        help='specify a separator character (space by default)'
    )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        help='specify an output file (existing file is overwritten)'
    )
    parser.add_argument(
        '-i',
        '--input',
        type=str,
        help='specify an input file (it must have the following format: '
             'single column, one word per line)'
    )
    parser.add_argument(
        '-d',
        '--diceware',
        action='store_true',
        default=False,
        help='specify input file as a diceware list (format: two colums)'
    )

    args = parser.parse_args()

    inputfile = args.input
    outputfile = args.output
    separator = args.separator
    is_diceware = args.diceware
    passwordlen = args.password
    amount_w = args.words
    amount_n = args.numbers
    show_version = args.version
    mute = args.mute
    verbose = args.verbose
    no_newline = args.no_newline
    gen_uuid4 = args.uuid4
    p_uppercase = args.use_uppercase
    p_lowercase = args.use_lowercase
    p_digits = args.use_digits
    p_punctuation = args.use_punctuation
    p_alphanumeric = args.use_alphanumeric
    entropy_bits = args.entropybits
    gen_insecure = args.insecure

    if show_version:
        print(__version_string__)
        sys_exit()

    if verbose:
        Aux.print_stderr(__version_string__)

    # Check system entropy
    system_entropy = Aux.system_entropy()
    if system_entropy < SYSTEM_ENTROPY_BITS_MIN:
        Aux.print_stderr(
            'Warning: the system has too little entropy: {} bits; randomness '
            'quality could be poor'.format(system_entropy)
        )
        if not gen_insecure:
            Aux.print_stderr(
                'Error: system entropy too low: {system_entropy} '
                '< {system_entropy_min}'.format(
                    system_entropy=system_entropy,
                    system_entropy_min=SYSTEM_ENTROPY_BITS_MIN
                )
            )
            sys_exit(1)

    if verbose:
        Aux.print_stderr(
            'Using {} bits of entropy for calculations (if any). The minimum '
            'recommended is {}'.format(entropy_bits, ENTROPY_BITS_MIN)
        )

    # Check selected entropy
    check_chosen_entropy = False if gen_uuid4 else not (
        amount_n and amount_w and passwordlen is None
    )
    if check_chosen_entropy and entropy_bits < ENTROPY_BITS_MIN:
        Aux.print_stderr(
            'Warning: insecure number of bits for entropy calculations '
            'chosen! Should be bigger than {}'.format(ENTROPY_BITS_MIN)
        )
    passphrase.entropy_bits_req = entropy_bits

    # Generate whatever is requested
    if gen_uuid4:
        # Generate uuid4
        gen_what = 'UUID v4'
        gen_ent = 133.78

        if verbose:
            Aux.print_stderr('Generating UUID v4')
        passphrase.generate_uuid4()
        passphrase.separator = '-'
    elif passwordlen is not None:
        # Generate a password
        gen_what = 'password'

        p_uppercase = True if p_uppercase is not None else False
        p_lowercase = True if p_lowercase is not None else False
        if (
                p_uppercase
                or p_lowercase
                or p_digits
                or p_punctuation
                or p_alphanumeric
        ):
            passphrase.password_use_uppercase = (p_uppercase or p_alphanumeric)
            passphrase.password_use_lowercase = (p_lowercase or p_alphanumeric)
            passphrase.password_use_digits = (p_digits or p_alphanumeric)
            passphrase.password_use_punctuation = p_punctuation

        min_len = passphrase.password_length_needed()
        if passwordlen < 1:
            passwordlen = min_len
        elif passwordlen < min_len:
            Aux.print_stderr(
                'Warning: insecure password length chosen! Should be bigger '
                'than or equal to {}'.format(min_len)
            )

        passphrase.passwordlen = passwordlen
        gen_ent = passphrase.generated_password_entropy()

        if verbose:
            verbose_string = (
                'Generating password of {} characters long '
                'using '.format(passwordlen)
            )
            verbose_string += (
                'uppercase characters, ' if (
                    passphrase.password_use_uppercase or p_alphanumeric
                ) else ''
            )
            verbose_string += (
                'lowercase characters, ' if (
                    passphrase.password_use_lowercase or p_alphanumeric
                ) else ''
            )
            verbose_string += (
                'digits, ' if (
                    passphrase.password_use_digits or p_alphanumeric
                ) else ''
            )
            verbose_string += (
                'punctuation characters, ' if (
                    passphrase.password_use_punctuation
                ) else ''
            )
            Aux.print_stderr(
                verbose_string[:-2] if (
                    verbose_string[-2:] == ', '
                ) else verbose_string
            )

        passphrase.generate_password()
        passphrase.separator = ''
    else:
        # Generate a passphrase
        gen_what = 'passphrase'

        # Read wordlist if indicated
        try:
            if inputfile is None:
                passphrase.load_internal_wordlist()
            else:
                try:
                    passphrase.import_words_from_file(inputfile, is_diceware)

                except IOError as ioerr:
                    Aux.print_stderr(
                        "Error: file {} can't be opened or read, reason: "
                        "{}".format(
                            inputfile,
                            os_strerror(ioerr.errno)
                        )
                    )
                    sys_exit(1)

        except FileNotFoundError as err:
            Aux.print_stderr('Error: {}'.format(err))
            sys_exit(1)

        passphrase.amount_n = amount_n
        amount_w_good = passphrase.words_amount_needed()
        if amount_w is None:
            amount_w = amount_w_good
        elif amount_w < amount_w_good:
            Aux.print_stderr(
                'Warning: insecure amount of words chosen! Should be '
                'bigger than or equal to {}'.format(amount_w_good)
            )

        passphrase.amount_w = amount_w
        gen_ent = passphrase.generated_passphrase_entropy()

        if verbose:
            Aux.print_stderr(
                'Generating a passphrase of {} words and {} '
                'numbers using {}'.format(
                    amount_w,
                    amount_n,
                    'internal wordlist' if inputfile is None else (
                        'external wordlist: ' + inputfile + (
                            ' (diceware-like)' if is_diceware else ''
                        )
                    )
                )
            )

        case = (-1 * p_lowercase) if p_lowercase else p_uppercase
        passphrase.generate(case)
        passphrase.separator = separator

    if verbose:
        Aux.print_stderr(
            'The entropy of this {what} is {ent:.2f} bits'.format(
                what=gen_what,
                ent=gen_ent
            )
        )

    if gen_ent < ENTROPY_BITS_MIN:
        Aux.print_stderr('Warning: the {} is too short!'.format(gen_what))

    if not mute:
        if no_newline:
            print(passphrase, end='')
        else:
            print(passphrase)

    if outputfile is not None:
        # ensure path to file exists or create
        from os.path import dirname as os_path_dirname
        from os import makedirs as os_makedirs

        os_makedirs(os_path_dirname(outputfile), exist_ok=True)

        try:
            with open(outputfile, mode='wt', encoding='utf-8') as outfile:
                linefeed = '' if no_newline else '\n'
                outfile.write(str(passphrase) + linefeed)

        except IOError as ioerr:
            Aux.print_stderr(
                "Error: file {} can't be opened or written, reason: "
                "{}".format(
                    outputfile,
                    os_strerror(ioerr.errno)
                )
            )
            sys_exit(1)


if __name__ == '__main__':
    main()
