import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv

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

def update_nilai(idnya, nama, bio, fis, ing, prediksi):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        UPDATE nilai_siswa
        SET nama_siswa=?, biologi=?, fisika=?, inggris=?, prediksi_fakultas=?
        WHERE id=?
    ''', (nama, bio, fis, ing, prediksi, idnya))
    conn.commit()
    conn.close()

def delete_nilai(idnya):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM nilai_siswa WHERE id=?", (idnya,))
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
    if biologi > fisika and biologi > inggris:
        return 'Kedokteran'
    elif fisika > biologi and fisika > inggris:
        return 'Teknik'
    elif inggris > biologi and inggris > fisika:
        return 'Bahasa'
    else:
        # tie → prioritas Bio → Fis → Inggris
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
        root.minsize(800, 400)

        self.selected_id = None

        # ---------- UI ----------
        style = ttk.Style()
        try: style.theme_use('clam')
        except: pass

        frm_left = ttk.LabelFrame(root, text='Data Input', padding=(12,12))
        frm_left.grid(row=0, column=0, sticky='nws', padx=12, pady=12)

        frm_right = ttk.LabelFrame(root, text='Data Tersimpan', padding=(8,8))
        frm_right.grid(row=0, column=1, sticky='nsew', padx=12, pady=12)

        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)

        ttk.Label(frm_left, text="Nama Siswa:").grid(row=0, column=0, sticky="w")
        self.entry_nama = ttk.Entry(frm_left, width=34)
        self.entry_nama.grid(row=1, column=0, pady=6, sticky="w")

        inner = ttk.Frame(frm_left)
        inner.grid(row=2, column=0, sticky='w', pady=10)
        ttk.Label(inner, text="Biologi:").grid(row=0, column=0)
        self.entry_bio = ttk.Entry(inner, width=8)
        self.entry_bio.grid(row=0, column=1, padx=8)

        ttk.Label(inner, text="Fisika:").grid(row=0, column=2)
        self.entry_fis = ttk.Entry(inner, width=8)
        self.entry_fis.grid(row=0, column=3, padx=8)

        ttk.Label(inner, text="Inggris:").grid(row=0, column=4)
        self.entry_ing = ttk.Entry(inner, width=8)
        self.entry_ing.grid(row=0, column=5)

        btn_frame = ttk.Frame(frm_left)
        btn_frame.grid(row=3, column=0, pady=12, sticky='w')

        self.btn_submit = ttk.Button(btn_frame, text="Submit", command=self.on_submit)
        self.btn_submit.grid(row=0, column=0, padx=5)

        self.btn_update = ttk.Button(btn_frame, text="Update", command=self.on_update)
        self.btn_update.grid(row=0, column=1, padx=5)

        self.btn_delete = ttk.Button(btn_frame, text="Delete", command=self.on_delete)
        self.btn_delete.grid(row=0, column=2, padx=5)

        self.btn_clear = ttk.Button(btn_frame, text="Clear", command=self.clear_form)
        self.btn_clear.grid(row=0, column=3, padx=5)

        columns = ('id','nama','biologi','fisika','inggris','prediksi')
        self.tree = ttk.Treeview(frm_right, columns=columns, show='headings')
        for col, hd in zip(columns, ['ID','Nama','Biologi','Fisika','Inggris','Prediksi']):
            self.tree.heading(col, text=hd)

        self.tree.grid(row=0, column=0, sticky='nsew')
        self.tree.bind("<ButtonRelease-1>", self.on_select_row)

        frm_right.columnconfigure(0, weight=1)
        frm_right.rowconfigure(0, weight=1)

        self.load_table()

    def validate_inputs(self, nama, bio_s, fis_s, ing_s):
        if not nama.strip():
            messagebox.showwarning("Validasi", "Nama siswa harus diisi.")
            return False
        try:
            bio = float(bio_s); fis = float(fis_s); ing = float(ing_s)
        except:
            messagebox.showwarning("Validasi", "Masukkan angka untuk nilai.")
            return False
        for v in (bio, fis, ing):
            if v < 0 or v > 100:
                messagebox.showwarning("Validasi", "Nilai harus 0 - 100.")
                return False
        return True

    def on_submit(self):
        nama = self.entry_nama.get()
        bio_s = self.entry_bio.get()
        fis_s = self.entry_fis.get()
        ing_s = self.entry_ing.get()

        if not self.validate_inputs(nama, bio_s, fis_s, ing_s): return

        bio = float(bio_s); fis = float(fis_s); ing = float(ing_s)
        prediksi = predict_fakultas(bio, fis, ing)

        insert_nilai(nama, bio, fis, ing, prediksi)
        messagebox.showinfo("Sukses", f"Data tersimpan. Prediksi: {prediksi}")
        self.clear_form()
        self.load_table()

    def on_update(self):
        if self.selected_id is None:
            messagebox.showinfo("Update", "Pilih data dari tabel dulu.")
            return

        nama = self.entry_nama.get()
        bio_s = self.entry_bio.get()
        fis_s = self.entry_fis.get()
        ing_s = self.entry_ing.get()

        if not self.validate_inputs(nama, bio_s, fis_s, ing_s): return

        bio = float(bio_s); fis = float(fis_s); ing = float(ing_s)
        prediksi = predict_fakultas(bio, fis, ing)

        update_nilai(self.selected_id, nama, bio, fis, ing, prediksi)
        messagebox.showinfo("Update", "Data berhasil diperbarui.")
        self.clear_form()
        self.load_table()

    def on_delete(self):
        if self.selected_id is None:
            messagebox.showinfo("Delete", "Pilih data dari tabel dulu.")
            return

        confirm = messagebox.askyesno("Hapus", "Yakin ingin menghapus data ini?")
        if confirm:
            delete_nilai(self.selected_id)
            messagebox.showinfo("Delete", "Data berhasil dihapus.")
            self.clear_form()
            self.load_table()

    def on_select_row(self, event):
        selected = self.tree.focus()
        if not selected: return
        data = self.tree.item(selected, "values")

        self.selected_id = int(data[0])
        self.entry_nama.delete(0, tk.END)
        self.entry_nama.insert(0, data[1])

        self.entry_bio.delete(0, tk.END)
        self.entry_bio.insert(0, data[2])

        self.entry_fis.delete(0, tk.END)
        self.entry_fis.insert(0, data[3])

        self.entry_ing.delete(0, tk.END)
        self.entry_ing.insert(0, data[4])

    def load_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = fetch_all()
        for r in rows: self.tree.insert('', tk.END, values=r)

    def clear_form(self):
        self.selected_id = None
        self.entry_nama.delete(0, tk.END)
        self.entry_bio.delete(0, tk.END)
        self.entry_fis.delete(0, tk.END)
        self.entry_ing.delete(0, tk.END)

if __name__ == '__main__':
    init_db()
    root = tk.Tk()
    app = NilaiApp(root)
    root.mainloop()