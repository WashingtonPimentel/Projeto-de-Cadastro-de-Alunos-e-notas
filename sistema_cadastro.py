import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Conectar ao banco de dados SQLite
conn = sqlite3.connect('sistema_escolar.db')
cursor = conn.cursor()


# Criar tabelas de curso, aluno e notas se não existirem
cursor.execute('''CREATE TABLE IF NOT EXISTS curso (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS aluno (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cpf TEXT, email TEXT, telefone TEXT, curso_id INTEGER, FOREIGN KEY(curso_id) REFERENCES curso(id))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS notas (aluno_id INTEGER PRIMARY KEY, nota1 REAL, nota2 REAL, nota3 REAL, nota4 REAL, FOREIGN KEY(aluno_id) REFERENCES aluno(id))''')
conn.commit()

# Função para cadastrar novo curso
def cadastrar_curso():
    nome = entry_nome_curso.get()
    if nome:
        cursor.execute('INSERT INTO curso (nome) VALUES (?)', (nome,))
        conn.commit()
        messagebox.showinfo('Sucesso', 'Curso cadastrado com sucesso!')
        atualizar_combobox_cursos()
        entry_nome_curso.delete(0, tk.END)
        atualizar_lista_cursos()
    else:
        messagebox.showerror('Erro', 'O nome do curso é obrigatório!')

# Função para atualizar combobox de cursos
def atualizar_combobox_cursos():
    cursor.execute('SELECT id, nome FROM curso')
    cursos = cursor.fetchall()
    combobox_curso_aluno['values'] = [f"{curso[0]} - {curso[1]}" for curso in cursos]

# Função para excluir curso
def excluir_curso():
    try:
        curso_selecionado = listbox_cursos.get(listbox_cursos.curselection())
        curso_id = curso_selecionado.split(' ')[0]
        if curso_selecionado:
            cursor.execute('DELETE FROM curso WHERE id = ?', (curso_id,))
            conn.commit()
            messagebox.showinfo('Sucesso', 'Curso excluído com sucesso!')
            atualizar_combobox_cursos()
            atualizar_lista_cursos()
    except:
        messagebox.showerror('Erro', 'Selecione um curso para excluir!')

# Função para listar cursos cadastrados
def atualizar_lista_cursos():
    listbox_cursos.delete(0, tk.END)
    cursor.execute('SELECT * FROM curso')
    cursos = cursor.fetchall()
    for curso in cursos:
        listbox_cursos.insert(tk.END, f"{curso[0]} - {curso[1]}")

# Função para cadastrar novo aluno
def cadastrar_aluno():
    nome = entry_nome_aluno.get()
    cpf = entry_cpf_aluno.get()
    email = entry_email_aluno.get()
    telefone = entry_telefone_aluno.get()
    curso_id = combobox_curso_aluno.get().split(' ')[0]  # Selecionar ID do curso
    
    if nome and cpf and email and telefone and curso_id:
        cursor.execute('INSERT INTO aluno (nome, cpf, email, telefone, curso_id) VALUES (?, ?, ?, ?, ?)', 
                       (nome, cpf, email, telefone, curso_id))
        conn.commit()
        messagebox.showinfo('Sucesso', 'Aluno cadastrado com sucesso!')
        atualizar_combobox_alunos()
        entry_nome_aluno.delete(0, tk.END)
        entry_cpf_aluno.delete(0, tk.END)
        entry_email_aluno.delete(0, tk.END)
        entry_telefone_aluno.delete(0, tk.END)
        atualizar_lista_alunos()
    else:
        messagebox.showerror('Erro', 'Todos os campos são obrigatórios!')

# Função para atualizar combobox de alunos
def atualizar_combobox_alunos():
    cursor.execute('SELECT id, nome FROM aluno')
    alunos = cursor.fetchall()
    combobox_aluno['values'] = [f"{aluno[0]} - {aluno[1]}" for aluno in alunos]

# Função para excluir aluno
def excluir_aluno():
    try:
        aluno_selecionado = listbox_alunos.get(listbox_alunos.curselection())
        aluno_id = aluno_selecionado.split(' ')[0]
        if aluno_selecionado:
            cursor.execute('DELETE FROM aluno WHERE id = ?', (aluno_id,))
            conn.commit()
            messagebox.showinfo('Sucesso', 'Aluno excluído com sucesso!')
            atualizar_combobox_alunos()
            atualizar_lista_alunos()
    except:
        messagebox.showerror('Erro', 'Selecione um aluno para excluir!')

# Função para listar alunos cadastrados
def atualizar_lista_alunos():
    listbox_alunos.delete(0, tk.END)
    cursor.execute('''SELECT aluno.id, aluno.nome, aluno.cpf, aluno.email, aluno.telefone, curso.nome 
                      FROM aluno LEFT JOIN curso ON aluno.curso_id = curso.id''')
    alunos = cursor.fetchall()
    for aluno in alunos:
        listbox_alunos.insert(tk.END, f"{aluno[0]} - {aluno[1]}, {aluno[2]}, {aluno[3]}, {aluno[4]}, Curso: {aluno[5]}")

