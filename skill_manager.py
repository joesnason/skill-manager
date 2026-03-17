"""Skill Manager - GUI app to view and manage installed Claude Code skills."""

import os
import shutil
import zipfile
import tkinter as tk
from tkinter import messagebox
from dataclasses import dataclass
from pathlib import Path


SKILLS_DIR = Path.home() / ".claude" / "skills"


@dataclass
class SkillInfo:
    name: str
    description: str
    path: Path
    skill_type: str  # "directory" | "zip" | "legacy_md"


def parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter from SKILL.md text. Returns {"name": "", "description": ""} on failure."""
    try:
        lines = text.split("\n")
        if not lines or lines[0].strip() != "---":
            return {"name": "", "description": ""}

        end_idx = None
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                end_idx = i
                break

        if end_idx is None:
            return {"name": "", "description": ""}

        name = ""
        description = ""
        frontmatter_lines = lines[1:end_idx]
        i = 0
        while i < len(frontmatter_lines):
            line = frontmatter_lines[i]
            if line.startswith("name:"):
                name = line[len("name:"):].strip().strip('"').strip("'")
            elif line.startswith("description:"):
                value = line[len("description:"):].strip()
                if value in (">", "|", ">-", "|-"):
                    continuation_lines: list[str] = []
                    i += 1
                    while i < len(frontmatter_lines) and (
                        frontmatter_lines[i].startswith("  ") or frontmatter_lines[i].startswith("\t")
                    ):
                        continuation_lines.append(frontmatter_lines[i].strip())
                        i += 1
                    description = " ".join(continuation_lines)
                    continue
                else:
                    description = value.strip('"').strip("'")
            i += 1

        return {"name": name, "description": description}
    except Exception:
        return {"name": "", "description": ""}


def load_skill_directory(path: Path) -> SkillInfo | None:
    """Load a skill from a directory containing SKILL.md."""
    try:
        skill_md = path / "SKILL.md"
        if not skill_md.exists():
            return None
        data = parse_frontmatter(skill_md.read_text())
        return SkillInfo(
            name=data["name"] or path.name,
            description=data["description"],
            path=path,
            skill_type="directory",
        )
    except Exception:
        return None


def load_skill_zip(path: Path) -> SkillInfo | None:
    """Load a skill from a .skill zip file."""
    try:
        with zipfile.ZipFile(path, "r") as z:
            member = next(
                (m for m in z.namelist() if Path(m).name == "SKILL.md"), None
            )
            if member is None:
                return None
            text = z.read(member).decode("utf-8")
        data = parse_frontmatter(text)
        stem = path.stem
        return SkillInfo(
            name=data["name"] or stem,
            description=data["description"],
            path=path,
            skill_type="zip",
        )
    except Exception:
        return None


def load_skill_legacy_md(path: Path) -> SkillInfo | None:
    """Load a skill from a legacy .md file."""
    try:
        data = parse_frontmatter(path.read_text())
        stem = path.stem
        return SkillInfo(
            name=data["name"] or stem,
            description=data["description"],
            path=path,
            skill_type="legacy_md",
        )
    except Exception:
        return None


def discover_skills() -> list[SkillInfo]:
    """Discover all skills in ~/.claude/skills/."""
    if not SKILLS_DIR.exists():
        return []

    skills = []
    for entry in SKILLS_DIR.iterdir():
        skill = None
        if entry.is_dir() and (entry / "SKILL.md").exists():
            skill = load_skill_directory(entry)
        elif entry.is_file() and entry.suffix == ".skill":
            skill = load_skill_zip(entry)
        elif entry.is_file() and entry.suffix == ".md":
            skill = load_skill_legacy_md(entry)

        if skill is not None:
            skills.append(skill)

    return sorted(skills, key=lambda s: s.name.lower())


def remove_skill(info: SkillInfo) -> None:
    """Remove a skill from the filesystem."""
    if info.skill_type == "directory":
        shutil.rmtree(info.path)
    else:
        os.remove(info.path)


class SkillManagerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Skill Manager")
        self.root.geometry("600x500")
        self.root.minsize(400, 300)
        self.root.configure(bg="#f5f5f5")

        self._build_header()
        self._build_scroll_area()
        self._build_status_bar()

        self.refresh()

    def _build_header(self):
        header = tk.Frame(self.root, bg="#2c2c2c", pady=8)
        header.pack(fill=tk.X)

        title = tk.Label(
            header,
            text="Skill Manager",
            font=("Helvetica", 14, "bold"),
            fg="white",
            bg="#2c2c2c",
            padx=12,
        )
        title.pack(side=tk.LEFT)

        refresh_btn = tk.Label(
            header,
            text="Refresh",
            bg="#1a6fcc",
            fg="white",
            padx=10,
            pady=4,
            cursor="hand2",
            font=("Helvetica", 11),
        )
        refresh_btn.pack(side=tk.RIGHT, padx=10)
        refresh_btn.bind("<Button-1>", lambda e: self.refresh())

    def _build_scroll_area(self):
        container = tk.Frame(self.root, bg="#f5f5f5")
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        self.canvas = tk.Canvas(container, bg="#f5f5f5", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.inner_frame = tk.Frame(self.canvas, bg="#f5f5f5")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

    def _build_status_bar(self):
        status_frame = tk.Frame(self.root, bg="#e0e0e0", pady=5)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = tk.Label(
            status_frame,
            text="",
            font=("Helvetica", 10),
            fg="#555555",
            bg="#e0e0e0",
            padx=12,
        )
        self.status_label.pack(side=tk.LEFT)

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _build_skill_row(self, parent: tk.Frame, info: SkillInfo, idx: int):
        bg = "#ffffff" if idx % 2 == 0 else "#f9f9f9"
        row = tk.Frame(parent, bg=bg, pady=8, padx=10)
        row.pack(fill=tk.X, pady=(0, 1))
        row.columnconfigure(0, weight=1)

        name_label = tk.Label(
            row,
            text=info.name,
            font=("Helvetica", 13, "bold"),
            fg="#1a1a1a",
            bg=bg,
            anchor="w",
        )
        name_label.grid(row=0, column=0, sticky="w")

        remove_btn = tk.Label(
            row,
            text="Remove",
            bg="#cc0000",
            fg="#ffff00",
            padx=8,
            pady=3,
            cursor="hand2",
            font=("Helvetica", 10),
        )
        remove_btn.grid(row=0, column=1, rowspan=2, padx=(8, 0), sticky="ne")
        remove_btn.bind("<Button-1>", lambda e, i=info: self._on_remove_clicked(i))

        desc_text = info.description or "(no description)"
        desc_label = tk.Label(
            row,
            text=desc_text,
            font=("Helvetica", 11),
            fg="#666666",
            bg=bg,
            anchor="w",
            justify=tk.LEFT,
            wraplength=460,
        )
        desc_label.grid(row=1, column=0, sticky="w")

        separator = tk.Frame(parent, bg="#e0e0e0", height=1)
        separator.pack(fill=tk.X)

    def _on_remove_clicked(self, info: SkillInfo):
        confirmed = messagebox.askyesno(
            "Remove Skill",
            f"Remove skill '{info.name}'?\n\nThis cannot be undone.",
            icon=messagebox.WARNING,
        )
        if not confirmed:
            return
        try:
            remove_skill(info)
        except OSError as e:
            messagebox.showerror("Error", f"Failed to remove skill:\n{e}")
            return
        self.root.after(0, self.refresh)

    def refresh(self):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        skills = discover_skills()

        if not skills:
            empty_label = tk.Label(
                self.inner_frame,
                text="No skills installed.",
                font=("Helvetica", 12),
                fg="#999999",
                bg="#f5f5f5",
                pady=40,
            )
            empty_label.pack(expand=True)
        else:
            for idx, info in enumerate(skills):
                self._build_skill_row(self.inner_frame, info, idx)

        count = len(skills)
        noun = "skill" if count == 1 else "skills"
        self.status_label.config(text=f"{count} {noun} installed")

        self.canvas.yview_moveto(0)


def main():
    root = tk.Tk()
    app = SkillManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
