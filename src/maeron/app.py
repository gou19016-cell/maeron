"""Tkinter desktop interface for the Minecraft mod scanner."""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .core import ModInfo, export_json, export_markdown, scan_mods, toggle_enabled


class MaeronApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Maeron - Minecraft MOD 管理・診断")
        self.geometry("1080x620")
        self.folder: Path | None = None
        self.mods: list[ModInfo] = []
        self.query = tk.StringVar()
        self.status_filter = tk.StringVar(value="すべて")
        self.loader_filter = tk.StringVar(value="すべて")
        self._build()

    def _build(self) -> None:
        bar = ttk.Frame(self, padding=8)
        bar.pack(fill="x")
        ttk.Button(bar, text="modsフォルダを選択", command=self.choose_folder).pack(side="left")
        ttk.Button(bar, text="再スキャン", command=self.refresh).pack(side="left", padx=4)
        ttk.Button(bar, text="有効/無効を切替", command=self.toggle_selected).pack(side="left", padx=4)
        ttk.Button(bar, text="エクスポート", command=self.export).pack(side="left", padx=4)
        self.folder_label = ttk.Label(bar, text="フォルダ未選択")
        self.folder_label.pack(side="left", padx=12)
        filters = ttk.Frame(self, padding=(8, 0, 8, 8))
        filters.pack(fill="x")
        ttk.Label(filters, text="検索").pack(side="left")
        search = ttk.Entry(filters, textvariable=self.query, width=28)
        search.pack(side="left", padx=5)
        search.bind("<KeyRelease>", lambda _: self.render())
        ttk.Label(filters, text="状態").pack(side="left", padx=(12, 2))
        status = ttk.Combobox(filters, textvariable=self.status_filter, values=["すべて", "正常", "警告", "エラー候補"], state="readonly", width=12)
        status.pack(side="left")
        status.bind("<<ComboboxSelected>>", lambda _: self.render())
        ttk.Label(filters, text="ローダー").pack(side="left", padx=(12, 2))
        loader = ttk.Combobox(filters, textvariable=self.loader_filter, values=["すべて", "Forge", "NeoForge", "Fabric", "Quilt", "Unknown"], state="readonly", width=12)
        loader.pack(side="left")
        loader.bind("<<ComboboxSelected>>", lambda _: self.render())
        columns = ("state", "name", "id", "version", "loader", "minecraft", "file", "issues")
        self.table = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        headings = {"state":"状態", "name":"MOD名", "id":"MOD ID", "version":"バージョン", "loader":"ローダー", "minecraft":"Minecraft", "file":"JARファイル", "issues":"問題候補"}
        widths = {"state":58,"name":160,"id":130,"version":95,"loader":88,"minecraft":120,"file":210,"issues":280}
        for column in columns:
            self.table.heading(column, text=headings[column])
            self.table.column(column, width=widths[column], minwidth=50)
        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=yscroll.set)
        self.table.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=(0, 8))
        yscroll.pack(side="right", fill="y", padx=(0, 8), pady=(0, 8))
        self.footer = ttk.Label(self, text="modsフォルダを選択してください", anchor="w", padding=8)
        self.footer.pack(side="bottom", fill="x")

    def choose_folder(self) -> None:
        folder = filedialog.askdirectory(title="Minecraft の mods フォルダを選択")
        if folder:
            self.folder = Path(folder)
            self.folder_label.configure(text=str(self.folder))
            self.refresh()

    def refresh(self) -> None:
        if not self.folder:
            return
        try:
            self.mods = scan_mods(self.folder)
        except (OSError, NotADirectoryError) as exc:
            messagebox.showerror("スキャン失敗", str(exc))
            return
        self.render()

    def render(self) -> None:
        self.table.delete(*self.table.get_children())
        query = self.query.get().casefold()
        state = self.status_filter.get()
        loader = self.loader_filter.get()
        visible = 0
        for index, mod in enumerate(self.mods):
            haystack = " ".join((mod.file, mod.name, mod.mod_id, mod.version, mod.loader)).casefold()
            if query and query not in haystack:
                continue
            if loader != "すべて" and mod.loader != loader:
                continue
            if state == "正常" and mod.issues:
                continue
            if state == "警告" and not mod.issues:
                continue
            if state == "エラー候補" and not any("読み取りエラー" in issue or "見つかりません" in issue for issue in mod.issues):
                continue
            self.table.insert("", "end", iid=str(index), values=("有効" if mod.enabled else "無効", mod.name or "不明", mod.mod_id or "不明", mod.version or "不明", mod.loader, ", ".join(mod.minecraft_versions), mod.file, "、".join(mod.issues) or "なし"))
            visible += 1
        warning_count = sum(bool(m.issues) for m in self.mods)
        self.footer.configure(text=f"{visible}/{len(self.mods)} 件表示  |  問題候補 {warning_count} 件")

    def toggle_selected(self) -> None:
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("対象なし", "切り替えるMODを一覧から選択してください")
            return
        mod = self.mods[int(selected[0])]
        action = "無効化" if mod.enabled else "有効化"
        if not messagebox.askyesno("ファイル名変更の確認", f"次のファイルを{action}します。\n\n{mod.file}\n\nファイル名を変更する可逆操作です。"):
            return
        try:
            toggle_enabled(mod.path)
        except (OSError, ValueError) as exc:
            messagebox.showerror("切替失敗", str(exc))
        self.refresh()

    def export(self) -> None:
        if not self.mods:
            messagebox.showinfo("出力対象なし", "先にフォルダを選択してスキャンしてください")
            return
        path = filedialog.asksaveasfilename(title="スキャン結果を保存", defaultextension=".md", filetypes=[("Markdown", "*.md"), ("JSON", "*.json")])
        if not path:
            return
        try:
            (export_json if path.lower().endswith(".json") else export_markdown)(self.mods, path)
            messagebox.showinfo("出力完了", f"保存しました: {path}")
        except OSError as exc:
            messagebox.showerror("出力失敗", str(exc))


def main() -> None:
    MaeronApp().mainloop()


if __name__ == "__main__":
    main()
