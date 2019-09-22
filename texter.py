import argparse
from typing import Optional, List, Match, Pattern, Any
from hashlib import md5
from _hashlib import HASH
import os
import re
from pathlib import Path
import sys
from binascii import b2a_base64, a2b_base64
import functools

# Usage:
#
#   python texter.py b2a --dir=data --stem=billet --input=input_file
#   python texter.py a2b --dir=data --stem=billet --output=output_file

ACTIONS = {'b2a', 'a2b'}
INDEX_FIELD_LENGTH = 6    # Can be changed
TOTAL_FIELD_LENGTH = 6    # Can be changed
DEFAULT_LINE_WIDTH = 60   # Can be changed
DEFAULT_MAX_CHAR = 1024   # Can be changed
DEFAULT_OUTPUT_DIR = '.'  # Can be changed
DEFAULT_STEM = 'part'     # Can be changed
MD5_FIELD_LENGTH = 32


ChunkInstance = Any
ChunkContainerIdInstance = Any


class Document:
    """This class represents the document to convert.
    """

    def __init__(self, data: str, line_width: int):
        """Create a document.

        :param data: the document content.
        :param line_width: number of characters on a line of text.
        """
        self._data = data
        self._line_width = line_width
        self._current_index = 0

    def shift(self, length: int) -> str:
        """Extract a given number of characters from the document.

        :param length: the number of characters to extract.
        :return: the extracted characters.
        """
        result: str = ''
        total = 0
        line_pos = 0
        line_nb_chars = self._line_width - len(os.linesep)
        while total < length:
            if self.reminder == 0:
                return result
            if line_pos < line_nb_chars:
                result += self._data[0:1][0]
                self._data = self._data[1:]
                if self.reminder == 0:
                    return result
                total += 1
                self._current_index += 1
                line_pos += 1
                continue
            result += os.linesep
            total += len(os.linesep)
            line_pos = 0
        return result

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def reminder(self) -> int:
        return len(self._data)


class Chunk:
    """A chunk of document.
    """

    def __init__(self, chunk: str, fingerprint: Optional[str] = None):
        """Create a document part.

        :param chunk: a chunk of document.
        Please keep in mind that the chunk is a multiline string. All lines
        have the same length, except, eventually, the last one.
        :param fingerprint: the chunk fingerprint.
        This parameter is optional. If it is not specified, that it is
        calculated.
        """
        self._chunk_str = chunk
        self._chunk_bytes = chunk.encode()
        if fingerprint is None:
            fingerprint_hash: HASH = md5(self._chunk_bytes)
            self._fingerprint = fingerprint_hash.hexdigest()
        else:
            self._fingerprint = fingerprint

    @property
    def as_string(self) -> str:
        """The part chunk as a string.

        :return: the part chunk.
        """
        return self._chunk_str

    @property
    def as_bytes(self) -> bytes:
        """The part chunk as a sequence of bytes.

        :return: the part chunk as a sequence of bytes.
        """
        return self._chunk_bytes

    @property
    def fingerprint(self) -> str:
        """The chunk fingerprint.

        :return: the chunk fingerprint.
        """
        return self._fingerprint

    @staticmethod
    def get_instance(path: str) -> ChunkInstance:
        """Create a "Part" from the content of a file.

        :param path: path to the file.
        :return: an instance of Part.
        """
        input_part = Path(path)
        text = input_part.read_text()
        data = text.split(os.linesep)
        if len(data) < 5:
            raise Exception(f'Invalid part "{path}"!')

        # N: the total number of lines.
        # M: N-1
        #
        # Line 1: the part index (within the list of parts).
        # Line 2: the total number of parts.
        # line 3: the part fingerprint.
        # line 4: the boundary.
        # line 5: the first line of the data part.
        # ...
        # line M: the last line of the data part.
        # line N: the boundary.

        expected_fingerprint = data[2]
        boundary1 = data[3]
        boundary2 = data[len(data) - 1]
        if not Chunk._boundary_valid(boundary1):
            raise Exception(f'Invalid part "{path}": unexpected boundary '
                            f'"{boundary1}".')
        if not Chunk._boundary_valid(boundary2):
            raise Exception(f'Invalid part "{path}": unexpected boundary '
                            f'"{boundary2}".')
        chunk = ''.join(data[4:len(data)-1])
        fingerprint: HASH = md5(os.linesep.join(data[4:len(data)-1]).encode())
        fingerprint_hex = fingerprint.hexdigest()
        if fingerprint_hex != expected_fingerprint:
            raise Exception(f'Invalid part "{path}"! Fingerprints don\'t match.')
        return Chunk(chunk, fingerprint_hex)

    @staticmethod
    def _boundary_valid(boundary: str) -> bool:
        """Test whether a chunk boundary is valid or not.

        :param boundary: the boundary to check.
        :return: if the boundary is valid, then the method returns the value
        True. Otherwise, it returns the value False.
        """
        breg: Pattern = re.compile('^-+$')
        return breg.match(boundary) is not None


