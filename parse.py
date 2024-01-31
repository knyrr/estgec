import os
import glob
import uuid

# insert into core.text_error_analysis_sentences(id, text_id, sentence_num, sentence)
# values  (gen_random_uuid(), core.get_text_id_by_code_or_title('%III_003-052%') ::UUID, 1, 'ak_eriala_analuus');

# insert into core.text_error_analysis_segments(id, sentence_id, scope_start, scope_end, error_type, correction, annotator_id)
# values('193e5646-6e26-4127-bf73-926c973d801a'::UUID,'193e5646-6e26-4127-bf73-926c973d801c'::UUID,
#        9, 10, 'R:LEX', 'enda ||oma', 0);

dir = 'EstGEC-L2-Corpus/dev'
sentences_sql = ''
segments_sql = ''
extracted_file_name = ''
index = 0

mock_file_name = 'A2IV_003-053.txt'
mock = """
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


def add_to_segments_sql(sentence_uuid, sentence):
    global segments_sql
    segments = sentence.split('|||')

    scope = segments[0].split()
    scope_start = scope[0]
    scope_end = scope[1]
    error_type = segments[1]
    correction = segments[2]
    annotator_num = segments[5]

    if scope_start != '-1' and scope_end != '-1':
        segments_sql += "insert into core.text_error_analysis_segments("
        segments_sql += "id, sentence_id, scope_start, scope_end, error_type, correction, annotator_id"
        segments_sql += ") values('"
        segments_sql += str(uuid.uuid4()) + "'::UUID, '"
        segments_sql += sentence_uuid + "'::UUID, "
        segments_sql += scope_start + ", " + scope_end + ", '"
        segments_sql += error_type + "', $$"
        segments_sql += correction + "$$, "
        segments_sql += annotator_num + ");\n"


def add_to_sentences_sql(sentence_uuid, get_text_id_sql_query, sentence_index, sentence):
    global sentences_sql
    sentences_sql += "insert into core.text_error_analysis_sentences(id, text_id, sentence_num, sentence)"
    sentences_sql += " values('" + sentence_uuid + "'::UUID"
    sentences_sql += ", " + get_text_id_sql_query
    sentences_sql += "::UUID, " + \
        str(sentence_index) + ", &&" + sentence + "&&);\n"


def get_text_id_sql(file_name):
    level = file_name[:2]
    extracted_file_name = file_name[2:]
    sql_query = ''
    if extracted_file_name[0:5] == '_doc_':
        extracted_file_name = extracted_file_name[1:-4] + '_item'
        # core.get_text_id_by_full_code_or_title('doc_18538799202_item');
        sql_query = "core.get_text_id_by_full_code_or_title('" + \
            extracted_file_name + "')"
    elif extracted_file_name[0] == '_':
        year = extracted_file_name[1:5]
        extracted_file_name = extracted_file_name[5:-4]
        # core.get_text_id_by_full_code_or_title('C1 2018 III_003-047');
        sql_query = "core.get_text_id_by_full_code_or_title('" + \
            level + " " + year + " "
        sql_query += extracted_file_name + "')"
    else:
        extracted_file_name = extracted_file_name[:-4]
        # core.get_text_id_by_partial_code_or_title('%III_003-052%');
        sql_query = "core.get_text_id_by_partial_code_or_title('" + \
            level + "______" + \
            extracted_file_name + "')"
    return sql_query


def parse_text(file_name, text):
    get_text_id_sql_query = get_text_id_sql(file_name)
    lines = text.splitlines()
    sentence_count = 0
    segment_count = 0
    sentence_uuid = ''
    for line in lines:
        if line and line[0] == 'S':
            segment_count = 0
            sentence_uuid = str(uuid.uuid4())
            sentence = line[2:]
            add_to_sentences_sql(sentence_uuid, get_text_id_sql_query,
                                 sentence_count, sentence)
            sentence_count += 1
        elif line and line[0] == 'A':
            sentence = line[2:]
            add_to_segments_sql(sentence_uuid, sentence)
            segment_count += 1


# parse_text(mock_file_name, mock)
# print(segments_sql)


def parse_dir():
    for subdir in glob.glob(os.path.join(dir, '*/')):
        path = os.path.dirname(subdir)
        # subdir_name = os.path.basename(path)
        for file in glob.glob(os.path.join(subdir, '*.txt')):
            with open(os.path.join(os.getcwd(), file), 'r') as f:
                file_name = os.path.basename(file)
                text = f.read()
                parse_text(file_name, text)

    with open('sentences_sql.txt', 'w') as file:
        file.write(sentences_sql)
        file.write(segments_sql)


parse_dir()
# print(sentences)
