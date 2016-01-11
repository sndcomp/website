# -*- coding: utf-8 -*-
from __future__ import unicode_literals
'''
    In the php version of the soundcomparisons websites
    it was possible to import .csv files from Pauls database.
    This module aims to replicate this feature.
    For the corresponding .php file
    a look at admin/query/dbimport/Importer.php may be educational.
'''
import db
import os
import re
import clldutils.dsv as dsv
from itertools import izip

'''
    csvMapping realizes a mapping from regexes of file namess
    to their accompaning database models,
    and a mapping from column names in the csv contents of these files to columns
    of the database models they belong to.
'''
csvMapping = {
    '^Contributors\.txt$': {
        'model': db.Contributors,
        'columns': {
            'Contributor Ix': 'ContributorIx',
            'Sort Group': 'SortGroup',
            'Sort Ix for About page': 'SortIxForAboutPage',
            'Forenames': 'Forenames',
            'Surnames': 'Surnames',
            'Initials': 'Initials',
            'Email up to AT sign': 'EmailUpToAt',
            'Email after AT sign': 'EmailAfterAt',
            'Personal Website Text to link to': 'PersonalWebsite',
            'Full Role Description for About page': 'FullRoleDescription'
        }},
    '^ContributorCategories\.txt$': {
        'model': db.ContributorCategories,
        'columns': {
            'Sort Group': 'SortGroup',
            'Heading Text for this Sort Group': 'Headline',
            'Heading Abbr': 'Abbr'
        }},
    '^DefaultSingleLanguage\.txt$': {
        'model': db.DefaultLanguages,
        'columns': {
            'Study Ix': 'StudyIx',
            'Family Ix': 'FamilyIx',
            'Default Single Language Full Ix': 'LanguageIx'
        }},
    '^DefaultLanguagesToExcludeFromMap\.txt$': {
        'model': db.DefaultLanguagesExcludeMap,
        'columns': {
            'Study Ix': 'StudyIx',
            'Family Ix': 'FamilyIx',
            'Default Language to Exclude from Map Full Ix': 'LanguageIx'
        }},
    '^DefaultSingleWord\.txt$': {
        'model': db.DefaultWords,
        'columns': {
            'Study Ix': 'StudyIx',
            'Family Ix': 'FamilyIx',
            'Default Single Word Elicitation Ix': 'IxElicitation'
        }},
    '^DefaultTableMultipleLanguages\.txt$': {
        'model': db.DefaultMultipleLanguages,
        'columns': {
            'Study Ix': 'StudyIx',
            'Family Ix': 'FamilyIx',
            'Default Table Multiple Language Full Ix': 'LanguageIx'
        }},
    '^DefaultTableMultipleWords\.txt$': {
        'model': db.DefaultMultipleWords,
        'columns': {
            'Study Ix': 'StudyIx',
            'Family Ix': 'FamilyIx',
            'Default Table Multiple Word Elicitation Ix': 'IxElicitation'
        }},
    '^Flags\.txt$': {
        'model': db.FlagTooltip,
        'columns': {
            'Flag Image File Name': 'Flag',
            'Flag Tooltip': 'Tooltip'
        }},
    '^Languages_(.*)\.txt$': {
        'model': db.Languages,
        'columns': {
            'Study Ix': 'StudyIx',
            'Family Ix': 'FamilyIx',
            'Spelling Reference Language for WebSite': 'IsSpellingRfcLang',
            'Spelling Reference Language for WebSite Lg Name': 'SpellingRfcLangName',
            'Associated Phonetics Lg for this Spelling Lg':
                'AssociatedPhoneticsLgForThisSpellingLg',
            'Is This ONLY An Orthography With No Transcriptions':
                'IsOrthographyHasNoTranscriptions',
            'Full Index Number': 'LanguageIx',
            'Website Short Name': 'ShortName',
            'Website Tooltip': 'ToolTip',
            'Specific Language Variety Name': 'SpecificLanguageVarietyName',
            'Language Status Type Ix': 'LanguageStatusType',
            'Website Subgroup Name': 'WebsiteSubgroupName',
            'Website Subgroup Wikipedia String': 'WebsiteSubgroupWikipediaString',
            'Historical Period': 'HistoricalPeriod',
            'Historical Period Wikipedia String': 'HistoricalPeriodWikipediaString',
            'Ethnic Group': 'EthnicGroup',
            'State/Region': 'StateRegion',
            'Nearest City': 'NearestCity',
            'Precise Locality': 'PreciseLocality',
            'Precise Locality as Spelt in National Std Lg': 'PreciseLocalityNationalSpelling',
            'External WebLink': 'ExternalWeblink',
            'Ccd:  Overall FileName': 'FilePathPart',
            'Flag': 'Flag',
            'Associated Rfc Lg\'s Full Index Number': 'RfcLanguage',
            'LatitudeAsString': 'Latitude',
            'LongitudeAsString': 'Longtitude',
            'ISO 639-3 code': 'ISOCode',
            'Glottolog code': 'GlottoCode',
            'Wikipedia Atv Text more precise than ISO': 'WikipediaLinkPart',
            'Contributor:  Spoken By': 'ContributorSpokenBy',
            'Contributor:  Recorded By 1': 'ContributorRecordedBy1',
            'Contributor:  Recorded By 2': 'ContributorRecordedBy2',
            'Contributor:  Sound Editing By': 'ContributorSoundEditingBy',
            'Contributor:  Phonetic Transcription By': 'ContributorPhoneticTranscriptionBy',
            'Contributor:  Reconstruction By': 'ContributorReconstructionBy',
            'Contributor:  Citation Author 1': 'ContributorCitationAuthor1',
            'Citation 1:  Year': 'Citation1Year',
            'Citation 1:  Pages': 'Citation1Pages',
            'Contributor:  Citation Author 2': 'ContributorCitationAuthor2',
            'Citation 2:  Year': 'Citation2Year',
            'Citation 2:  Pages': 'Citation2Pages'
        }},
    '^LanguageStatusTypes\.txt$': {
        'model': db.LanguageStatusTypes,
        'columns': {
            'Language Status Type Ix': 'LanguageStatusType',
            'Language Status Type Description Text': 'Description',
            'Language Status Abbreviation': 'Status',
            'Language Status ToolTip': 'StatusTooltip',
            'Status Type Colour on Website': 'Color',
            'Opacity Percentage': 'Opacity',
            'Colour Depth Percentage': 'ColorDepth'
        }},
    '^MeaningGroups\.txt$': {
        'model': db.MeaningGroups,
        'columns': {
            'Meaning Group Ix': 'MeaningGroupIx',
            'Meaning Group Name': 'Name'
        }},
    '^MeaningGroupMembers\.txt$': {
        'model': db.MeaningGroupMembers,
        'columns': {
            'Study Ix': 'StudyIx',
            'Family Ix': 'FamilyIx',
            'Meaning Group Ix': 'MeaningGroupIx',
            'Meaning Group Member Ix': 'MeaningGroupMemberIx',
            'Ix Elicitation': 'IxElicitation',
            'Ix Morphological Instance': 'IxMorphologicalInstance'
        }},
    '^RegionGroupMemberLanguages_(.*)\.txt$': {
        'model': db.RegionLanguages,
        'columns': {
            'Study Ix': 'StudyIx',
            'Family Ix': 'FamilyIx',
            'Sub-Family Ix': 'SubFamilyIx',
            'Region Gp Ix': 'RegionGpIx',
            'Region Member Lg Ix': 'RegionMemberLgIx',
            'Region Member Lg Full Index Number': 'LanguageIx',
            'Region Member Website SubGroup Ix': 'RegionMemberWebsiteSubGroupIx',
            'Region Gp Member Lg Name Short In This Sub-Family WebSite':
                'RegionGpMemberLgNameShortInThisSubFamilyWebsite',
            'Region Gp Member Lg Name Long In This Sub-Family WebSite':
                'RegionGpMemberLgNameLongInThisSubFamilyWebsite',
            'Bn - Include?': 'Include'
        }},
    '^RegionGroups_(.*)\.txt$': {
        'model': db.Regions,
        'columns': {
            'Study Ix': 'StudyIx',
            'Family Ix': 'FamilyIx',
            'Sub-Family Ix': 'SubFamilyIx',
            'Region Gp Ix': 'RegionGpIx',
            'Region Gp Type Ix': 'RegionGpTypeIx',
            'Region Gp Nm Long': 'RegionGpNameLong',
            'Region Gp Nm Short': 'RegionGpNameShort',
            'Bn: Default Expanded State': 'DefaultExpandedState'
        }},
    '^Studies\.txt$': {
        'model': db.Studies,
        'columns': {
            'Study Ix': 'StudyIx',
            'Family Ix': 'FamilyIx',
            'Sub-Family Ix': 'SubFamilyIx',
            'Sub-Family Nm': 'Name',
            'Default Top Left Latitude': 'DefaultTopLeftLat',
            'Default Top Left Longitude': 'DefaultTopLeftLon',
            'Default Bottom Right Latitude': 'DefaultBottomRightLat',
            'Default Bottom Right Longitude': 'DefaultBottomRightLon',
            'Bn: Colour by Family Rather Than By Region': 'ColorByFamily',
            'Second Rfc Lg for this Study': 'SecondRfcLg'
        }},
    '^Families\.txt$': {
        'model': db.Families,
        'columns': {
            'Study Ix': 'StudyIx',
            'Family Ix': 'FamilyIx',
            'Family Nm': 'FamilyNm',
            'Family Abbr:  All FileNames': 'FamilyAbbrAllFileNames',
            'Project About URL': 'ProjectAboutUrl',
            'Bn:  Project Active?': 'ProjectActive'
        }},
    '^Transcription Superscript Info\.txt': {
        'model': db.TranscrSuperscriptInfo,
        'columns': {
            'Transcription Superscript Ix': 'Ix',
            'Transcription Superscript Abbreviation': 'Abbreviation',
            'Transcription Superscript Abbreviation Full Hover Text': 'HoverText'
        }},
    '^Transcription Superscript Lender Lgs\.txt': {
        'model': db.TranscrSuperscriptLenderLgs,
        'columns': {
            'Lender Language ISO Code': 'IsoCode',
            'Lender Language Superscript Abbreviation Letters': 'Abbreviation',
            'Lender Language Full Name for Hover Text': 'FullNameForHoverText'
        }},
    '^Transcriptions_(.*)\.txt$': {
        'model': db.Transcriptions,
        'columns': {
            'Study Ix': 'StudyIx',
            'Family Ix': 'FamilyIx',
            'Ix Elicitation': 'IxElicitation',
            'Ix Morphological Instance': 'IxMorphologicalInstance',
            'Alternative Lexeme Ix': 'AlternativeLexemIx',
            'Alternative PhoneTic Realisation Ix': 'AlternativePhoneticRealisationIx',
            'Full Index Number': 'LanguageIx',
            'PhoneTic Transcription in Unicode': 'Phonetic',
            'Spelling Altv 1': 'SpellingAltv1',
            'Spelling Altv 2': 'SpellingAltv2',
            'TSI 01:  Bn: Not Cognate with Main Word in This Family':
                'NotCognateWithMainWordInThisFamily',
            'Bn: Not Cognate with Main Word in This Family':
                'NotCognateWithMainWordInThisFamily',  # TODO only seen in Mapudungun
            'TSI 02:  Bn: Common Root but Morpheme Structure Different':
                'CommonRootMorphemeStructDifferent',
            'Bn: Common Root but Morpheme Structure Different':
                'CommonRootMorphemeStructDifferent',  # TODO only seen in Mapudungun
            'TSI 03:  Bn: Different Meaning to Usual for This Cognate':
                'DifferentMeaningToUsualForCognate',
            'TSI 11:  Cognate\'s Actual Meaning in This Language': 'ActualMeaningInThisLanguage',
            'TSI 12:  Other Lexeme in This Language for This Meaning':
                'OtherLexemeInLanguageForMeaning',
            'TSI 21:  Bn: Is This Root A Loan Word from a Known Donor?':
                'RootIsLoanWordFromKnownDonor',
            'TSI 22:  Bn: Is This Root Shared in Another Family?': 'RootSharedInAnotherFamily',
            'TSI 99:  ISO Code for Known Donor or Shared Language or Family': 'IsoCodeKnownDonor',
            'TSI 04:  Txt: Different Morpheme Structure Note': 'DifferentMorphemeStructureNote',
            'TSI 41:  Bn: Odd Phonology': 'OddPhonology',
            'TSI 42:  Txt: Odd Phonology Note': 'OddPhonologyNote',
            'TSI 13:  Txt: Usage Note': 'UsageNote',
            'TSI 81:  Bn: Sound Problem': 'SoundProblem',
            'TSI 05:  Bn: Reconstructed or Historical Form Questionable?':
                'ReconstructedOrHistQuestionable',
            'TSI 06:  Txt: Reconstructed or Historical Form Questionable Note':
                'ReconstructedOrHistQuestionableNote'
        }},
    '^Words_(.*)\.txt$': {
        'model': db.Words,
        'columns': {
            'Ix Elicitation': 'IxElicitation',
            'Ix Morphological Instance': 'IxMorphologicalInstance',
            'Meaning Group Ix': 'MeaningGroupIx',
            'Meaning Group Member Ix': 'MeaningGroupMemberIx',
            'This Fy:  Sort Order By Alphabetical of Family Ancestor':
                'ThisFySortOrderByAlphabeticalOfFamilyAncestor',
            'Ccd:  for Sound Files:  Word Identifier Text': 'SoundFileWordIdentifierText',
            'For FileName:  Rfc Modern Lg:  01': 'FileNameRfcModernLg01',
            'For FileName:  Rfc Modern Lg:  02': 'FileNameRfcModernLg02',
            'For FileName:  Rfc Proto-Lg:  01': 'FileNameRfcProtoLg01',
            'For FileName:  Rfc Proto-Lg:  02': 'FileNameRfcProtoLg02',
            'Full Written Form:  Rfc Modern Lg:  01': 'FullRfcModernLg01',
            'Longer Written Form if Needed:  Rfc Modern Lg:  01': 'LongerRfcModernLg01',
            'Full Written Form:  Rfc Modern Lg:  02': 'FullRfcModernLg02',
            'Longer Written Form if Needed:  Rfc Modern Lg:  02': 'LongerRfcModernLg02',
            'Full Written Form:  Rfc Proto-Lg:  01': 'FullRfcProtoLg01',
            'Full Written Form:  Rfc Proto-Lg:  02': 'FullRfcProtoLg02',
            'Full Written Form:  Rfc Proto-Lg:  01  Altv Root': 'FullRfcProtoLg01AltvRoot',
            'Full Written Form:  Rfc Proto-Lg:  02  Altv Root': 'FullRfcProtoLg02AltvRoot'
        }}}


