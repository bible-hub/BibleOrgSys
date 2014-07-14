#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# HebrewOldLexicon.py
#   Last modified: 2014-07-14 (also update ProgVersion below)
#
# Module handling the old Open Scriptures Hebrew lexicon
#
# Copyright (C) 2011-2014 Robert Hunt
# Author: Robert Hunt <robert316@users.sourceforge.net>
# License: See gpl-3.0.txt
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Module handling the OpenScriptures Hebrew lexicon
    which contains 10,761 entries.

Currently this version doesn't yet store (and return) many of the fields -- only usage and a couple of others.
"""

ProgName = "Old Hebrew Lexicon format handler"
ProgVersion = "0.08"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = False


import logging, os.path
from gettext import gettext as _
from collections import OrderedDict
from xml.etree.ElementTree import ElementTree

import Globals


class HebrewOldLexiconFileConverter:
    """
    Class for reading, validating, and converting HebrewOldLexicon.
    This is only intended as a transitory class (used at start-up).
    The HebrewOldLexicon class has functions more generally useful.
    """
    filenameBase = "HebrewOldLexicon"
    XMLNameSpace = "{http://www.w3.org/XML/1998/namespace}"
    HebLexNameSpace = "{http://www.APTBibleTools.com/namespace}"
    treeTag = HebLexNameSpace + "lexicon"
    textTag = HebLexNameSpace + "entry"
    headerTag = HebLexNameSpace + "header"
    divTag = HebLexNameSpace + "div"
    compulsoryAttributes = ()
    optionalAttributes = ()
    uniqueAttributes = compulsoryAttributes + optionalAttributes
    compulsoryElements = ( "nameEnglish", "referenceAbbreviation", "referenceNumber" )
    optionalElements = ( "expectedChapters", "SBLAbbreviation", "OSISAbbreviation", "SwordAbbreviation", "CCELNumber", "ParatextAbbreviation", "ParatextNumber", "NETBibleAbbreviation", "ByzantineAbbreviation", "possibleAlternativeBooks" )
    #uniqueElements = compulsoryElements + optionalElements
    uniqueElements = compulsoryElements # Relax the checking


    def __init__( self ):
        """
        Constructor: just sets up the Old Hebrew Lexicon file converter object.
        """
        self.title, self.version, self.date = None, None, None
        self.tree, self.header, self.entries = None, None, None
    # end of __init__


    def __str__( self ):
        """
        This method returns the string representation of a Old Hebrew Lexicon converter object.

        @return: the name of a Old Hebrew Lexicon converter object formatted as a string
        @rtype: string
        """
        result = "Old Hebrew Lexicon File Converter object"
        if self.title: result += ('\n' if result else '') + "  " + self.title
        if self.version: result += ('\n' if result else '') + "  " + _("Version: {} ").format( self.version )
        if self.date: result += ('\n' if result else '') + "  " + _("Date: {}").format( self.date )
        result += ('\n' if result else '') + "  " + _("Number of entries = {}").format( len(self.entries) )
        return result
    # end of __str__


    def loadAndValidate( self, XMLFolder ):
        """
        Load the source XML file and remove the header from the tree.
        Also, extracts some useful elements from the header element.
        """
        if Globals.verbosityLevel > 2: print( _("Loading from {}...").format( XMLFolder ) )
        self.XMLFolder = XMLFolder
        XMLFilepath = os.path.join( XMLFolder, "HebrewMesh.xml" )
        self.tree = ElementTree().parse( XMLFilepath )
        assert( len ( self.tree ) ) # Fail here if we didn't load anything at all

        self.entries = {}
        if self.tree.tag == HebrewOldLexiconFileConverter.treeTag:
            for entry in self.tree:
                self.validateEntry( entry )
        else: logging.error( "Expected to load '{}' but got '{}'".format( HebrewOldLexiconFileConverter.treeTag, self.tree.tag ) )
        if self.tree.tail is not None and self.tree.tail.strip(): logging.error( "Unexpected '{}' tail data after {} element".format( self.tree.tail, self.tree.tag ) )
    # end of loadAndValidate


    def validateEntry( self, entry ):
        """
        Check/validate the given OSIS div record.
        """
        # Process the entry attributes first
        entryID = None
        for attrib,value in entry.items():
            if attrib=="id":
                entryID = value
                if Globals.verbosityLevel > 2: print( "Validating {} entry...".format( entryID ) )
            else: logging.warning( "Unprocessed '{}' attribute ({}) in main entry element".format( attrib, value ) )

        entryResults = []
        for element in entry:
########### w
            if element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"w":
                word = element.text
                Globals.checkXMLNoTail( element, element.tag, "d4hg" )
                # Process the attributes
                pos = pron = xlit = src = lang = None
                for attrib,value in element.items():
                    if attrib=="pos": pos = value
                    elif attrib=="pron": pron = value
                    elif attrib=="xlit": xlit = value
                    elif attrib=="src": src = value
                    elif attrib==HebrewOldLexiconFileConverter.XMLNameSpace+"lang":
                        lang = value
                    else: logging.warning( "Unprocessed '{}' attribute ({}) in {}".format( attrib, value, element.tag ) )
                if word: entryResults.append( ('word', (word,pos,pron,xlit,src,), ) )
                # Now process the subelements
                for subelement in element.getchildren():
                    if subelement.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"w":
                        location = "w of w"
                        self.w = subelement.text
                        tail = subelement.tail
                        Globals.checkXMLNoSubelements( subelement, location )
                        src = None
                        for attrib,value in subelement.items():
                            if attrib=="src": src = value
                            #elif attrib=="pron": pron = value
                            #elif attrib=="xlit": xlit = value
                            else: logging.warning( "Unprocessed '{}' attribute ({}) in {}".format( attrib, value, location ) )
                    else: logging.warning( "Unprocessed '{}' sub-element ({}) in {}".format( subelement.tag, subelement.text, element.tag ) )
########### source
            elif element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"source":
                source = element.text
                Globals.checkXMLNoAttributes( element, element.tag, "n4cq" )
                Globals.checkXMLNoTail( element, element.tag, "g7ju" )
                if source: entryResults.append( ('source', source,) )
                # Now process the subelements
                for subelement in element.getchildren():
                    if subelement.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"w":
                        location = "w of source"
                        sourceW = subelement.text
                        sourceWTail = subelement.tail
                        Globals.checkXMLNoSubelements( subelement, location, "n4fa" )
                        src = pron = xlit = None
                        for attrib,value in subelement.items():
                            if attrib=="src": src = value
                            elif attrib=="pron": pron = value
                            elif attrib=="xlit": xlit = value
                            else: logging.warning( "b5gd Unprocessed '{}' attribute ({}) in {}".format( attrib, value, location ) )
                        if sourceW or sourceWTail: entryResults.append( ('sourceWord', (sourceW,sourceWTail, src,pron,xlit,), ) )
                    elif subelement.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"def":
                        location = "def of source"
                        defText = subelement.text
                        defTail = subelement.tail
                        Globals.checkXMLNoAttributes( subelement, location, "b3f5" )
                        Globals.checkXMLNoSubelements( subelement, location, "b3xz" )
                        if defText: entryResults.append( ('sourceDef', (defText,defTail,), ) )
                    elif subelement.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"note":
                        location = "note of source"
                        noteText = subelement.text
                        noteTail = subelement.tail
                        Globals.checkXMLNoAttributes( subelement, location, "v43b" )
                        Globals.checkXMLNoSubelements( subelement, location )
                        if noteText: entryResults.append( ('sourceNote', (noteText,noteTail,), ) )
                    else: logging.warning( "c3fa Unprocessed '{}' sub-element ({}) in {}".format( subelement.tag, subelement.text, element.tag ) )
########### meaning
            elif element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"meaning":
                meaning = element.text
                Globals.checkXMLNoTail( element, element.tag, "d43f" )
                Globals.checkXMLNoAttributes( element, element.tag, "34f5" )
                if meaning: entryResults.append( ('meaning', meaning,) )
                # Now process the subelements
                for subelement in element.getchildren():
                    if subelement.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"def":
                        sublocation = "def of meaning"
                        w = subelement.text
                        w2 = subelement.tail
                        Globals.checkXMLNoSubelements( subelement, sublocation, "g76h" )
                        Globals.checkXMLNoAttributes( subelement, sublocation, "sd2d" )
                    elif subelement.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"w":
                        sublocation = "w of meaning"
                        w = subelement.text
                        w2 = subelement.tail
                        Globals.checkXMLNoSubelements( subelement, sublocation )
                        src = None
                        for attrib,value in subelement.items():
                            if attrib=="src": src = value
                            else: logging.warning( "Unprocessed '{}' attribute ({}) in {}".format( attrib, value, sublocation ) )
                    elif subelement.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"note":
                        sublocation = "note of meaning"
                        w = subelement.text
                        w2 = subelement.tail
                        Globals.checkXMLNoAttributes( subelement, sublocation, "df5h" )
                        Globals.checkXMLNoSubelements( subelement, sublocation, "d2fy" )
                    else: logging.warning( "wUnprocessed '{}' sub-element ({}) in {}".format( subelement.tag, subelement.text, element.tag ) )
########### usage
            elif element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"usage":
                usage = element.text
                Globals.checkXMLNoTail( element, element.tag, "f5gy" )
                Globals.checkXMLNoAttributes( element, element.tag, "1s4d" )
                if usage: entryResults.append( ('usage', usage,) )
                for subelement in element.getchildren():
                    if subelement.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"w":
                        sublocation = 'w of usage'
                        w = element.text
                        wTail = element.tail
                        Globals.checkXMLNoSubelements( subelement, sublocation )
                        src = pron = xlit = None
                        for attrib,value in subelement.items():
                            if attrib=="src": src = value
                            elif attrib=="pron": pron = value
                            elif attrib=="xlit": xlit = value
                            else: logging.warning( "Unprocessed '{}' attribute ({}) in {}".format( attrib, value, sublocation ) )
                        for sub2element in subelement.getchildren():
                            if sub2element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"w":
                                sub2location = 'w of ' + sublocation
                                w = element.text
                                Globals.checkXMLNoTail( element, sub2location, "5g4f" )
                                Globals.checkXMLNoAttributes( element, sub2location, "g4h8" )
                            else: logging.warning( "Unprocessed '{}' sub-element ({}) in {}".format( subelement.tag, subelement.text, sublocation ) )
                    elif subelement.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"note":
                        sublocation = "note of usage"
                        w = subelement.text
                        w2 = subelement.tail
                        Globals.checkXMLNoAttributes( subelement, sublocation, "f3f5" )
                        Globals.checkXMLNoSubelements( subelement, sublocation, "z23v" )
                    else: logging.warning( "Unprocessed '{}' sub-element ({}) in {}".format( subelement.tag, subelement.text, element.tag ) )
########### bdb
            elif element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"bdb":
                occasionalText = element.text
                Globals.checkXMLNoTail( element, element.tag, "f2f3" )
                # Process the attributes
                cite = form = mod = theType = None
                for attrib,value in element.items():
                    if attrib=="cite": cite = value
                    elif attrib=="form": form = value
                    elif attrib=="mod": mod = value
                    elif attrib=="type": theType = value
                    else: logging.warning( "Unprocessed '{}' attribute ({}) in {}".format( attrib, value, element.tag ) )
                # Process the subelements
                for subelement in element.getchildren():
                    if subelement.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"w":
                        sublocation = "w of " + element.tag
                        w = element.text
                        w2 = element.tail
                        Globals.checkXMLNoSubelements( subelement, sublocation )
                        src = origin = n = None
                        for attrib,value in subelement.items():
                            if attrib=="src": src = value
                            elif attrib=="origin": origin = value
                            elif attrib=="n": n = value
                            else: logging.warning( "Unprocessed '{}' attribute ({}) in {}".format( attrib, value, sublocation ) )
                    elif subelement.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"def":
                        sublocation = "def of " + element.tag
                        theDef = element.text
                        theDef2 = element.tail
                        Globals.checkXMLNoSubelements( subelement, sublocation, "fh5h" )
                        Globals.checkXMLNoAttributes( subelement, sublocation, "dfg4" )
                    elif subelement.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"stem":
                        sublocation = "stem of " + element.tag
                        stem = element.text
                        stem2 = element.tail
                        Globals.checkXMLNoSubelements( subelement, sublocation, "f3fg" )
                        Globals.checkXMLNoAttributes( subelement, sublocation, "b34h" )
                    elif subelement.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"pos":
                        sublocation = "pos of " + element.tag
                        pos = element.text
                        pos2 = element.tail
                        Globals.checkXMLNoSubelements( subelement, sublocation, "d2f6" )
                        Globals.checkXMLNoAttributes( subelement, sublocation, "s1d3" )
                    elif subelement.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"em":
                        sublocation = "em of " + element.tag
                        pos = element.text
                        pos2 = element.tail
                        Globals.checkXMLNoSubelements( subelement, sublocation, "a2d4" )
                        Globals.checkXMLNoAttributes( subelement, sublocation, "v5b6" )
                    elif subelement.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"asp":
                        sublocation = "asp of " + element.tag
                        pos = element.text
                        pos2 = element.tail
                        Globals.checkXMLNoSubelements( subelement, sublocation, "d2fg" )
                        Globals.checkXMLNoAttributes( subelement, sublocation, "j4h6" )
                    elif subelement.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"ref":
                        sublocation = "ref of " + element.tag
                        ref = element.text
                        ref2 = element.tail
                        r = None
                        for attrib,value in subelement.items():
                            if attrib=="r": r = value
                            else: logging.warning( "1s4f Unprocessed '{}' attribute ({}) in {}".format( attrib, value, sublocation ) )
                        Globals.checkXMLNoSubelements( subelement, sublocation, "m54f" )
                    elif subelement.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"foreign":
                        sublocation = "foreign of " + element.tag
                        foreign = element.text
                        foreign2 = element.tail
                        lang = None
                        for attrib,value in subelement.items():
                            if attrib==HebrewOldLexiconFileConverter.XMLNameSpace+"lang": lang = value
                            else: logging.warning( "k3z9 Unprocessed '{}' attribute ({}) in {}".format( attrib, value, sublocation ) )
                        Globals.checkXMLNoSubelements( subelement, sublocation, "j6gh" )
                    elif subelement.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"sense":
                        sublocation = "sense of " + element.tag
                        sense = element.text
                        senseTail = element.tail
                        n = None
                        for attrib,value in subelement.items():
                            if attrib=="n": n = value
                            else: logging.warning( "b4m2 Unprocessed '{}' attribute ({}) in {}".format( attrib, value, sublocation ) )
                        for sub2element in subelement.getchildren():
                            if sub2element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"w":
                                sub2location = "w of " + sublocation
                                word = sub2element.text
                                word2 = sub2element.tail
                                # Process the attributes
                                lemma = morph = None
                                for attrib,value in sub2element.items():
                                    if attrib=="src": src = value
                                    elif attrib=="morph": morph = value
                                    else: logging.warning( "3w52 Unprocessed '{}' attribute ({}) in {}".format( attrib, value, sub2location ) )
                            elif sub2element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"def":
                                sub2location = "def of " + sublocation
                                theDef = sub2element.text
                                theDef2 = sub2element.tail
                                Globals.checkXMLNoAttributes( sub2element, sub2location, "s3fd" )
                                Globals.checkXMLNoSubelements( sub2element, sub2location, "b4bn" )
                            elif sub2element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"stem":
                                sub2location = "stem of " + sublocation
                                stem = sub2element.text
                                stem2 = sub2element.tail
                                Globals.checkXMLNoAttributes( sub2element, sub2location, "5vb6" )
                                Globals.checkXMLNoSubelements( sub2element, sub2location, "v3v5" )
                            elif sub2element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"pos":
                                sub2location = "pos of " + sublocation
                                stem = sub2element.text
                                stem2 = sub2element.tail
                                Globals.checkXMLNoAttributes( sub2element, sub2location, "s2h5" )
                                Globals.checkXMLNoSubelements( sub2element, sub2location, "v4v4" )
                            elif sub2element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"em":
                                sub2location = "em of " + sublocation
                                stem = sub2element.text
                                stem2 = sub2element.tail
                                Globals.checkXMLNoAttributes( sub2element, sub2location, "cv3b" )
                                Globals.checkXMLNoSubelements( sub2element, sub2location, "z4b6" )
                            elif sub2element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"asp":
                                sub2location = "asp of " + sublocation
                                stem = sub2element.text
                                stem2 = sub2element.tail
                                Globals.checkXMLNoAttributes( sub2element, sub2location, "mn42" )
                                Globals.checkXMLNoSubelements( sub2element, sub2location, "v3c1" )
                            elif sub2element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"ref":
                                sub2location = "ref of " + sublocation
                                ref = sub2element.text
                                ref2 = sub2element.tail
                                r = None
                                for attrib,value in sub2element.items():
                                    if attrib=="r": r = value
                                    else: logging.warning( "g5df Unprocessed '{}' attribute ({}) in {}".format( attrib, value, sub2location ) )
                                Globals.checkXMLNoSubelements( sub2element, sub2location, "be6h" )
                            elif sub2element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"foreign":
                                sub2location = "foreign of " + sublocation
                                foreign = sub2element.text
                                foreign2 = sub2element.tail
                                lang = None
                                for attrib,value in sub2element.items():
                                    if attrib==HebrewOldLexiconFileConverter.XMLNameSpace+"lang": lang = value
                                    else: logging.warning( "g5g2 Unprocessed '{}' attribute ({}) in {}".format( attrib, value, sub2location ) )
                                Globals.checkXMLNoSubelements( sub2element, sub2location, "8j6h" )
                            elif sub2element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"sense":
                                sub2location = "sense of " + sublocation
                                stem = sub2element.text
                                stem2 = sub2element.tail
                                # Process the attributes
                                lemma = morph = None
                                for attrib,value in sub2element.items():
                                    if attrib=="n": n = value
                                    #elif attrib=="morph": morph = value
                                    else: logging.warning( "q1Unprocessed '{}' attribute ({}) in {}".format( attrib, value, sub2location ) )
                                for sub3element in sub2element.getchildren():
                                    if sub3element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"w":
                                        sub3location = "w of " + sub2location
                                        w = sub3element.text
                                        w2 = sub3element.tail
                                        Globals.checkXMLNoAttributes( sub3element, sub3location, "i7j7" )
                                        Globals.checkXMLNoSubelements( sub3element, sub3location, "6g3f" )
                                    elif sub3element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"def":
                                        sub3location = "def of " + sub2location
                                        theDef = sub3element.text
                                        theDef2 = sub3element.tail
                                        Globals.checkXMLNoAttributes( sub3element, sub3location, "2sd4" )
                                        Globals.checkXMLNoSubelements( sub3element, sub3location, "f2d5" )
                                    elif sub3element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"stem":
                                        sub3location = "stem of " + sub2location
                                        theDef = sub3element.text
                                        theDef2 = sub3element.tail
                                        Globals.checkXMLNoAttributes( sub3element, sub3location, "s1d4" )
                                        Globals.checkXMLNoSubelements( sub3element, sub3location, "g3v6" )
                                    elif sub3element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"asp":
                                        sub3location = "asp of " + sub2location
                                        theDef = sub3element.text
                                        theDef2 = sub3element.tail
                                        Globals.checkXMLNoAttributes( sub3element, sub3location, "a1sd" )
                                        Globals.checkXMLNoSubelements( sub3element, sub3location, "d2df" )
                                    elif sub3element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"pos":
                                        sub3location = "pos of " + sub2location
                                        theDef = sub3element.text
                                        theDef2 = sub3element.tail
                                        Globals.checkXMLNoAttributes( sub3element, sub3location, "a2d3" )
                                        Globals.checkXMLNoSubelements( sub3element, sub3location, "b5b6" )
                                    elif sub3element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"em":
                                        sub3location = "em of " + sub2location
                                        theDef = sub3element.text
                                        theDef2 = sub3element.tail
                                        Globals.checkXMLNoAttributes( sub3element, sub3location, "n34v" )
                                        Globals.checkXMLNoSubelements( sub3element, sub3location, "v45v" )
                                    elif sub3element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"ref":
                                        sub3location = "ref of " + sub2location
                                        ref = sub3element.text
                                        ref2 = sub3element.tail
                                        r = None
                                        for attrib,value in sub3element.items():
                                            if attrib=="r": r = value
                                            else: logging.warning( "k6h8 Unprocessed '{}' attribute ({}) in {}".format( attrib, value, sub3location ) )
                                        Globals.checkXMLNoSubelements( sub3element, sub3location, "b4g6" )
                                    elif sub3element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"sense":
                                        sub3location = "sense of " + sub2location
                                        theDef = sub3element.text
                                        theDef2 = sub3element.tail
                                        for attrib,value in sub3element.items():
                                            if attrib=="n": n = value
                                            #elif attrib=="morph": morph = value
                                            else: logging.warning( "3q1Unprocessed '{}' attribute ({}) in {}".format( attrib, value, sub3location ) )
                                        for sub4element in sub3element.getchildren():
                                            if sub4element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"w":
                                                sub4location = "w of " + sub3location
                                                w = sub4element.text
                                                w2 = sub4element.tail
                                                Globals.checkXMLNoSubelements( sub4element, sub4location )
                                                for attrib,value in sub4element.items():
                                                    if attrib=="src": src = value
                                                    else: logging.warning( "4q1Unprocessed '{}' attribute ({}) in {}".format( attrib, value, sub4location ) )
                                            elif sub4element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"def":
                                                sub4location = "def of " + sub3location
                                                theDef = sub4element.text
                                                theDef2 = sub4element.tail
                                                Globals.checkXMLNoSubelements( sub4element, sub4location )
                                                for attrib,value in sub4element.items():
                                                    if attrib=="n": n = value
                                                    #elif attrib=="morph": morph = value
                                                    else: logging.warning( "4q1Unprocessed '{}' attribute ({}) in {}".format( attrib, value, sub4location ) )
                                            elif sub4element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"stem":
                                                sub4location = "stem of " + sub3location
                                                theDef = sub4element.text
                                                theDef2 = sub4element.tail
                                                Globals.checkXMLNoAttributes( sub4element, sub4location, "cdsv" )
                                                Globals.checkXMLNoSubelements( sub4element, sub4location, "3rve" )
                                            elif sub4element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"em":
                                                sub4location = "em of " + sub3location
                                                theDef = sub4element.text
                                                theDef2 = sub4element.tail
                                                Globals.checkXMLNoAttributes( sub4element, sub4location, "a2ds" )
                                                Globals.checkXMLNoSubelements( sub4element, sub4location, "f4f5" )
                                            elif sub4element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"sense":
                                                sub4location = "sense of " + sub3location
                                                theDef = sub4element.text
                                                theDef2 = sub4element.tail
                                                for attrib,value in sub4element.items():
                                                    if attrib=="n": n = value
                                                    #elif attrib=="morph": morph = value
                                                    else: logging.warning( "46q1Unprocessed '{}' attribute ({}) in {}".format( attrib, value, sub4location ) )
                                                for sub5element in sub4element.getchildren():
                                                    if sub5element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"w":
                                                        sub5location = "w of " + sub4location
                                                        w = sub5element.text
                                                        w2 = sub5element.tail
                                                        Globals.checkXMLNoSubelements( sub5element, sub5location, "vreb" )
                                                        Globals.checkXMLNoAttributes( sub5element, sub5location, "3d5g" )
                                                    elif sub5element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"def":
                                                        sub5location = "def of " + sub4location
                                                        theDef = sub5element.text
                                                        theDef2 = sub5element.tail
                                                        Globals.checkXMLNoSubelements( sub5element, sub5location )
                                                        for attrib,value in sub5element.items():
                                                            if attrib=="n": n = value
                                                            #elif attrib=="morph": morph = value
                                                            else: logging.warning( "4q1Unprocessed '{}' attribute ({}) in {}".format( attrib, value, sub5location ) )
                                                    elif sub5element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"stem":
                                                        sub5location = "stem of " + sub4location
                                                        theDef = sub5element.text
                                                        theDef2 = sub5element.tail
                                                        Globals.checkXMLNoAttributes( sub5element, sub5location, "nmgd" )
                                                        Globals.checkXMLNoSubelements( sub5element, sub5location, "2d21" )
                                                    elif sub5element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"em":
                                                        sub5location = "em of " + sub4location
                                                        theDef = sub5element.text
                                                        theDef2 = sub5element.tail
                                                        Globals.checkXMLNoAttributes( sub5element, sub5location, "s32f" )
                                                        Globals.checkXMLNoSubelements( sub5element, sub5location, "d21d" )
                                                    elif sub5element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"sense":
                                                        sub5location = "sense of " + sub4location
                                                        theDef = sub5element.text
                                                        theDef2 = sub5element.tail
                                                        for attrib,value in sub5element.items():
                                                            if attrib=="n": n = value
                                                            #elif attrib=="morph": morph = value
                                                            else: logging.warning( "456q1Unprocessed '{}' attribute ({}) in {}".format( attrib, value, sub5location ) )
                                                        for sub6element in sub5element.getchildren():
                                                            if sub6element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"w":
                                                                sub6location = "w of " + sub5location
                                                                w = sub6element.text
                                                                w2 = sub6element.tail
                                                                Globals.checkXMLNoSubelements( sub6element, sub6location, "v3fv" )
                                                                Globals.checkXMLNoAttributes( sub6element, sub6location, "d3fh" )
                                                            elif sub6element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"def":
                                                                sub6location = "def of " + sub5location
                                                                theDef = sub6element.text
                                                                theDef2 = sub6element.tail
                                                                Globals.checkXMLNoSubelements( sub6element, sub6location, "d3fh" )
                                                                Globals.checkXMLNoAttributes( sub6element, sub6location, "db65" )
                                                            else: logging.warning( "3b6d Unprocessed '{}' sub-element ({}) in {}".format( sub6element.tag, sub6element.text, sub5location ) )
                                                    else: logging.warning( "9j56 Unprocessed '{}' sub-element ({}) in {}".format( sub5element.tag, sub5element.text, sub4location ) )
                                            else: logging.warning( "3c5f Unprocessed '{}' sub-element ({}) in {}".format( sub4element.tag, sub4element.text, sub3location ) )
                                    else: logging.warning( "cdfb Unprocessed '{}' sub-element ({}) in {}".format( sub3element.tag, sub3element.text, sub2location ) )
                            else: logging.warning( "2d54 Unprocessed '{}' sub-element ({}) in {}".format( sub2element.tag, sub2element.text, sublocation ) )
                    else: logging.warning( "h8j4 Unprocessed '{}' sub-element ({}) in {}".format( subelement.tag, subelement.text, element.tag ) )
                #entryResults.append( ('bdb', sense,) )
########### xref
            elif element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"xref":
                Globals.checkXMLNoText( element, element.tag, "s2f5" )
                Globals.checkXMLNoTail( element, element.tag, "s2d2" )
                Globals.checkXMLNoSubelements( element, element.tag, "s2d5" )
                # Process the attributes
                twot = src = None
                for attrib,value in element.items():
                    if attrib=="twot": twot = value
                    elif attrib=="src": src = value
                    else: logging.warning( "c4bv Unprocessed '{}' attribute ({}) in {}".format( attrib, value, element.tag ) )
########### status
            elif element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"status":
                status = element.text
                Globals.checkXMLNoTail( element, element.tag, "8h6h" )
                Globals.checkXMLNoSubelements( element, element.tag )
                # Process the attributes
                p = src = None
                for attrib,value in element.items():
                    if attrib=="p": p = value
                    elif attrib=="src": src = value
                    else: logging.warning( "pqrUnprocessed '{}' attribute ({}) in {}".format( attrib, value, element.tag ) )
########### note
            elif element.tag == HebrewOldLexiconFileConverter.HebLexNameSpace+"note":
                note = element.text
                Globals.checkXMLNoTail( element, element.tag, "f3g7" )
                Globals.checkXMLNoSubelements( element, element.tag, "m56g" )
                Globals.checkXMLNoAttributes( element, element.tag, "md3d" )
            else: logging.warning( "2d4f Unprocessed '{}' sub-element ({}) in entry".format( element.tag, element.text ) )
            if element.tail is not None and element.tail.strip(): logging.error( "Unexpected '{}' tail data after {} element in entry".format( element.tail, element.tag ) )

        #print( entryResults )
        self.entries[entryID] = entryResults
    # end of validateMainDiv


    def importDataToPython( self ):
        """
        Loads (and pivots) the data (not including the header) into suitable Python containers to use in a Python program.
        (Of course, you can just use the elementTree in self.tree if you prefer.)
        """
        assert( len ( self.tree ) )
        assert( self.entries )
        return self.entries # temp................................XXXXXXXXXXXXXXXXXXXXXXXXXXXXX......................
    # end of importDataToPython
# end of HebrewOldLexiconFileConverter class


class HebrewOldLexicon:
    """
    Class for handling an Old Hebrew Lexicon

    This class doesn't deal at all with XML, only with Python dictionaries, etc.

    Note: BBB is used in this class to represent the three-character referenceAbbreviation.
    """
    def __init__( self, XMLFolder ):
        """
        Constructor: expects the filepath of the source XML file.
        Loads (and crudely validates the XML file) into an element tree.
        """
        hlc = HebrewOldLexiconFileConverter() # Create the empty object
        hlc.loadAndValidate( XMLFolder ) # Load the XML
        self.entries = hlc.importDataToPython()
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible book code.

        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "Old Hebrew Lexicon object"
        #if self.title: result += ('\n' if result else '') + self.title
        #if self.version: result += ('\n' if result else '') + "Version: {} ".format( self.version )
        #if self.date: result += ('\n' if result else '') + "Date: {}".format( self.date )
        result += ('\n' if result else '') + "  " + _("Number of entries = {}").format( len(self.entries) )
        return result
    # end of __str__

    def getEntryData( self, key ):
        """
        The key is a Hebrew Strong's number (string) like 'H1979'.

        Returns an entry for the given key.
            This is a list of 2-tuples containing pairs of strings, e.g., [('usage', 'company, going, walk, way.')]
        Returns None if the key is not found.
        """
        if key in self.entries: return self.entries[key]

    def getEntryField( self, key, field ):
        """
        The key is a Hebrew Strong's number (string) like 'H1979'.
        The field is a name (string) like 'usage'.

        Returns a string for the given key and field names.
        Returns None if the key or field is not found.
        """
        if key in self.entries:
            for f,d in self.entries[key]:
                if f==field: return d
# end of HebrewOldLexicon class


def demo():
    """
    Main program to handle command line parameters and then run what they want.
    """
    if Globals.verbosityLevel > 0: print( ProgNameVersion )

    testFolder = "../HebrewLexicon/OldLexicon/" # Old Hebrew Lexicon folder

    # Demonstrate the Old Hebrew Lexicon converter class
    if Globals.verbosityLevel > 1: print( "\nDemonstrating the Old Hebrew Lexicon converter class..." )
    hlc = HebrewOldLexiconFileConverter()
    hlc.loadAndValidate( testFolder ) # Load the XML
    print( hlc ) # Just print a summary

    #if Globals.commandLineOptions.export:
        #hlc.exportDataToPython() # Produce the .py tables
        #hlc.exportDataToC() # Produce the .h tables

    # Demonstrate the Old Hebrew Lexicon class
    if Globals.verbosityLevel > 1: print( "\nDemonstrating the Old Hebrew Lexicon class..." )
    hl = HebrewOldLexicon( testFolder ) # Load and process the XML
    print( hl ) # Just print a summary
    print()
    for strongs in ('H1','H123','H1979','H2011',):
        print( strongs, hl.getEntryData( strongs ) )
        print( strongs, hl.getEntryField( strongs, 'usage' ) )
# end of demo

if __name__ == '__main__':
    # Configure basic set-up
    parser = Globals.setup( ProgName, ProgVersion )
    Globals.addStandardOptionsAndProcess( parser, exportAvailable=False )

    demo()

    Globals.closedown( ProgName, ProgVersion )
# end of HebrewOldLexicon.py