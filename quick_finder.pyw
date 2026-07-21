# -*- coding: utf-8 -*-
"""
快速文件搜索 QuickFinder
- 即输即搜（毫秒级，本地内存索引）
- 自定义搜索范围：勾选盘符 + 添加任意文件夹
- 双击打开 / 右键打开所在位置 / 复制路径
"""
import os
import sys
import json
import sqlite3
import time
import subprocess
import string
from collections import deque

from PySide6.QtCore import (Qt, QThread, Signal, QTimer, QSettings, QSize)
from PySide6.QtGui import QAction, QGuiApplication
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLineEdit, QListWidget,
                               QListWidgetItem, QLabel, QPushButton,
                               QMenu, QFileDialog, QMessageBox, QSplitter,
                               QCheckBox, QScrollArea, QFrame, QProgressBar,
                               QAbstractItemView, QStackedWidget)

APP_NAME = "QuickFinder"
MAX_RESULTS = 120
CACHE_VERSION = 2
RESOURCE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
CHECK_ICON_URL = os.path.join(RESOURCE_DIR, "check.svg").replace("\\", "/")
APP_DATA_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "QuickFinder"
)
CACHE_FILE = os.path.join(APP_DATA_DIR, "quickfinder_index.sqlite3")

APP_STYLE = """
QMainWindow, QWidget#appRoot {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #EAF3FF, stop:0.42 #F2ECFF, stop:0.72 #E7F7FB, stop:1 #F7FAFF);
    color: #1B2333;
    font-family: "Microsoft YaHei UI";
    font-size: 13px;
}
QLabel#brandMark {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #66A6FF, stop:0.52 #5B74F8, stop:1 #9B7AF7);
    color: white;
    border: 1px solid rgba(255,255,255,0.72);
    border-radius: 13px;
    font-size: 21px;
    font-weight: 700;
}
QLabel#appTitle { font-size: 21px; font-weight: 700; color: #182033; }
QLabel#appSubtitle, QLabel#mutedLabel { color: #68748A; font-size: 12px; }
QFrame#sidebar, QFrame#contentCard {
    background: rgba(255, 255, 255, 0.64);
    border: 1px solid rgba(255,255,255,0.9);
    border-radius: 22px;
}
QFrame#glassToolbar {
    background: rgba(255,255,255,0.42);
    border: 1px solid rgba(255,255,255,0.75);
    border-radius: 18px;
}
QLabel#sectionTitle { color: #263147; font-size: 13px; font-weight: 700; }
QLineEdit#searchInput {
    background: rgba(255,255,255,0.78);
    border: 1px solid rgba(255,255,255,0.96);
    border-radius: 18px;
    padding: 0 20px;
    color: #172033;
    selection-background-color: #C7D7FF;
    font-size: 15px;
}
QLineEdit#searchInput:focus { border: 2px solid rgba(76,111,245,0.72); padding-left: 19px; }
QPushButton {
    min-height: 36px;
    padding: 0 14px;
    border: 1px solid rgba(255,255,255,0.9);
    border-radius: 12px;
    background: rgba(255,255,255,0.62);
    color: #354158;
    font-weight: 600;
}
QPushButton:hover { background: rgba(255,255,255,0.88); border-color: white; }
QPushButton:pressed { background: rgba(225,232,247,0.9); }
QPushButton#primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4F82F8, stop:1 #776AF3);
    color: white;
    border: 1px solid rgba(255,255,255,0.58);
    border-radius: 13px;
}
QPushButton#primaryButton:hover { background: #526FEF; }
QPushButton#compactButton { min-height: 32px; padding: 0 12px; font-size: 12px; border-radius: 11px; }
QPushButton#dangerButton { min-height: 32px; padding: 0 12px; font-size: 12px; color: #D54A5C; border-radius: 11px; }
QCheckBox { color: #3A4559; spacing: 9px; min-height: 30px; }
QCheckBox::indicator { width: 17px; height: 17px; }
QCheckBox::indicator:unchecked {
    background: rgba(255,255,255,0.68); border: 1px solid #BFC9DA; border-radius: 6px;
}
QCheckBox::indicator:checked {
    background: #5C7CF3; border: 1px solid #5C7CF3; border-radius: 6px;
    image: url(check.svg);
}
QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }
QListWidget#folderList {
    background: rgba(255,255,255,0.34);
    border: 1px solid rgba(255,255,255,0.62);
    border-radius: 12px;
    padding: 4px;
    outline: none;
}
QListWidget#folderList::item { padding: 7px 8px; border-radius: 8px; }
QListWidget#folderList::item:selected { background: rgba(218,229,255,0.9); color: #3558CC; }
QListWidget#resultList {
    background: transparent;
    border: none;
    outline: none;
    padding: 2px 8px 8px 8px;
}
QListWidget#resultList::item {
    border-bottom: 1px solid rgba(186,197,216,0.26);
    border-radius: 13px;
}
QListWidget#resultList::item:hover { background: rgba(255,255,255,0.47); }
QListWidget#resultList::item:selected { background: rgba(216,228,255,0.72); }
QLabel#fileIcon {
    background: rgba(226,236,255,0.82);
    color: #5479E8;
    border: 1px solid rgba(255,255,255,0.78);
    border-radius: 12px;
    font-size: 17px;
    font-weight: 700;
}
QLabel#folderIcon {
    background: rgba(255,241,202,0.84);
    color: #D39736;
    border: 1px solid rgba(255,255,255,0.78);
    border-radius: 12px;
    font-size: 17px;
    font-weight: 700;
}
QLabel#resultName { color: #1A2233; font-size: 13px; font-weight: 600; }
QLabel#resultPath { color: #778398; font-size: 11px; }
QLabel#resultType {
    color: #647189;
    background: rgba(255,255,255,0.52);
    border: 1px solid rgba(255,255,255,0.68);
    border-radius: 9px;
    padding: 3px 8px;
    font-size: 11px;
}
QLabel#emptyIcon { color: #B8C1D1; font-size: 32px; font-weight: 700; }
QLabel#emptyTitle { color: #364153; font-size: 15px; font-weight: 700; }
QProgressBar { background: rgba(205,214,230,0.55); border: none; border-radius: 3px; }
QProgressBar::chunk { background: #637FF2; border-radius: 3px; }
QSplitter::handle { background: transparent; width: 12px; }
QMenu { background: rgba(250,252,255,0.96); border: 1px solid white; border-radius: 12px; padding: 7px; }
QMenu::item { padding: 9px 30px 9px 13px; border-radius: 8px; }
QMenu::item:selected { background: #E3EBFF; color: #3957C6; }
"""
APP_STYLE = APP_STYLE.replace("url(check.svg)", f"url({CHECK_ICON_URL})")