# Função para cadastrar ou atualizar notas
def salvar_notas():
    aluno = combobox_aluno.get().split(' ')[0]  # ID do aluno
    try:
        nota1 = float(entry_nota1.get())
        nota2 = float(entry_nota2.get())
        nota3 = float(entry_nota3.get())
        nota4 = float(entry_nota4.get())
        media = (nota1 + nota2 + nota3 + nota4) / 4

        cursor.execute('SELECT aluno_id FROM notas WHERE aluno_id = ?', (aluno,))
        resultado = cursor.fetchone()

        if resultado:
            cursor.execute('''UPDATE notas SET nota1 = ?, nota2 = ?, nota3 = ?, nota4 = ? 
                              WHERE aluno_id = ?''', (nota1, nota2, nota3, nota4, aluno))
        else:
            cursor.execute('''INSERT INTO notas (aluno_id, nota1, nota2, nota3, nota4) 
                              VALUES (?, ?, ?, ?, ?)''', (aluno, nota1, nota2, nota3, nota4))

        conn.commit()
        atualizar_tabela_notas()
        entry_nota1.delete(0, tk.END)
        entry_nota2.delete(0, tk.END)
        entry_nota3.delete(0, tk.END)
        entry_nota4.delete(0, tk.END)
        
        label_media.config(text=f"Média: {media:.2f}")
    except ValueError:
        messagebox.showerror('Erro', 'As notas devem ser números.')

# Função para atualizar a tabela de notas e médias
def atualizar_tabela_notas():
    for row in treeview_notas.get_children():
        treeview_notas.delete(row)

    cursor.execute('''SELECT aluno.id, aluno.nome, 
                             (COALESCE(notas.nota1, 0) + COALESCE(notas.nota2, 0) + COALESCE(notas.nota3, 0) + COALESCE(notas.nota4, 0)) / 
                             (CASE WHEN (COALESCE(notas.nota1, 0) + COALESCE(notas.nota2, 0) + COALESCE(notas.nota3, 0) + COALESCE(notas.nota4, 0)) = 0 THEN 1 ELSE 4 END) AS media,
                             notas.nota1, notas.nota2, notas.nota3, notas.nota4
                      FROM aluno
                      LEFT JOIN notas ON aluno.id = notas.aluno_id''')
    
    rows = cursor.fetchall()
    for row in rows:
        media = row[2] if row[2] is not None else 0
        status = "Aprovado" if media >= 6 else "Reprovado"

        treeview_notas.insert('', tk.END, values=(row[0], row[1], 
                                           row[2] if row[2] is not None else 0,  # Nota 1
                                           row[3] if row[3] is not None else 0,  # Nota 2
                                           row[4] if row[4] is not None else 0,  # Nota 3
                                           row[5] if row[5] is not None else 0,  # Nota 4
                                           media, status))  # Média

# Criar a janela principal
root = tk.Tk()
root.title('Sistema Escolar')
root.geometry('1550x1100')  # Ajustar o tamanho da janela

# Frames para organização da tela (2x2)
frame_curso = tk.Frame(root, relief="groove", borderwidth=2)
frame_curso.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

frame_aluno = tk.Frame(root, relief="groove", borderwidth=2)
frame_aluno.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

frame_notas = tk.Frame(root, relief="groove", borderwidth=2)
frame_notas.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Layout para cadastro de curso
label_nome_curso = tk.Label(frame_curso, text='Nome do Curso:')
label_nome_curso.grid(row=0, column=0, padx=5, pady=5, sticky='e')

entry_nome_curso = tk.Entry(frame_curso)
entry_nome_curso.grid(row=0, column=1, padx=5, pady=5)

button_cadastrar_curso = tk.Button(frame_curso, text='Cadastrar Curso', command=cadastrar_curso)
button_cadastrar_curso.grid(row=1, columnspan=2, pady=5)

label_lista_cursos = tk.Label(frame_curso, text='Cursos Cadastrados:')
label_lista_cursos.grid(row=2, column=0, padx=5, pady=5, sticky='e')

listbox_cursos = tk.Listbox(frame_curso, width=40)
listbox_cursos.grid(row=3, columnspan=2, padx=5, pady=5)

button_excluir_curso = tk.Button(frame_curso, text='Excluir Curso', command=excluir_curso)
button_excluir_curso.grid(row=4, columnspan=2, pady=5)

# Layout para cadastro de aluno
label_nome_aluno = tk.Label(frame_aluno, text='Nome do Aluno:')
label_nome_aluno.grid(row=0, column=0, padx=5, pady=5, sticky='e')

entry_nome_aluno = tk.Entry(frame_aluno)
entry_nome_aluno.grid(row=0, column=1, padx=5, pady=5)