class ChunkContainerId:
    def __init__(self, stem: str, index: int, count: int, dir: str):
        """Create a chunk container ID.

        A chunk container is designed by the following elements:
        - a stem.
        - the index of the chuck within the list of chunks.
        - the total number of chunks.
        - the path to the file that contains the chunk.

        :param stem: chunk "stem".
        :param index: the index of the chuck within the list of chunks.
        :param count: the total number of chunks.
        :param dir: the directory that contains the file which content is the
        chunk.
        """
        if index > count:
            raise Exception(f'Index is greater than the total count ({index} > {count})')

        self._stem = stem
        self._index = index
        self._count = count
        self._dir = dir
        self._basename = f'{stem}-{index}-{count}.part'
        self._path = os.path.join(self._dir, self._basename)

    @property
    def stem(self) -> str:
        """The stem.

        :return: the chunk "stem".
        """
        return self._stem

    @property
    def index(self) -> int:
        """The position of the chunk within the list of chunks.

        :return: the position of the chunk within the list of chunks.
        """
        return self._index

    @property
    def count(self) -> int:
        """The total number of chunks.

        :return: the total number of chunks.
        """
        return self._count

    @property
    def basename(self) -> str:
        """The basename of the file that contains the chunk.

        :return: the basename of the file that contains the chunk.
        """
        return self._basename

    @property
    def path(self) -> str:
        """The path of the file that contains the chunk.

        :return: the path of the file that contains the chunk.
        """
        return self._path

    @staticmethod
    def cmp(left, right) -> int:
        """Compare the position of 2 chunks within the list of chunks.

        :param left: the first chunk to compare.
        :param right: the second chunk to compare.
        :return: the method may return one of the following values: -1, +1 or 0.
        If the left chunk is prior to the right chunk within the
        list of chunks, then the method returns the value -1.
        If the left chunk is after to the right chunk within the
        list of chunks, then the method returns the value +1.
        Otherwise, the method returnd the value 0
        """
        left: ChunkContainerId
        right: ChunkContainerId
        if left.stem != right.stem:
            raise Exception(f'Cannot compare "{left.basename}" with {right.basename}!')
        if left.count != right.count:
            raise Exception(f'Cannot compare "{left.basename}" with {right.basename}!')
        if left.index > right.index:
            return 1
        if left.index < right.index:
            return -1
        return 0

    @staticmethod
    def get_instance(stem: str,
                     path: str) -> Optional[ChunkContainerIdInstance]:
        """Create a chunk container ID from a file path.

        :param stem: the chunk stem.
        :param path: path to the file.
        :return: if the name of the file identifies a chunk container,
        the the method returns an instance of ChunkContainerId. Otherwise,
        it returns the value None.
        """
        suffix_re: Pattern = re.compile('^(?P<stem>[a-z_.0-9]+)-'
                                        '(?P<index>\\d+)-'
                                        '(?P<count>\\d+)\\.part$')
        dir = os.path.dirname(path)
        basename = os.path.basename(path)
        tokens: Match = suffix_re.match(basename)
        if tokens is None:
            return None
        if tokens['stem'] != stem:
            return None
        return ChunkContainerId(tokens['stem'],
                                int(tokens['index']),
                                int(tokens['count']),
                                dir)


def b2a(input_file: str,
        stem: str,
        max_char: int) -> int:
    """Convert an input file into a series of ASCII files (called "parts").

    :param input_file: the input file to convert.
    :param stem: the parts stem.
    :param max_char: the maximum size (in bytes) of a part.
    :return: the number of created parts.
    """

    min_width = len(os.linesep)
    if DEFAULT_LINE_WIDTH < min_width:
        print(f"The maximum length of a line must be greater than {min_width}.")
        sys.exit(1)

    # Load the input file.
    try:
        input_bytes: bytes = Path(input_file).read_bytes()
    except Exception as e:
        print(e.__str__())
        sys.exit(1)

    input_text: str = b2a_base64(input_bytes, newline=False).decode()
    document = Document(input_text, DEFAULT_LINE_WIDTH)

    container: List[Chunk] = []
    cr_length = len(os.linesep)
    header_length = INDEX_FIELD_LENGTH + TOTAL_FIELD_LENGTH + MD5_FIELD_LENGTH +\
        (DEFAULT_LINE_WIDTH - cr_length) + 4 * cr_length
    footer_length = DEFAULT_LINE_WIDTH - cr_length

    if max_char < header_length + footer_length:
        print(f'You must specify a maximum number of characters greater than {header_length}.')
        sys.exit(1)

    # We subtract len(os.linesep), because the body is followed by one new line
    # character.
    chunk_size = max_char - header_length - footer_length - len(os.linesep)

    while True:
        text = document.shift(chunk_size)
        if not text:
            break
        container.append(Chunk(text))

    for part_number in range(1, len(container)+1):
        part = container[part_number-1]
        output_file = f'{stem}-{part_number}-{len(container)}.part'
        data = [
            f'{part_number}'.rjust(INDEX_FIELD_LENGTH, '0'),
            f'{len(container)}'.rjust(TOTAL_FIELD_LENGTH, '0'),
            part.fingerprint,
            '-' * (DEFAULT_LINE_WIDTH - len(os.linesep)),
            part.as_string,
            '-' * (DEFAULT_LINE_WIDTH - len(os.linesep))
        ]
        with open(output_file, 'w') as fd:
            fd.write("\n".join(data))
    return len(container)


