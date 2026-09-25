"""Core scanner for Minecraft mod JAR files."""
from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ModInfo:
    file: str
    path: str
    enabled: bool
    name: str = ""
    mod_id: str = ""
    version: str = ""
    loader: str = "Unknown"
    minecraft_versions: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)


def _toml_value(text: str, key: str) -> str:
    match = re.search(r"^\s*" + re.escape(key) + r"\s*=\s*[\"']([^\"']*)[\"']", text, re.M)
    return match.group(1).strip() if match else ""


def _parse_fabric(data: dict[str, Any], result: ModInfo) -> None:
    result.loader = "Fabric"
    result.mod_id = str(data.get("id", ""))
    result.name = str(data.get("name") or result.mod_id)
    result.version = str(data.get("version", ""))
    depends = data.get("depends", {})
    if isinstance(depends, dict):
        result.dependencies = [str(k) for k in depends if k not in ("minecraft", "fabricloader", "java")]
        mc = depends.get("minecraft")
        if mc:
            result.minecraft_versions = [str(mc)]


def _parse_quilt(data: dict[str, Any], result: ModInfo) -> None:
    result.loader = "Quilt"
    q = data.get("quilt_loader", data)
    result.mod_id = str(q.get("id", ""))
    result.name = str(q.get("metadata", {}).get("name") or result.mod_id)
    result.version = str(q.get("version", ""))
    depends = q.get("depends", [])
    if isinstance(depends, list):
        result.dependencies = [str(d.get("id")) for d in depends if isinstance(d, dict) and d.get("id") not in ("minecraft", "quilt_loader")]
        result.minecraft_versions = [str(d.get("versions")) for d in depends if isinstance(d, dict) and d.get("id") == "minecraft" and d.get("versions")]


def _parse_toml(text: str, result: ModInfo, loader: str) -> None:
    result.loader = loader
    # Extract the first [[mods]] table and its simple string fields.
    chunks = re.split(r"(?m)^\s*\[\[mods\]\]\s*$", text)
    section = chunks[1] if len(chunks) > 1 else text
    result.mod_id = _toml_value(section, "modId")
    result.name = _toml_value(section, "displayName") or result.mod_id
    result.version = _toml_value(section, "version")
    result.minecraft_versions = list(dict.fromkeys(re.findall(r"(?:minecraft|\[?\d+\.\d+(?:\.\d+)?\]?)(?:[<>=!~^]+\s*)?\d+\.\d+(?:\.\d+)?", text, re.I)))
    result.dependencies = list(dict.fromkeys(re.findall(r"(?m)^\s*modId\s*=\s*[\"']([^\"']+)[\"']", text)))
    result.dependencies = [d for d in result.dependencies if d != result.mod_id]


def scan_mods(folder: str | Path) -> list[ModInfo]:
    root = Path(folder)
    if not root.is_dir():
        raise NotADirectoryError(str(root))
    files = sorted(p for p in root.iterdir() if p.is_file() and (p.suffix.lower() == ".jar" or p.name.lower().endswith(".jar.disabled")))
    mods: list[ModInfo] = []
    for path in files:
        enabled = path.suffix.lower() == ".jar"
        mod = ModInfo(file=path.name, path=str(path), enabled=enabled)
        try:
            with zipfile.ZipFile(path) as jar:
                names = set(jar.namelist())
                if "fabric.mod.json" in names:
                    _parse_fabric(json.loads(jar.read("fabric.mod.json")), mod)
                elif "quilt.mod.json" in names:
                    _parse_quilt(json.loads(jar.read("quilt.mod.json")), mod)
                elif "META-INF/neoforge.mods.toml" in names:
                    _parse_toml(jar.read("META-INF/neoforge.mods.toml").decode("utf-8", "replace"), mod, "NeoForge")
                elif "META-INF/mods.toml" in names:
                    _parse_toml(jar.read("META-INF/mods.toml").decode("utf-8", "replace"), mod, "Forge")
                else:
                    mod.issues.append("MODメタデータが見つかりません")
        except (OSError, zipfile.BadZipFile, json.JSONDecodeError, KeyError) as exc:
            mod.issues.append(f"読み取りエラー: {exc}")
        if not mod.mod_id and not mod.issues:
            mod.issues.append("MOD IDを取得できません")
        mods.append(mod)
    _diagnose(mods)
    return mods


def _diagnose(mods: list[ModInfo]) -> None:
    enabled = [m for m in mods if m.enabled]
    ids: dict[str, list[ModInfo]] = {}
    for mod in enabled:
        if mod.mod_id:
            ids.setdefault(mod.mod_id, []).append(mod)
    for group in ids.values():
        if len(group) > 1:
            versions = {m.version for m in group}
            message = "同一MOD IDが重複しています" + ("（複数バージョン）" if len(versions) > 1 else "")
            for mod in group:
                mod.issues.append(message)
    available = set(ids)
    for mod in enabled:
        for dependency in mod.dependencies:
            if dependency not in available:
                mod.issues.append(f"依存MODが見つかりません: {dependency}")


def toggle_enabled(path: str | Path) -> Path:
    """Reversibly toggle a JAR's enabled state by adding/removing .disabled."""
    source = Path(path)
    if source.name.lower().endswith(".jar.disabled"):
        target = source.with_name(source.name[:-9])
    elif source.suffix.lower() == ".jar":
        target = source.with_name(source.name + ".disabled")
    else:
        raise ValueError("対象は .jar または .jar.disabled ファイルに限ります")
    if target.exists():
        raise FileExistsError(str(target))
    source.rename(target)
    return target


def export_json(mods: list[ModInfo], destination: str | Path) -> None:
    Path(destination).write_text(json.dumps([m.__dict__ for m in mods], ensure_ascii=False, indent=2), encoding="utf-8")


def export_markdown(mods: list[ModInfo], destination: str | Path) -> None:
    lines = ["# Minecraft MOD scan", "", "| 状態 | MOD名 | ID | バージョン | ローダー | ファイル | 問題 |", "|---|---|---|---|---|---|---|"]
    for m in mods:
        state = "有効" if m.enabled else "無効"
        issues = "、".join(m.issues) or "なし"
        cells = [state, m.name or "不明", m.mod_id or "不明", m.version or "不明", m.loader, m.file, issues]
        lines.append("| " + " | ".join(v.replace("|", "\\|").replace("\n", " ") for v in cells) + " |")
    Path(destination).write_text("\n".join(lines) + "\n", encoding="utf-8")