label_cpf_aluno = tk.Label(frame_aluno, text='CPF:')
label_cpf_aluno.grid(row=1, column=0, padx=5, pady=5, sticky='e')

entry_cpf_aluno = tk.Entry(frame_aluno)
entry_cpf_aluno.grid(row=1, column=1, padx=5, pady=5)

label_email_aluno = tk.Label(frame_aluno, text='E-mail:')
label_email_aluno.grid(row=2, column=0, padx=5, pady=5, sticky='e')

entry_email_aluno = tk.Entry(frame_aluno)
entry_email_aluno.grid(row=2, column=1, padx=5, pady=5)

label_telefone_aluno = tk.Label(frame_aluno, text='Telefone:')
label_telefone_aluno.grid(row=3, column=0, padx=5, pady=5, sticky='e')

entry_telefone_aluno = tk.Entry(frame_aluno)
entry_telefone_aluno.grid(row=3, column=1, padx=5, pady=5)

label_curso_aluno = tk.Label(frame_aluno, text='Curso:')
label_curso_aluno.grid(row=4, column=0, padx=5, pady=5, sticky='e')

combobox_curso_aluno = ttk.Combobox(frame_aluno)
combobox_curso_aluno.grid(row=4, column=1, padx=5, pady=5)

button_cadastrar_aluno = tk.Button(frame_aluno, text='Cadastrar Aluno', command=cadastrar_aluno)
button_cadastrar_aluno.grid(row=5, columnspan=2, pady=5)

label_lista_alunos = tk.Label(frame_aluno, text='Alunos Cadastrados:')
label_lista_alunos.grid(row=6, column=0, padx=5, pady=5, sticky='e')

listbox_alunos = tk.Listbox(frame_aluno, width=50)
listbox_alunos.grid(row=7, columnspan=2, padx=5, pady=5)

button_excluir_aluno = tk.Button(frame_aluno, text='Excluir Aluno', command=excluir_aluno)
button_excluir_aluno.grid(row=8, columnspan=2, pady=5)

# Layout para cadastro de notas
label_aluno_notas = tk.Label(frame_notas, text='Selecionar Aluno:')
label_aluno_notas.grid(row=0, column=0, padx=5, pady=5, sticky='e')

combobox_aluno = ttk.Combobox(frame_notas)
combobox_aluno.grid(row=0, column=1, padx=5, pady=5)

label_nota1 = tk.Label(frame_notas, text='Nota 1:')
label_nota1.grid(row=1, column=0, padx=5, pady=5, sticky='e')

entry_nota1 = tk.Entry(frame_notas)
entry_nota1.grid(row=1, column=1, padx=5, pady=5)

label_nota2 = tk.Label(frame_notas, text='Nota 2:')
label_nota2.grid(row=2, column=0, padx=5, pady=5, sticky='e')

entry_nota2 = tk.Entry(frame_notas)
entry_nota2.grid(row=2, column=1, padx=5, pady=5)

label_nota3 = tk.Label(frame_notas, text='Nota 3:')
label_nota3.grid(row=3, column=0, padx=5, pady=5, sticky='e')

entry_nota3 = tk.Entry(frame_notas)
entry_nota3.grid(row=3, column=1, padx=5, pady=5)

label_nota4 = tk.Label(frame_notas, text='Nota 4:')
label_nota4.grid(row=4, column=0, padx=5, pady=5, sticky='e')

entry_nota4 = tk.Entry(frame_notas)
entry_nota4.grid(row=4, column=1, padx=5, pady=5)

button_salvar_notas = tk.Button(frame_notas, text='Salvar Notas', command=salvar_notas)
button_salvar_notas.grid(row=5, columnspan=2, pady=5)

label_media = tk.Label(frame_notas, text='Média: ')
label_media.grid(row=6, columnspan=2, pady=5)

# Tabela para exibir notas
treeview_notas = ttk.Treeview(frame_notas, columns=('ID', 'Nome', 'Nota 1', 'Nota 2', 'Nota 3', 'Nota 4', 'Média', 'Status'), show='headings')
treeview_notas.heading('ID', text='ID')
treeview_notas.heading('Nome', text='Nome')
treeview_notas.heading('Nota 1', text='Nota 1')
treeview_notas.heading('Nota 2', text='Nota 2')
treeview_notas.heading('Nota 3', text='Nota 3')
treeview_notas.heading('Nota 4', text='Nota 4')
treeview_notas.heading('Média', text='Média')
treeview_notas.heading('Status', text='Status')
treeview_notas.grid(row=7, columnspan=2, padx=5, pady=5)

# Iniciar a aplicação
atualizar_combobox_cursos()
atualizar_combobox_alunos()
atualizar_lista_cursos()
atualizar_lista_alunos()
atualizar_tabela_notas()
root.mainloop()

# Fechar a conexão com o banco de dados ao sair
conn.close()
