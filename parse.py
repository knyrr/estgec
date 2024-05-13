"""Module for creating SQL insert statements for EstGEC-L2-Corpus"""
import os
import glob
import uuid
import zipfile
from urllib.parse import urlparse
import shutil
import requests

URL = "https://github.com/tlu-dt-nlp/EstGEC-L2-Corpus/archive/refs/heads/main.zip"
CORPUS_DIR = 'EstGEC-L2-Corpus-main'


def download_and_unpack_zip(url, output_dir=""):
    """
    Download a ZIP file from the given URL, unpack it into the specified directory,
    and then delete the ZIP file.
    """
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    zip_path = os.path.join(output_dir, filename)
    response = requests.get(url, timeout=10)
    with open(zip_path, 'wb') as file:
        file.write(response.content)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    os.remove(zip_path)


def add_to_annotations_sql(sentence_uuid, annotation):
    """
    Return an insert statement for annotation
    """
    segments = annotation.split('|||')
    if len(segments) < 6:
        print(annotation)
        raise ValueError("Sentence does not contain enough segments.")
    scope = segments[0].split()
    if len(scope) != 2:
        raise ValueError("Scope does not have exactly two parts.")

    scope_start, scope_end = scope
    error_type = segments[1]
    correction = segments[2]
    annotator_num = segments[5]

    annotation_sql = f"""insert into core.text_error_analysis_annotations(id, sentence_id, scope_start, scope_end, error_type, correction, annotator_id) values ('{uuid.uuid4()}'::UUID, '{sentence_uuid}'::UUID, {scope_start}, {scope_end}, '{error_type}', $${correction}$$, {annotator_num});\n"""

    return annotation_sql


def add_to_sentences_sql(sentence_uuid, get_text_id_sql, sentence_index, sentence):
    """
    Return an insert statement for sentence
    """
    sentence_sql = f"""insert into core.text_error_analysis_sentences(id, text_id, sentence_num, sentence) values ('{sentence_uuid}'::UUID, {get_text_id_sql}::UUID, {sentence_index}, $${sentence}$$);\n"""
    return sentence_sql


def get_text_id(file_name):
    """
    Return the function call to get source text id
    """
    level = file_name[:2]
    extracted_file_name = file_name[2:]
    sql_query = ''
    if extracted_file_name[0:5] == '_doc_':
        extracted_file_name = extracted_file_name[1:-4] + '_item'
        # core.get_text_id_by_full_code_or_title('doc_18538799202_item');
        sql_query = "core.get_text_id_by_code_or_title('" + \
            extracted_file_name + "')"
    elif extracted_file_name[0] == '_':
        year = extracted_file_name[1:5]
        extracted_file_name = extracted_file_name[5:-4]
        # core.get_text_id_by_full_code_or_title('C1 2018 III_003-047');
        sql_query = "core.get_text_id_by_code_or_title('" + \
            level + " " + year + " "
        sql_query += extracted_file_name + "')"
    else:
        extracted_file_name = extracted_file_name[:-4]
        # core.get_text_id_by_code_or_title('C1______III_003-052');
        sql_query = "core.get_text_id_by_code_or_title('" + \
            level + "______" + \
            extracted_file_name + "')"
    return sql_query


def parse_text(file_name, text):
    """
    Parse text from file
    """
    get_text_id_sql = get_text_id(file_name)
    lines = text.splitlines()
    sentence_count = 0
    segment_count = 0
    sentence_uuid = ''
    sentences_sql = ''
    annotations_sql = ''
    for line in lines:
        if line and line[0] == 'S':
            segment_count = 0
            sentence_uuid = str(uuid.uuid4())
            sentence = line[2:]
            sentences_sql += add_to_sentences_sql(sentence_uuid, get_text_id_sql,
                                                  sentence_count, sentence)
            sentence_count += 1
        elif line and line[0] == 'A':
            sentence = line[2:]
            annotations_sql += add_to_annotations_sql(sentence_uuid, sentence)
            segment_count += 1
    return sentences_sql, annotations_sql