# 默认排除的目录名（噪音大、无搜索价值）
EXCLUDE_DIRS = {
    "$recycle.bin", "system volume information", "windows", "$windows.~bt",
    "$winreagent", "programdata\\microsoft", "appdata\\local\\temp",
    "node_modules", ".git", ".svn", "__pycache__", ".idea", ".vscode",
    "recovery", "msocache", "perflogs", "config.msi", "$getcurrent",
}
EXCLUDE_FILE_PREFIX = ("~$",)
def get_fixed_drives():
    """返回本机固定磁盘盘符列表，如 ['C:\\', 'D:\\']"""
    drives = []
    try:
        import ctypes
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        DRIVE_FIXED = 3
        for i, letter in enumerate(string.ascii_uppercase):
            if bitmask & (1 << i):
                root = f"{letter}:\\"
                if ctypes.windll.kernel32.GetDriveTypeW(root) == DRIVE_FIXED:
                    drives.append(root)
    except Exception:
        drives = ["C:\\"]
    return drives


# ---------------- 索引器 ----------------

class FileIndex:
    """内存文件名索引。条目: (完整路径, 小写文件名, 是否目录)"""

    def __init__(self):
        self.entries = []

    def clear(self):
        self.entries = []

    def add(self, path, name_lower, is_dir):
        self.entries.append((path, name_lower, is_dir))

    def build_for_roots(self, roots, progress_cb=None, cancel_flag=None):
        """BFS 扫描，进度回调 (count, current_dir)"""
        self.clear()
        count = 0
        for root in roots:
            root = os.path.normpath(root)
            if not os.path.isdir(root):
                continue
            q = deque([root])
            while q:
                if cancel_flag and cancel_flag():
                    return count
                d = q.popleft()
                try:
                    with os.scandir(d) as it:
                        for entry in it:
                            try:
                                name = entry.name
                                low = name.lower()
                                if entry.is_dir(follow_symlinks=False):
                                    if low in EXCLUDE_DIRS:
                                        continue
                                    # 排除掉路径段落入黑名单的（如 AppData\Local\Temp）
                                    self.add(entry.path, low, True)
                                    q.append(entry.path)
                                else:
                                    if low.startswith(EXCLUDE_FILE_PREFIX):
                                        continue
                                    self.add(entry.path, low, False)
                                count += 1
                                if progress_cb and count % 5000 == 0:
                                    progress_cb(count, d)
                            except (PermissionError, OSError):
                                continue
                except (PermissionError, OSError, FileNotFoundError):
                    continue
        return count

    def search(self, query, scope_roots=None, limit=MAX_RESULTS,
               dirs_only=False, cancel_flag=None):
        """
        搜索。空格分隔多个关键词 = AND。
        scope_roots: 限定结果路径须以其开头（用户当前勾选的范围），None 表示全部。
        """
        query = query.strip().lower()
        if not query:
            return []
        terms = query.split()
        results = []
        norm_scope = None
        if scope_roots:
            norm_scope = tuple(os.path.normcase(os.path.normpath(r)) for r in scope_roots)

        for position, (path, name_low, is_dir) in enumerate(self.entries):
            if position % 2048 == 0 and cancel_flag and cancel_flag():
                return []
            if dirs_only and not is_dir:
                continue
            path_low = None
            ok = True
            for t in terms:
                if t in name_low:
                    continue
                if path_low is None:
                    path_low = path.lower()
                if t not in path_low:
                    ok = False
                    break
            if not ok:
                continue
            if norm_scope:
                plow = os.path.normcase(os.path.normpath(path))
                if not any(
                    plow == root or plow.startswith(
                        root if root.endswith(os.sep) else root + os.sep
                    )
                    for root in norm_scope
                ):
                    continue
            results.append((path, is_dir))
            if len(results) >= limit:
                break
        # 文件名匹配优先于路径匹配
        results.sort(key=lambda x: (terms[0] not in os.path.basename(x[0]).lower(), len(x[0])))
        return results

    def save_cache(self, roots):
        """以 SQLite 原子保存索引，不反序列化可执行对象。"""
        cache_dir = os.path.dirname(CACHE_FILE)
        os.makedirs(cache_dir, exist_ok=True)
        temp_file = f"{CACHE_FILE}.{os.getpid()}.{time.time_ns()}.tmp"
        normalized_roots = [os.path.normcase(os.path.normpath(r)) for r in roots]
        conn = sqlite3.connect(temp_file)
        try:
            conn.execute("PRAGMA journal_mode=OFF")
            conn.execute("PRAGMA synchronous=OFF")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            conn.execute(
                "CREATE TABLE entries (path TEXT NOT NULL, name_lower TEXT NOT NULL, is_dir INTEGER NOT NULL)"
            )
            conn.executemany(
                "INSERT INTO entries(path, name_lower, is_dir) VALUES (?, ?, ?)",
                ((path, name, int(is_dir)) for path, name, is_dir in self.entries),
            )
            conn.executemany(
                "INSERT INTO metadata(key, value) VALUES (?, ?)",
                (
                    ("version", str(CACHE_VERSION)),
                    ("roots", json.dumps(normalized_roots, ensure_ascii=False)),
                    ("saved_at", repr(time.time())),
                ),
            )
            conn.commit()
        finally:
            conn.close()
        os.replace(temp_file, CACHE_FILE)

    @staticmethod
    def load_cache():
        conn = sqlite3.connect(CACHE_FILE)
        try:
            conn.execute("PRAGMA query_only=ON")
            metadata = dict(conn.execute("SELECT key, value FROM metadata"))
            if int(metadata.get("version", 0)) != CACHE_VERSION:
                raise ValueError("索引版本已过期")
            roots = json.loads(metadata.get("roots", "[]"))
            if not isinstance(roots, list):
                raise ValueError("索引范围格式无效")
            entries = conn.execute(
                "SELECT path, name_lower, is_dir FROM entries"
            ).fetchall()
        finally:
            conn.close()
        if not isinstance(entries, list):
            raise ValueError("索引格式无效")
        return entries, roots, float(metadata.get("saved_at", 0))