def parseCSV(path, filename=''):
    '''
        @param path String
        @param filename String
        @return ([db.db.Model ∧ SndCompModel], [String])
        This function parses a given csv string that is expected to have a headline
        and will be read from a file expected at <path>.
        The filename will be matched against the keys of the csvMapping,
        and the first entry that matches the filename will be used.
        When the entry is found, it's SndCompModel fromDict method shall be used
        to create a SndCompModel which shall be returned in a list.
        The returned tuple is composed of a list of successfully parsed models,
        and list of errors or warnings.
        If no filename is given, it will be taken from the basename of <path>.
    '''
    # Sanitize filename:
    if filename == '':
        filename = os.path.basename(path)
    # Searching for a mapping:
    mapping = None
    for regex in csvMapping.keys():
        if re.match(regex, filename):
            mapping = csvMapping[regex]
            break
    else:  # Exit if no mapping found:
        return ([], ["No mapping found for filename '%s'." % filename])
    # Dissecting csv:
    dicts = list(dsv.reader(path, dicts=True))
    # Composing models:
    models = []
    for oDict in dicts:
        mDict = {}  # model dict to be generated from original dict
        for k, v in mapping['columns'].iteritems():
            if k in oDict:
                mDict[v] = oDict[k]
        model = mapping['model'](**mDict)
        models.append(model)
    # Validating models:
    valModels, messages = ([], [])
    for (i, m) in izip(xrange(1, len(models)+1), models):
        errors, warnings = m.validate()
        if len(warnings) > 0:
            messages += ["Warning for entry %i: '%s'" % (i, w) for w in warnings]
        if len(errors) > 0:
            messages += ["Error for entry %i: '%s'" % (i, e) for e in errors]
        else:
            valModels.append(m)
    return (valModels, messages)