def parse_dir():
    """
    Parse corpus directory
    """
    sentences_sql = ''
    annotations_sql = ''
    for main_dir in glob.glob(os.path.join(CORPUS_DIR, '*/')):
        for subdir in glob.glob(os.path.join(main_dir, '*/')):
            for file in glob.glob(os.path.join(subdir, '*.txt')):
                with open(os.path.join(os.getcwd(), file), 'r', encoding="utf-8") as f:
                    file_name = os.path.basename(file)
                    if file_name.find("source") == -1:
                        text = f.read()
                        sentences, annotations = parse_text(file_name, text)
                        sentences_sql += sentences
                        annotations_sql += annotations

    with open('R__0009-core.text_error_analysis.sql', 'w', encoding="utf-8") as file:
        file.write(sentences_sql)
        file.write(annotations_sql)


MOCK_FILE_NAME = 'A2IV_003-053.txt'
MOCK = """
S Suvel ma ei ela Jyväskyläs , aga ma elan minu pere ühes teises linnas .
A 9 10|||R:LEX|||enda||oma|||REQUIRED|||-NONE-|||0
A 10 11|||R:NOM:FORM|||perega|||REQUIRED|||-NONE-|||0
A 6 7|||R:LEX|||vaid|||REQUIRED|||-NONE-|||1
A 9 10|||R:LEX|||enda||oma|||REQUIRED|||-NONE-|||1
A 10 11|||R:NOM:FORM|||perega|||REQUIRED|||-NONE-|||1

S Ma elan kodupaikal sest et sain tööt sealt .
A 2 3|||R:NOM:FORM:SPELL|||kodupaigas|||REQUIRED|||-NONE-|||0
A 3 3|||M:PUNCT|||,|||REQUIRED|||-NONE-|||0
A 6 8|||R:WO|||sealt tööd|||REQUIRED|||-NONE-|||0

S Ka veedan ma nats puhkust , kunas suvel minu tuttav pere Itaaliast tule Soome külastada kaheks nädalaks !
A 3 4|||R:LEX|||natuke|||REQUIRED|||-NONE-|||0
A 6 7|||R:LEX|||kuna|||REQUIRED|||-NONE-|||0
A 12 13|||R:VERB:FORM|||tuleb|||REQUIRED|||-NONE-|||0
A 8 13|||R:WO|||tuleb minu tuttav pere Itaaliast|||REQUIRED|||-NONE-|||0
A 13 14|||R:NOM:FORM|||Soomet|||REQUIRED|||-NONE-|||0
A 14 15|||R:LEX:VERB:FORM|||külastama|||REQUIRED|||-NONE-|||0
A 13 17|||R:WO|||kaheks nädalaks Soome külastama|||REQUIRED|||-NONE-|||0
A 3 4|||R:LEX|||natuke|||REQUIRED|||-NONE-|||1
A 6 7|||R:LEX|||kuna|||REQUIRED|||-NONE-|||1
A 12 13|||R:VERB:FORM|||tuleb|||REQUIRED|||-NONE-|||1
A 8 13|||R:WO|||tuleb minu tuttav pere Itaaliast|||REQUIRED|||-NONE-|||1
A 14 15|||R:LEX|||külla|||REQUIRED|||-NONE-|||1
A 13 17|||R:WO|||kaheks nädalaks Soome külla|||REQUIRED|||-NONE-|||1

S Ühes teeme palju - sõidame autoga piki Soomee , ujutame Päijänne-järves , sööme soomaist toita , käime lõbustusparkis ...
A 6 7|||R:LEX|||mööda|||REQUIRED|||-NONE-|||0
A 7 8|||R:SPELL|||Soomet|||REQUIRED|||-NONE-|||0
A 9 10|||R:LEX|||ujume|||REQUIRED|||-NONE-|||0
A 10 11|||R:WS|||Päijänne järves|||REQUIRED|||-NONE-|||0
A 13 14|||R:SPELL|||soomemaist|||REQUIRED|||-NONE-|||0
A 14 15|||R:SPELL|||toitu|||REQUIRED|||-NONE-|||0
A 17 18|||R:SPELL|||lõbustuspargis|||REQUIRED|||-NONE-|||0
A 6 7|||R:LEX|||mööda|||REQUIRED|||-NONE-|||1
A 7 8|||R:SPELL|||Soomet|||REQUIRED|||-NONE-|||1
A 8 8|||M:LEX|||ringi|||REQUIRED|||-NONE-|||1
A 9 10|||R:LEX|||ujume|||REQUIRED|||-NONE-|||1
A 10 11|||R:WS|||Päijänne järves|||REQUIRED|||-NONE-|||1
A 13 14|||R:LEX|||soome|||REQUIRED|||-NONE-|||1
A 14 15|||R:LEX:SPELL|||toitu|||REQUIRED|||-NONE-|||1
A 17 18|||R:SPELL|||lõbustuspargis|||REQUIRED|||-NONE-|||1

S Suvel Soomes päike tõuseb vara ja läheb looja hilja .
A 0 4|||R:WO|||Soomes tõuseb päike suvel|||REQUIRED|||-NONE-|||0

S See on tuttav perele uus vaade !
A 2 3|||R:NOM:FORM|||tuttavate|||REQUIRED|||-NONE-|||0

S Suvel on samuti minu sünnipäev .
A -1 -1|||noop|||-NONE-|||-NONE-|||-NONE-|||0

S Ma veedan minu sünnipäeva minu sõpradega koos .
A 2 3|||R:LEX|||enda||oma|||REQUIRED|||-NONE-|||0
A 4 5|||U:LEX|||-NONE-|||REQUIRED|||-NONE-|||0

S Sööme erinevata " suvihõrgutis " , näiteks värskesit maasikasit , ja mineme randa .
A 1 2|||R:NOM:FORM:SPELL|||erinevaid|||REQUIRED|||-NONE-|||0
A 2 3|||U:PUNCT|||-NONE-|||REQUIRED|||-NONE-|||0
A 3 4|||R:NOM:FORM|||suvehõrgutisi|||REQUIRED|||-NONE-|||0
A 4 5|||U:PUNCT|||-NONE-|||REQUIRED|||-NONE-|||0
A 7 8|||R:SPELL|||värskeid|||REQUIRED|||-NONE-|||0
A 8 9|||R:SPELL|||maasikaid|||REQUIRED|||-NONE-|||0
A 9 10|||U:PUNCT|||-NONE-|||REQUIRED|||-NONE-|||0
A 11 12|||R:SPELL|||lähme|||REQUIRED|||-NONE-|||0

S Õhtul sööme sadamas einelaudis .
A 3 4|||R:SPELL|||einelauas|||REQUIRED|||-NONE-|||0

S Loodetavasti suvel ei sadada tublisti aga ilm on hea ja päike paista iga päev !
A 3 4|||R:VERB:FORM|||saja|||REQUIRED|||-NONE-|||0
A 1 4|||R:WO|||ei saja suvel|||REQUIRED|||-NONE-|||0
A 5 5|||M:PUNCT|||,|||REQUIRED|||-NONE-|||0
A 5 6|||R:LEX|||vaid|||REQUIRED|||-NONE-|||0
A 11 12|||R:VERB:FORM|||paistab|||REQUIRED|||-NONE-|||0
A 3 4|||R:VERB:FORM|||saja|||REQUIRED|||-NONE-|||1
A 4 5|||R:LEX|||eriti|||REQUIRED|||-NONE-|||1
A 2 5|||R:WO|||eriti ei saja|||REQUIRED|||-NONE-|||1
A 5 5|||M:PUNCT|||,|||REQUIRED|||-NONE-|||1
A 5 6|||R:LEX|||vaid|||REQUIRED|||-NONE-|||1
A 11 12|||R:VERB:FORM|||paistab|||REQUIRED|||-NONE-|||1
"""


# sentences, annotations = parse_text(MOCK_FILE_NAME, MOCK)
# print(annotations)


download_and_unpack_zip(URL)
parse_dir()
shutil.rmtree(CORPUS_DIR)
