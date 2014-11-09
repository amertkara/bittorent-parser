# -*- coding: utf-8 -*-
import time
import os


class BTParser:
    metadata = dict()
    _filename = ""
    _content = ""

    def __init__(self, filename, content=""):
        """ Initializes the object

            Args:
                filename (str): Path to the torrent file
                content (str): Overrides the torrent file if provided, allows passing bittorent data without a file
            Returns:
                None
        """
        self._filename = filename
        self._content = content

    def _open(self):
        """Opens the torrent file with the _filename provided in the object creation and writes the content
            to _content. The file is closed upon reading.

            Args:
                None
            Returns:
                None
            Raises:
                IOError
        """
        with open(self._filename, "rb") as f:
            self._content = f.read()

    def _parser(self, stream, position):
        """ Parses the given byte stream starting from the position marker.

            Uses the specifications provided: http://en.wikipedia.org/wiki/Bencode#Encoding_algorithm

            Args:
                stream (str): A byte stream (potentially _content) that contains a torrent file content
                position (int): Integer indicating the current position on the stream
            Returns:
                Depending on the next data structure (starting from position), it returns a tuple that contains:
                    0 : dict, list, int or str
                    1 : position after the returned data structure
            Raises:
                SyntaxError: When an unknown syntax is encountered, the bencode data structure is somewhat not right or
                    if ValueErrors are encountered during int conversions
        """
        result = None

        # Dictionaries start with a d
        if stream[position] == "d":
            d = dict()

            position += 1
            try:
                while stream[position] != "e":
                    key, position = self._parser(stream, position)
                    value, position = self._parser(stream, position)
                    d[key] = value
            except IndexError:
                raise SyntaxError("dictionary format is not correct, needs to be ended with 'e' at %d." % position)
            position += 1

            result = d
        # Lists start with a l
        elif stream[position] == "l":
            l = list()

            position += 1
            try:
                while stream[position] != "e":
                    element, position = self._parser(stream, position)
                    l.append(element)
            except IndexError:
                raise SyntaxError("list format is not correct, needs to be ended with 'e' at %d." % position)
            position += 1

            result = l
        # Integers start with an i
        elif stream[position] == "i":
            i = ""

            position += 1
            try:
                while stream[position] != "e":
                    i += stream[position]
                    position += 1
            except IndexError:
                raise SyntaxError("integer format is not correct, needs to be ended with 'e' at %d." % position)
            position += 1

            try:
                result = int(i, 10)
            except ValueError:
                raise SyntaxError("i<integer>e data structure is holding a non-integer value at %d." % position)
        # Byte streams start with an integer indicating the length
        elif stream[position].isdigit():
            separator = stream.find(":", position)

            try:
                length = int(stream[position:separator], 10)
            except ValueError:
                raise SyntaxError("string length is not an integer at position %d." % position)

            string = stream[separator+1:separator+length+1]
            position = separator + length + 1

            result = string
        else:
            raise SyntaxError("unknown data structure at position %d." % position)

        return result, position

    def get_content(self, spill=False):
        """ Gets the content of a bittorent file and loads the metadata dictionary to metadata variable.

            Checks if _content is actually a giant dictionary as it is part of the bittorent specification:
            http://en.wikipedia.org/wiki/Torrent_file#File_structure

            Args:
                spill (bool): Spills out the metadata dictionary
            Returns:
                metadata (dict): A dictionary that holds the entire bittorent content
            Raises:
                SyntaxError: if the bittorent file is not formatted properly
        """
        # Check if _content is already set
        if len(self._content) == 0:
            self._open()

        # Check if the content is a dictionary: d<content>e
        if self._content[0] is not "d" or self._content[-1] is not "e":
            raise SyntaxError("The torrent file needs to be a dictionary.")

        # Run the parser and set the metadata, assign position to a dummy variable _
        self.metadata, _ = self._parser(self._content, 0)

        if spill:
            print "Tracker URL: %s \nCreation Date: %s\nCreated by the client: %s" \
                  "\nComment: %s\nEncoding: %s\n" \
                  % (self.metadata.get("announce", ""),
                     time.strftime("%c", time.localtime(self.metadata.get("creation date", ""))),
                     self.metadata.get("created by", ""), self.metadata.get("comment", ""),
                     self.metadata.get("encoding", "")
                     )

            if self.metadata.get("info", None) is not None:
                print "Info:"
                print "Piece length: %s\nPieces (hexed): %s\n" \
                      % (self.metadata.get("info", dict()).get("piece length", ""),
                         self.metadata.get("info", dict()).get("pieces", "").encode("hex")
                         )

            if self.metadata.get("info", dict()).get("length", None) is not None:
                # Single file mode
                print "File:"
                print "Name: %s\nLength: %s\nmd5sum: %s" \
                      % (self.metadata.get("info", dict()).get("name", None),
                         self.metadata.get("info", dict()).get("length", None),
                         self.metadata.get("info", dict()).get("md5sum", None)
                         )

            if self.metadata.get("info", dict()).get("files", None) is not None:
                # Multiple file mode
                print "Files:"
                for f in self.metadata.get("info", dict()).get("files"):
                    print "Name: %s\nLength: %s\nmd5sum: %s\n" \
                          % (", ".join(f.get("path", list())),
                             f.get("length", None),
                             f.get("md5sum", None)
                             )

        return self.metadata

if __name__ == "__main__":
    parser = BTParser(os.path.join(os.path.dirname(__file__), "../tests/ubuntu-12.04.4-desktop-amd64.iso.torrent"))
    parser.get_content(True)