def a2b(input_dir: str,
        stem: str,
        output_file: str):
    """Take a series of "parts" and generates the original file.

    :param input_dir: path to the directory that contains the "parts".
    :param stem: the parts stem.
    :param output_file: the path to the output file.
    """

    input_parts: List[ChunkContainerId] = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            path = os.path.abspath(os.path.join(root, file))
            chunk: ChunkContainerId = ChunkContainerId.get_instance(
                stem, path)
            if chunk is not None:
                input_parts.append(chunk)

    cmp = functools.cmp_to_key(ChunkContainerId.cmp)
    input_parts.sort(key=cmp)
    result: str = ''
    for part in input_parts:
        print(part.path)
        chunk: Chunk = Chunk.get_instance(part.path)
        result += chunk.as_string
    file_content = a2b_base64(result)
    with open(output_file, 'wb') as fd:
        fd.write(file_content)


actions = list(ACTIONS)
actions.sort()
if len(sys.argv) < 2:
    print(f'Missing action (valid actions are: {", ".join(actions)}).')
    sys.exit(1)

action: str = sys.argv[1]
if action not in ACTIONS:
    print(f'Invalid action specifier "{action}" (valid actions are: {", ".join(actions)}).')
    sys.exit(1)

args = sys.argv[2:]

# --------------------------------------------------------------
# Take an input file and cut it into chunks of ASCII characters.
# --------------------------------------------------------------

if action == 'b2a':
    parser = argparse.ArgumentParser(description='Convert a binary file into '
                                                 'a series of text files.')
    parser.add_argument('--input',
                        dest='input',
                        type=str,
                        required=True,
                        help='The input file.')
    parser.add_argument('--dir',
                        dest='dir',
                        type=str,
                        required=False,
                        default=DEFAULT_OUTPUT_DIR,
                        help='The output directory '
                             f'(default "{DEFAULT_OUTPUT_DIR}").')
    parser.add_argument('--stem',
                        dest='stem',
                        type=str,
                        required=False,
                        default=DEFAULT_STEM,
                        help='The output file stem '
                             f'(default "{DEFAULT_STEM}").')
    parser.add_argument('--max-char',
                        dest='max-char',
                        type=int,
                        required=False,
                        default=DEFAULT_MAX_CHAR,
                        help='The maximum number of character per output file.')

    args = parser.parse_args(args)
    output_dir = args.__getattribute__('dir')
    input_path = args.__getattribute__('input')
    stem = args.__getattribute__('stem')
    max_char = args.__getattribute__('max-char')
    output_stem = os.path.join(output_dir, stem)
    count = b2a(input_path, output_stem, max_char)
    print(f'Count: {count}')

# --------------------------------------------------------------
# Take a series of file parts and create a binary file from
# these parts.
# --------------------------------------------------------------

if action == 'a2b':
    parser = argparse.ArgumentParser(description='Convert a series of text '
                                                 'files into a binary file')
    parser.add_argument('--dir',
                        dest='dir',
                        type=str,
                        required=False,
                        default=DEFAULT_OUTPUT_DIR,
                        help='The stem directory '
                             f'(default "{DEFAULT_OUTPUT_DIR}").')
    parser.add_argument('--stem',
                        dest='stem',
                        type=str,
                        required=False,
                        default=DEFAULT_STEM,
                        help='The input files stem '
                             f'(default "{DEFAULT_STEM}")')
    parser.add_argument('--output',
                        dest='output',
                        type=str,
                        required=True,
                        help='The output file.')
    args = parser.parse_args(args)
    input_dir = args.__getattribute__('dir')
    input_stem = args.__getattribute__('stem')
    output_file = args.__getattribute__('output')
    a2b(input_dir, input_stem, output_file)

sys.exit(0)