import os
import dao
import pydriller
import utils
import datetime

def testa_extensao_java(arquivo):
    if '.java' in arquivo:
        return True
    else:
        return False 

def clona_repositorio(my_repositorio):
    try:
        print('Clona repositório promocity')
        comando = f'git clone {my_repositorio}'
        os.system(comando)
        print('Repositorio clonado com sucesso!')
    except Exception as ex:
        print(f'Erro na clonagem do repositorio {my_repositorio}: {str(ex)}')

clona_repositorio(my_repositorio='https://github.com/armandossrecife/promocity.git')
print('Cria a sessão de banco de dados')
db_session = dao.create_session()
print('Cria as tabelas do banco')
dao.create_tables()
print('Tabelas criadas com sucesso!')

# Cria a colecao de CommitsComplete
myCommitsCompleteCollection = dao.CommitsCompleteCollection(db_session)
# Cria a colecao de FilesComplete
myFilesCompleteCollection = dao.FilesCompleteCollection(db_session)

qtd_commits = 0

tempo1 = datetime.datetime.now()
print('Analisa commits e arquivos modificados. Aguarde...')
for commit in pydriller.Repository('promocity').traverse_commits():
    try:
        currentCommit = dao.CommitComplete(
        name='promocity' + '_' + commit.hash,
        hash=commit.hash,
        msg=commit.msg,
        author=commit.author.name,
        committer=commit.committer.email,
        author_date=commit.author_date,
        author_timezone=commit.author_timezone,
        committer_date=commit.committer_date,
        committer_timezone=commit.committer_timezone,
        branches=utils.convert_list_to_str(commit.branches),
        in_main_branch=commit.in_main_branch,
        merge=commit.merge,
        modified_files=utils.convert_modifield_list_to_str(commit.modified_files),
        parents=utils.convert_list_to_str(commit.parents),
        project_name=commit.project_name,
        project_path=commit.project_path,
        deletions=commit.deletions,
        insertions=commit.insertions,
        lines=commit.lines,
        files=commit.files,
        dmm_unit_size=commit.dmm_unit_size,
        dmm_unit_complexity=commit.dmm_unit_complexity,
        dmm_unit_interfacing=commit.dmm_unit_interfacing)
        # salva dados do commit na tabela de commits do banco do repositorio
        myCommitsCompleteCollection.insert_commit(currentCommit)
        qtd_commits = qtd_commits + 1
        # analisa cada um dos arquivos modificados no commit
        for file in commit.modified_files:
            try:
                if file is not None and file.filename is not None:
                    currentFile = dao.FileComplete(
                                    name=file.filename,
                                    hash=commit.hash,
                                    old_path=file.old_path,
                                    new_path=file.new_path,
                                    filename=file.filename,
                                    is_java=testa_extensao_java(file.filename),
                                    change_type=file.change_type.name,
                                    diff=str(file.diff),
                                    diff_parsed=utils.convert_dictionary_to_str(file.diff_parsed),
                                    added_lines=file.added_lines,
                                    deleted_lines=file.deleted_lines,
                                    source_code=str(file.source_code),
                                    source_code_before=str(file.source_code_before),
                                    methods=utils.convert_list_to_str(file.methods),
                                    methods_before=utils.convert_list_to_str(file.methods_before),
                                    changed_methods=utils.convert_list_to_str(file.changed_methods),
                                    nloc=file.nloc,
                                    complexity=file.complexity,
                                    token_count=file.token_count,
                                    commit_id=myCommitsCompleteCollection.query_commit_hash(commit.hash))
                    myFilesCompleteCollection.insert_file(currentFile)
            except Exception as ex:
                print(f'Erro ao inserir arquivo {file.filename} na tabela de files do banco!: {str(ex)}')
    except Exception as ex:
        print(f'Erro ao salvar commit {commit.hash} no banco : {str(ex)}')
db_session.close()
tempo2 = datetime.datetime.now()
print('Sessão de banco de dados fechada!')
print(f'Quantidade de commits analisados: {qtd_commits}')
print(f'Tempo de análise: {tempo2-tempo1}')
