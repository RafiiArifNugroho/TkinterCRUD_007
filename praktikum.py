import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv
import os

DB_FILE = 'nilai_siswa.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS nilai_siswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_siswa TEXT NOT NULL,
            biologi REAL NOT NULL,
            fisika REAL NOT NULL,
            inggris REAL NOT NULL,
            prediksi_fakultas TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_nilai(nama, bio, fis, ing, prediksi):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO nilai_siswa (nama_siswa, biologi, fisika, inggris, prediksi_fakultas)
        VALUES (?, ?, ?, ?, ?)
    ''', (nama, bio, fis, ing, prediksi))
    conn.commit()
    conn.close()

def fetch_all():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('SELECT id, nama_siswa, biologi, fisika, inggris, prediksi_fakultas FROM nilai_siswa ORDER BY id DESC')
    rows = cur.fetchall()
    conn.close()
    return rows

def predict_fakultas(biologi, fisika, inggris):
    # Logika sederhana: mata pelajaran dengan nilai tertinggi menentukan prediksi
    if biologi > fisika and biologi > inggris:
        return 'Kedokteran'
    elif fisika > biologi and fisika > inggris:
        return 'Teknik'
    elif inggris > biologi and inggris > fisika:
        return 'Bahasa'
    else:
        # jika ada imbang, pilih berdasarkan mana yang sama dengan nilai maksimum (prioritas: Biologi, Fisika, Inggris)
        max_val = max(biologi, fisika, inggris)
        if biologi == max_val:
            return 'Kedokteran'
        elif fisika == max_val:
            return 'Teknik'
        else:
            return 'Bahasa'


class NilaiApp:
    def __init__(self, root):
        self.root = root
        root.title('Input Nilai Siswa - SQLite')
        root.geometry('900x520')
        root.minsize(800, 480)

        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        style.configure('TLabel', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10), padding=6)
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
        style.configure('Treeview', font=('Segoe UI', 10))

        frm_left = ttk.LabelFrame(root, text='Form Input', padding=(12, 12))
        frm_left.grid(row=0, column=0, sticky='nws', padx=12, pady=12)

        frm_right = ttk.LabelFrame(root, text='Data Tersimpan', padding=(8, 8))
        frm_right.grid(row=0, column=1, sticky='nsew', padx=12, pady=12)

        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)

        ttk.Label(frm_left, text='Nama Siswa:', style='Header.TLabel').grid(row=0, column=0, sticky='w')
        self.entry_nama = ttk.Entry(frm_left, width=34)
        self.entry_nama.grid(row=1, column=0, pady=6, sticky='w')

        lbl_nilai = ttk.Label(frm_left, text='Nilai (0-100):', style='Header.TLabel')
        lbl_nilai.grid(row=2, column=0, sticky='w', pady=(8, 0))

        inner = ttk.Frame(frm_left)
        inner.grid(row=3, column=0, sticky='w')

        ttk.Label(inner, text='Biologi').grid(row=0, column=0, padx=(0, 6))
        self.entry_bio = ttk.Entry(inner, width=8)
        self.entry_bio.grid(row=0, column=1, padx=(0, 12))

        ttk.Label(inner, text='Fisika').grid(row=0, column=2, padx=(0, 6))
        self.entry_fis = ttk.Entry(inner, width=8)
        self.entry_fis.grid(row=0, column=3, padx=(0, 12))

        ttk.Label(inner, text='Inggris').grid(row=0, column=4, padx=(0, 6))
        self.entry_ing = ttk.Entry(inner, width=8)
        self.entry_ing.grid(row=0, column=5)

        btn_frame = ttk.Frame(frm_left)
        btn_frame.grid(row=5, column=0, pady=12, sticky='w')

        self.btn_submit = ttk.Button(btn_frame, text='Submit', command=self.on_submit)
        self.btn_submit.grid(row=0, column=0, padx=(0, 8))

        self.btn_clear = ttk.Button(btn_frame, text='Clear', command=self.clear_form)
        self.btn_clear.grid(row=0, column=1, padx=(0, 8))

        # tombol export CSV
        self.btn_export = ttk.Button(btn_frame, text='Export CSV', command=self.export_csv)
        self.btn_export.grid(row=0, column=2, padx=(0, 8))

        # Treeview untuk menampilkan data
        columns = ('id', 'nama', 'biologi', 'fisika', 'inggris', 'prediksi')
        self.tree = ttk.Treeview(frm_right, columns=columns, show='headings')

        for col, hd in zip(columns, ['ID', 'Nama', 'Biologi', 'Fisika', 'Inggris', 'Prediksi Fakultas']):
            self.tree.heading(col, text=hd)

        self.tree.column('id', width=40, anchor='center')
        self.tree.column('nama', width=180, anchor='w')
        self.tree.column('biologi', width=80, anchor='center')
        self.tree.column('fisika', width=80, anchor='center')
        self.tree.column('inggris', width=80, anchor='center')
        self.tree.column('prediksi', width=140, anchor='center')

        vsb = ttk.Scrollbar(frm_right, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(frm_right, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        frm_right.grid_rowconfigure(0, weight=1)
        frm_right.grid_columnconfigure(0, weight=1)

        self.summary = ttk.Label(root, text='', anchor='w')
        self.summary.grid(row=1, column=0, columnspan=2, sticky='we', padx=14)

        # load data awal
        self.load_table()

    def validate_inputs(self, nama, bio_s, fis_s, ing_s):
        if not nama.strip():
            messagebox.showwarning('Validasi', 'Nama siswa harus diisi.')
            return False
        try:
            bio = float(bio_s)
            fis = float(fis_s)
            ing = float(ing_s)
        except ValueError:
            messagebox.showwarning('Validasi', 'Nilai harus berupa angka.')
            return False
        for v in (bio, fis, ing):
            if v < 0 or v > 100:
                messagebox.showwarning('Validasi', 'Nilai harus 0 - 100.')
                return False
        return True

    def on_submit(self):
        nama = self.entry_nama.get()
        bio_s = self.entry_bio.get()
        fis_s = self.entry_fis.get()
        ing_s = self.entry_ing.get()

        if not self.validate_inputs(nama, bio_s, fis_s, ing_s):
            return

        bio = float(bio_s)
        fis = float(fis_s)
        ing = float(ing_s)

        prediksi = predict_fakultas(bio, fis, ing)

        insert_nilai(nama, bio, fis, ing, prediksi)
        messagebox.showinfo('Sukses', f'Data tersimpan. Prediksi: {prediksi}')

        self.clear_form()
        self.load_table()

    def load_table(self):
        # kosongkan treeview
        for i in self.tree.get_children():
            self.tree.delete(i)

        rows = fetch_all()
        for r in rows:
            self.tree.insert('', tk.END, values=r)

        total = len(rows)
        counts = {'Kedokteran': 0, 'Teknik': 0, 'Bahasa': 0}

        for r in rows:
            pred = r[5]
            if pred in counts:
                counts[pred] += 1

        self.summary.config(
            text=f'Total entri: {total}    Kedokteran: {counts["Kedokteran"]}    Teknik: {counts["Teknik"]}    Bahasa: {counts["Bahasa"]}'
        )

    def clear_form(self):
        self.entry_nama.delete(0, tk.END)
        self.entry_bio.delete(0, tk.END)
        self.entry_fis.delete(0, tk.END)
        self.entry_ing.delete(0, tk.END)

    def export_csv(self):
        rows = fetch_all()
        if not rows:
            messagebox.showinfo('Export CSV', 'Tidak ada data untuk diekspor.')
            return

        filename = f'nilai_siswa_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'nama_siswa', 'biologi', 'fisika', 'inggris', 'prediksi_fakultas'])
                writer.writerows(rows)
            messagebox.showinfo('Export CSV', f'Data berhasil diekspor ke {os.path.abspath(filename)}')
        except Exception as e:
            messagebox.showerror('Export CSV', f'Gagal menulis file: {e}')


if __name__ == '__main__':
    init_db()
    root = tk.Tk()
    app = NilaiApp(root)
    root.mainloop()