# ---------------- 后台索引线程 ----------------

class IndexWorker(QThread):
    progress = Signal(int, str)
    status = Signal(str)
    done = Signal(int, float, bool, str)   # 总数, 耗时, 已缓存, 错误

    def __init__(self, index, roots):
        super().__init__()
        self.index = index
        self.roots = roots
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        t0 = time.time()
        n = self.index.build_for_roots(
            self.roots,
            progress_cb=lambda c, d: self.progress.emit(c, d),
            cancel_flag=lambda: self._cancel,
        )
        cached = False
        error = ""
        if not self._cancel:
            try:
                self.status.emit("正在保存索引，下次启动将直接载入…")
                self.index.save_cache(self.roots)
                cached = True
            except (OSError, sqlite3.Error, ValueError) as exc:
                error = str(exc)
        self.done.emit(n, time.time() - t0, cached, error)


class CacheLoadWorker(QThread):
    """后台读取缓存，避免大索引加载时冻结窗口。"""
    loaded = Signal(object, object, float, float)
    failed = Signal(str)

    def run(self):
        t0 = time.time()
        try:
            entries, roots, saved_at = FileIndex.load_cache()
            self.loaded.emit(entries, roots, saved_at, time.time() - t0)
        except (OSError, sqlite3.Error, ValueError, TypeError) as exc:
            self.failed.emit(str(exc))