def postCSV():
    '''
        This function provides the endpoint for POST requests for CSV files.
        CSV files well be parsed and the created models shall replace their counterparts in the database.
        Finally some status shall reported to the user.
        Inspired by:
        http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
        https://stackoverflow.com/a/17802252/448591
        https://stackoverflow.com/a/11817318/448591
    '''
    pass  # FIXME IMPLEMENT

# A simple test for development:
if __name__ == '__main__':
    print('Testing the stuff…')
    files = [
        'ContributorCategories.txt',
        'Contributors.txt',
        'DefaultLanguagesToExcludeFromMap.txt',
        'DefaultSingleLanguage.txt',
        'DefaultSingleWord.txt',
        'DefaultTableMultipleLanguages.txt',
        'DefaultTableMultipleWords.txt',
        'Families.txt',
        'Flags.txt',
        'Languages_Andean.txt',
        'Languages_Celtic.txt',
        'Languages_Englishes.txt',
        'Languages_Germanic.txt',
        'Languages_Mapudungun.txt',
        'Languages_Romance.txt',
        'Languages_Slavic.txt',
        'LanguageStatusTypes.txt',
        'MeaningGroupMembers.txt',
        'MeaningGroups.txt',
        'RegionGroupMemberLanguages_Andean.txt',
        'RegionGroupMemberLanguages_Celtic.txt',
        'RegionGroupMemberLanguages_Englishes.txt',
        'RegionGroupMemberLanguages_Germanic.txt',
        'RegionGroupMemberLanguages_Mapudungun.txt',
        'RegionGroupMemberLanguages_Romance.txt',
        'RegionGroupMemberLanguages_Slavic.txt',
        'RegionGroups_Andean.txt',
        'RegionGroups_Celtic.txt',
        'RegionGroups_Englishes.txt',
        'RegionGroups_Germanic.txt',
        'RegionGroups_Mapudungun.txt',
        'RegionGroups_Romance.txt',
        'RegionGroups_Slavic.txt',
        'Studies.txt',
        'Transcriptions_Andean.txt',
        'Transcriptions_Englishes.txt',
        'Transcriptions_Germanic.txt',
        'Transcriptions_Mapudungun.txt',
        'Transcriptions_Romance.txt',
        'Transcriptions_Slavic.txt',
        'Transcription Superscript Info.txt',
        'Transcription Superscript Lender Lgs.txt',
        'Words_Andean.txt',
        'Words_Celtic.txt',
        'Words_Englishes.txt',
        'Words_Germanic.txt',
        'Words_Mapudungun.txt',
        'Words_Romance.txt',
        'Words_Slavic.txt']
    for file in files:
        path = os.path.join('/tmp/v0', file)
        print('Parsing file "%s"' % file)
        (models, errors) = parseCSV(path)
        for e in errors:
            print(e)