class SearchWorker(QThread):
    """后台检索，保证输入和窗口动画不被大索引阻塞。"""
    done = Signal(str, object, float, bool)

    def __init__(self, index, query, dirs_only, scope_roots):
        super().__init__()
        self.index = index
        self.query = query
        self.dirs_only = dirs_only
        self.scope_roots = scope_roots
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        t0 = time.time()
        results = self.index.search(
            self.query,
            scope_roots=self.scope_roots,
            dirs_only=self.dirs_only,
            cancel_flag=lambda: self._cancel,
        )
        self.done.emit(self.query, results, (time.time() - t0) * 1000, self._cancel)


# ---------------- 主窗口 ----------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME + " - 快速文件搜索")
        self.resize(1040, 700)
        self.setMinimumSize(860, 580)
        self.settings = QSettings("QuickFinder", "QuickFinder")
        self.index = FileIndex()
        self.worker = None
        self.cache_worker = None
        self.search_worker = None
        self.pending_search = None
        self._restoring_scope = True
        self.custom_dirs = json.loads(self.settings.value("custom_dirs", "[]"))
        self.checked_drives = json.loads(self.settings.value("checked_drives", "null"))
        self.indexed_roots = []   # 已索引的根
        self.drive_checks = {}

        self._build_ui()
        self._build_trayless_shortcuts()
        self._restore_scope()
        self._restoring_scope = False

        # 搜索防抖
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(180)
        self.search_timer.timeout.connect(self._do_search)

        # 优先后台载入上次索引，仅首次使用或范围变化时重新扫描。
        QTimer.singleShot(100, self._load_cached_index)

    # ---------- UI ----------
    def _build_ui(self):
        central = QWidget()
        central.setObjectName("appRoot")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 20, 24, 22)
        root.setSpacing(16)

        # 品牌栏
        header = QHBoxLayout()
        header.setSpacing(12)
        mark = QLabel("Q")
        mark.setObjectName("brandMark")
        mark.setAlignment(Qt.AlignCenter)
        mark.setFixedSize(46, 46)
        header.addWidget(mark)

        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        title = QLabel("QuickFinder")
        title.setObjectName("appTitle")
        subtitle = QLabel("在你的电脑中，即刻找到任何文件")
        subtitle.setObjectName("appSubtitle")
        brand_text.addWidget(title)
        brand_text.addWidget(subtitle)
        header.addLayout(brand_text)
        header.addStretch(1)

        shortcut = QLabel("ESC  清空   ·   F5  更新索引")
        shortcut.setObjectName("mutedLabel")
        header.addWidget(shortcut)
        root.addLayout(header)

        # 玻璃搜索栏
        search_glass = QFrame()
        search_glass.setObjectName("glassToolbar")
        search_layout = QHBoxLayout(search_glass)
        search_layout.setContentsMargins(10, 9, 10, 9)
        search_layout.setSpacing(10)
        self.search_edit = QLineEdit()
        self.search_edit.setObjectName("searchInput")
        self.search_edit.setPlaceholderText("搜索文件、文件夹或路径…")
        self.search_edit.setMinimumHeight(54)
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(lambda _: self.search_timer.start())
        search_layout.addWidget(self.search_edit, 1)
        self.scope_hint = QLabel("空格分隔多个关键词")
        self.scope_hint.setObjectName("mutedLabel")
        self.scope_hint.setContentsMargins(8, 0, 8, 0)
        search_layout.addWidget(self.scope_hint)
        root.addWidget(search_glass)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter, 1)

        # 左侧：搜索范围
        left = QFrame()
        left.setObjectName("sidebar")
        left.setMinimumWidth(232)
        left.setMaximumWidth(270)
        lv = QVBoxLayout(left)
        lv.setContentsMargins(18, 18, 18, 18)
        lv.setSpacing(10)
        scope_title = QLabel("搜索范围")
        scope_title.setObjectName("sectionTitle")
        lv.addWidget(scope_title)
        scope_note = QLabel("选择需要建立索引的位置")
        scope_note.setObjectName("mutedLabel")
        lv.addWidget(scope_note)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scope_widget = QWidget()
        self.scope_layout = QVBoxLayout(scope_widget)
        self.scope_layout.setContentsMargins(0, 4, 0, 0)
        self.scope_layout.setSpacing(3)

        for d in get_fixed_drives():
            cb = QCheckBox(f"本地磁盘  {d}")
            cb.setChecked(True)
            cb.stateChanged.connect(self._on_scope_changed)
            self.drive_checks[d] = cb
            self.scope_layout.addWidget(cb)

        # 自定义目录区
        self.custom_label = QLabel("常用文件夹")
        self.custom_label.setObjectName("sectionTitle")
        self.custom_label.setContentsMargins(0, 12, 0, 2)
        self.scope_layout.addWidget(self.custom_label)
        self.custom_list = QListWidget()
        self.custom_list.setObjectName("folderList")
        self.custom_list.setMinimumHeight(86)
        self.custom_list.setMaximumHeight(130)
        self.scope_layout.addWidget(self.custom_list)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        add_btn = QPushButton("＋ 添加")
        add_btn.setObjectName("compactButton")
        del_btn = QPushButton("移除")
        del_btn.setObjectName("dangerButton")
        add_btn.clicked.connect(self._add_dir)
        del_btn.clicked.connect(self._del_dir)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(del_btn)
        self.scope_layout.addLayout(btn_row)
        self.scope_layout.addStretch(1)
        scroll.setWidget(scope_widget)
        lv.addWidget(scroll, 1)

        # 底部按钮：重建索引 + 只搜文件夹
        self.dirs_only = QCheckBox("只显示文件夹")
        self.dirs_only.stateChanged.connect(lambda _: self._do_search())
        lv.addWidget(self.dirs_only)
        reindex_btn = QPushButton("更新搜索索引")
        reindex_btn.setObjectName("primaryButton")
        reindex_btn.clicked.connect(self.rebuild_index)
        lv.addWidget(reindex_btn)
        splitter.addWidget(left)

        # 右侧：结果
        right = QFrame()
        right.setObjectName("contentCard")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(10, 14, 10, 10)
        rv.setSpacing(8)

        result_header = QHBoxLayout()
        result_header.setContentsMargins(10, 0, 10, 0)
        result_title = QLabel("搜索结果")
        result_title.setObjectName("sectionTitle")
        result_header.addWidget(result_title)
        result_header.addStretch(1)
        self.count_label = QLabel("")
        self.count_label.setObjectName("mutedLabel")
        result_header.addWidget(self.count_label)
        rv.addLayout(result_header)

        self.result_stack = QStackedWidget()
        self.result_stack.setStyleSheet("background: transparent;")
        self.result_list = QListWidget()
        self.result_list.setObjectName("resultList")
        self.result_list.setSpacing(2)
        self.result_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.result_list.itemDoubleClicked.connect(self._open_item)
        self.result_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.result_list.customContextMenuRequested.connect(self._context_menu)
        self.result_stack.addWidget(self.result_list)

        empty = QWidget()
        empty_layout = QVBoxLayout(empty)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(7)
        empty_icon = QLabel("⌕")
        empty_icon.setObjectName("emptyIcon")
        empty_icon.setAlignment(Qt.AlignCenter)
        self.empty_title = QLabel("开始搜索")
        self.empty_title.setObjectName("emptyTitle")
        self.empty_title.setAlignment(Qt.AlignCenter)
        self.empty_note = QLabel("输入文件名、类型或路径关键词")
        self.empty_note.setObjectName("mutedLabel")
        self.empty_note.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_icon)
        empty_layout.addWidget(self.empty_title)
        empty_layout.addWidget(self.empty_note)
        self.result_stack.addWidget(empty)
        self.result_stack.setCurrentWidget(empty)
        rv.addWidget(self.result_stack, 1)

        status_row = QHBoxLayout()
        status_row.setContentsMargins(10, 0, 10, 0)
        self.status_label = QLabel("就绪")
        self.status_label.setObjectName("mutedLabel")
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setFixedWidth(72)
        self.progress.setMaximumHeight(6)
        self.progress.hide()
        status_row.addWidget(self.progress)
        status_row.addWidget(self.status_label, 1)
        rv.addLayout(status_row)
        splitter.addWidget(right)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([245, 690])

        self._refresh_custom_list()

    def _build_trayless_shortcuts(self):
        # Esc 清空搜索，F5 重建索引
        esc = QAction(self)
        esc.setShortcut("Esc")
        esc.triggered.connect(self.search_edit.clear)
        self.addAction(esc)
        f5 = QAction(self)
        f5.setShortcut("F5")
        f5.triggered.connect(self.rebuild_index)
        self.addAction(f5)

    # ---------- 搜索范围 ----------
    def _restore_scope(self):
        for p in self.custom_dirs:
            pass
        self._refresh_custom_list()
        if self.checked_drives is not None:
            for d, cb in self.drive_checks.items():
                cb.setChecked(d in self.checked_drives)

    def current_scope(self):
        roots = [d for d, cb in self.drive_checks.items() if cb.isChecked()]
        for i in range(self.custom_list.count()):
            roots.append(self.custom_list.item(i).data(Qt.UserRole))
        return roots

    def _on_scope_changed(self):
        if self._restoring_scope:
            return
        self._persist_scope()
        # 范围变化：若新范围超出已索引范围则重建索引，否则只重新搜索
        scope = self.current_scope()
        if not scope:
            self._do_search()
            return
        if not self._scope_covered(scope):
            self.rebuild_index()
        else:
            self._do_search()

    def _scope_covered(self, scope):
        for s in scope:
            s_norm = os.path.normpath(s).lower()
            covered = False
            for r in self.indexed_roots:
                r_norm = os.path.normpath(r).lower()
                if s_norm == r_norm or s_norm.startswith(r_norm + os.sep):
                    covered = True
                    break
            if not covered:
                return False
        return True

    def _persist_scope(self):
        self.settings.setValue("checked_drives", json.dumps(
            [d for d, cb in self.drive_checks.items() if cb.isChecked()]))
        self.settings.setValue("custom_dirs", json.dumps(self.custom_dirs))

    def _add_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择要加入搜索范围的文件夹")
        if d and d not in self.custom_dirs:
            self.custom_dirs.append(d)
            self._refresh_custom_list()
            self._on_scope_changed()

    def _del_dir(self):
        row = self.custom_list.currentRow()
        if row >= 0:
            self.custom_dirs.pop(row)
            self._refresh_custom_list()
            self._on_scope_changed()

    def _refresh_custom_list(self):
        self.custom_list.clear()
        for d in self.custom_dirs:
            item = QListWidgetItem(os.path.basename(d) or d)
            item.setData(Qt.UserRole, d)
            item.setToolTip(d)
            self.custom_list.addItem(item)

    # ---------- 索引 ----------
    def _load_cached_index(self):
        if not os.path.isfile(CACHE_FILE):
            self.rebuild_index()
            return
        self.progress.show()
        self.status_label.setText("正在载入上次保存的索引…")
        self.cache_worker = CacheLoadWorker(self)
        self.cache_worker.loaded.connect(self._on_cache_loaded)
        self.cache_worker.failed.connect(self._on_cache_failed)
        self.cache_worker.start()

    def _on_cache_loaded(self, entries, cached_roots, saved_at, elapsed):
        current_roots = self.current_scope()
        normalized = [os.path.normcase(os.path.normpath(r)) for r in current_roots]
        if normalized != cached_roots:
            self.status_label.setText("搜索范围已变化，正在更新索引…")
            self.rebuild_index()
            return
        self.index.entries = entries
        self.indexed_roots = list(current_roots)
        self.progress.hide()
        updated = time.strftime("%m-%d %H:%M", time.localtime(saved_at)) if saved_at else "未知"
        self.status_label.setText(
            f"已载入 {len(entries):,} 项 · 用时 {elapsed:.1f} 秒 · 更新于 {updated}"
        )
        self._do_search()

    def _on_cache_failed(self, _error):
        self.progress.hide()
        self.status_label.setText("未找到可用索引，正在首次扫描…")
        self.rebuild_index()

    def rebuild_index(self):
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.cancel()
            self.pending_search = None
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait(2000)
        roots = self.current_scope()
        if not roots:
            self.status_label.setText("请先勾选搜索范围")
            return
        self.indexed_roots = list(roots)
        self.worker = IndexWorker(self.index, roots)
        self.worker.progress.connect(self._on_index_progress)
        self.worker.status.connect(self.status_label.setText)
        self.worker.done.connect(self._on_index_done)
        self.progress.show()
        self.status_label.setText("正在建立索引…")
        self.worker.start()

    def _on_index_progress(self, count, cur_dir):
        self.status_label.setText(f"索引中… 已扫描 {count:,} 项  {cur_dir}")

    def _on_index_done(self, total, elapsed, cached, error):
        self.progress.hide()
        cache_text = "，已保存" if cached else ""
        if error:
            cache_text = "，但保存失败"
        self.status_label.setText(
            f"索引完成：{total:,} 项，耗时 {elapsed:.1f} 秒{cache_text}。即输即搜。"
        )
        self._do_search()

    # ---------- 搜索 ----------
    def _make_result_widget(self, path, is_dir):
        """构建双行玻璃风格结果项。"""
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 7, 12, 7)
        layout.setSpacing(12)

        icon = QLabel("⌑" if is_dir else "◇")
        icon.setObjectName("folderIcon" if is_dir else "fileIcon")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(42, 42)
        layout.addWidget(icon)

        text = QVBoxLayout()
        text.setSpacing(2)
        name = os.path.basename(path.rstrip(os.sep)) or path
        name_label = QLabel(name)
        name_label.setObjectName("resultName")
        path_label = QLabel(os.path.dirname(path) or path)
        path_label.setObjectName("resultPath")
        path_label.setTextInteractionFlags(Qt.NoTextInteraction)
        text.addWidget(name_label)
        text.addWidget(path_label)
        layout.addLayout(text, 1)

        extension = os.path.splitext(name)[1].lstrip(".").upper()
        kind = "文件夹" if is_dir else (extension or "文件")
        kind_label = QLabel(kind[:8])
        kind_label.setObjectName("resultType")
        kind_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(kind_label)
        return row

    def _do_search(self):
        q = self.search_edit.text()
        if not q.strip():
            if self.search_worker and self.search_worker.isRunning():
                self.search_worker.cancel()
            self.pending_search = None
            self.result_list.clear()
            self.count_label.setText("")
            self.empty_title.setText("开始搜索")
            self.empty_note.setText("输入文件名、类型或路径关键词")
            self.result_stack.setCurrentIndex(1)
            return

        request = (q, self.dirs_only.isChecked())
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.cancel()
            self.pending_search = request
            self.count_label.setText("正在更新搜索…")
            return
        self._start_search(*request)

    def _start_search(self, query, dirs_only):
        self.pending_search = None
        self.count_label.setText("搜索中…")
        self.search_worker = SearchWorker(self.index, query, dirs_only, self.current_scope())
        self.search_worker.done.connect(self._on_search_done)
        self.search_worker.finished.connect(self._on_search_finished)
        self.search_worker.start()

    def _on_search_done(self, query, results, dt, canceled):
        if canceled or query != self.search_edit.text():
            return
        self.result_list.setUpdatesEnabled(False)
        self.result_list.clear()
        for path, is_dir in results:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, path)
            item.setToolTip(path)
            item.setSizeHint(QSize(0, 62))
            self.result_list.addItem(item)
            self.result_list.setItemWidget(item, self._make_result_widget(path, is_dir))
        self.result_list.setUpdatesEnabled(True)
        more = "（已达上限，仅显示前部分）" if len(results) >= MAX_RESULTS else ""
        self.count_label.setText(f"{len(results)} 个结果  ·  {dt:.0f} 毫秒 {more}")
        if results:
            self.result_stack.setCurrentIndex(0)
        else:
            self.empty_title.setText("没有找到相关内容")
            self.empty_note.setText("试试更短的关键词，或调整左侧搜索范围")
            self.result_stack.setCurrentIndex(1)

    def _on_search_finished(self):
        finished_worker = self.sender()
        if finished_worker is self.search_worker:
            self.search_worker = None
        finished_worker.deleteLater()
        if self.pending_search:
            query, dirs_only = self.pending_search
            if query == self.search_edit.text() and dirs_only == self.dirs_only.isChecked():
                self._start_search(query, dirs_only)
            else:
                self.pending_search = None

    def closeEvent(self, event):
        """安全结束后台任务，避免关闭时线程仍占用索引文件。"""
        for worker in (self.search_worker, self.worker, self.cache_worker):
            if worker and worker.isRunning():
                if hasattr(worker, "cancel"):
                    worker.cancel()
                worker.wait(1500)
        super().closeEvent(event)

    # ---------- 打开 ----------
    def _open_item(self, item):
        path = item.data(Qt.UserRole)
        try:
            os.startfile(path)
        except OSError as e:
            QMessageBox.warning(self, APP_NAME, f"无法打开：\n{path}\n\n{e}")

    def _context_menu(self, pos):
        item = self.result_list.itemAt(pos)
        if not item:
            return
        path = item.data(Qt.UserRole)
        menu = QMenu(self)
        act_open = menu.addAction("打开")
        act_loc = menu.addAction("打开所在位置")
        act_copy = menu.addAction("复制路径")
        act = menu.exec(self.result_list.mapToGlobal(pos))
        if act == act_open:
            self._open_item(item)
        elif act == act_loc:
            if os.path.isdir(path):
                os.startfile(path)
            else:
                subprocess.run(["explorer", "/select,", os.path.normpath(path)])
        elif act == act_copy:
            QGuiApplication.clipboard().setText(path)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
