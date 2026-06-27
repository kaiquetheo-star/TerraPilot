"""
Acompanhamento de progresso das retificações para o produtor rural.

Persiste histórico em SQLite local (custo zero, offline-first).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import TypedDict


class HistoryEntry(TypedDict):
    issue_code: str
    title: str
    status: str
    registered_at: str
    resolved_at: str | None
    benefit_message: str | None


class ProgressSummary(TypedDict):
    producer_id: str
    resolved_count: int
    total_count: int
    percent: int
    bar_message: str
    pending_issue_codes: list[str]
    is_complete: bool


class CompletionResult(TypedDict):
    issue_code: str
    title: str
    benefit_message: str
    progress: ProgressSummary


_DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "progress" / "retifications.db"
_GUIDES_PATH = Path(__file__).resolve().parents[2] / "guides" / "retification_guides.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def _load_guide_metadata() -> dict[str, dict[str, str]]:
    with _GUIDES_PATH.open(encoding="utf-8") as handle:
        guides = json.load(handle)

    return {
        issue_code: {
            "title": entry["title"],
            "benefit": entry["benefit"],
        }
        for issue_code, entry in guides.items()
    }


def _bar_message(resolved: int, total: int) -> str:
    if total == 0:
        return "Nenhum problema pendente no momento."

    if resolved == total:
        return (
            "Parabéns! Você resolveu todos os problemas. "
            "Aguarde a análise do órgão ambiental."
        )

    remaining = total - resolved
    if resolved == 0:
        return f"Você tem {total} problema(s) para corrigir. Vamos um de cada vez."

    if remaining == 1:
        return f"{resolved} de {total} problemas resolvidos — falta só mais um!"

    if resolved / total >= 0.5:
        return f"{resolved} de {total} problemas resolvidos — falta pouco!"

    return f"{resolved} de {total} problemas resolvidos — continue assim!"


class ProgressTracker:
    """Rastreia retificações pendentes e concluídas por produtor."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path else _DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS retification_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producer_id TEXT NOT NULL,
                    issue_code TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('pending', 'resolved')),
                    registered_at TEXT NOT NULL,
                    resolved_at TEXT,
                    UNIQUE (producer_id, issue_code, status)
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_retification_producer
                ON retification_items (producer_id, status)
                """
            )

    def register_issues(self, producer_id: str, issue_codes: list[str]) -> int:
        """
        Registra problemas pendentes de retificação.

        Returns:
            Quantidade de novos itens registrados (ignora duplicatas pendentes).
        """
        producer_id = producer_id.strip()
        if not producer_id:
            raise ValueError("O identificador do produtor não pode ser vazio.")

        metadata = _load_guide_metadata()
        registered = 0
        now = _utc_now()

        with self._connect() as connection:
            for raw_code in issue_codes:
                issue_code = raw_code.strip().upper()
                if not issue_code:
                    continue
                if issue_code not in metadata:
                    raise KeyError(f"issue_code desconhecido: {issue_code}")

                cursor = connection.execute(
                    """
                    SELECT 1 FROM retification_items
                    WHERE producer_id = ? AND issue_code = ? AND status = 'pending'
                    """,
                    (producer_id, issue_code),
                )
                if cursor.fetchone():
                    continue

                connection.execute(
                    """
                    INSERT INTO retification_items
                    (producer_id, issue_code, status, registered_at)
                    VALUES (?, ?, 'pending', ?)
                    """,
                    (producer_id, issue_code, now),
                )
                registered += 1

        return registered

    def complete_issue(self, producer_id: str, issue_code: str) -> CompletionResult:
        """Marca um problema como resolvido e retorna o benefício tangível."""
        producer_id = producer_id.strip()
        issue_code = issue_code.strip().upper()

        metadata = _load_guide_metadata()
        if issue_code not in metadata:
            raise KeyError(f"issue_code desconhecido: {issue_code}")

        now = _utc_now()

        with self._connect() as connection:
            cursor = connection.execute(
                """
                SELECT id FROM retification_items
                WHERE producer_id = ? AND issue_code = ? AND status = 'pending'
                ORDER BY id DESC
                LIMIT 1
                """,
                (producer_id, issue_code),
            )
            row = cursor.fetchone()

            if row:
                connection.execute(
                    """
                    UPDATE retification_items
                    SET status = 'resolved', resolved_at = ?
                    WHERE id = ?
                    """,
                    (now, row["id"]),
                )
            else:
                connection.execute(
                    """
                    INSERT INTO retification_items
                    (producer_id, issue_code, status, registered_at, resolved_at)
                    VALUES (?, ?, 'resolved', ?, ?)
                    """,
                    (producer_id, issue_code, now, now),
                )

        benefit = metadata[issue_code]["benefit"]
        progress = self.get_progress(producer_id)

        return CompletionResult(
            issue_code=issue_code,
            title=metadata[issue_code]["title"],
            benefit_message=benefit,
            progress=progress,
        )

    def get_progress(self, producer_id: str) -> ProgressSummary:
        """Retorna resumo visual do progresso (barra e mensagem)."""
        producer_id = producer_id.strip()

        with self._connect() as connection:
            total = connection.execute(
                """
                SELECT COUNT(*) AS count FROM retification_items
                WHERE producer_id = ?
                """,
                (producer_id,),
            ).fetchone()["count"]

            resolved = connection.execute(
                """
                SELECT COUNT(*) AS count FROM retification_items
                WHERE producer_id = ? AND status = 'resolved'
                """,
                (producer_id,),
            ).fetchone()["count"]

            pending_rows = connection.execute(
                """
                SELECT issue_code FROM retification_items
                WHERE producer_id = ? AND status = 'pending'
                ORDER BY registered_at ASC
                """,
                (producer_id,),
            ).fetchall()

        percent = round((resolved / total) * 100) if total else 0

        return ProgressSummary(
            producer_id=producer_id,
            resolved_count=resolved,
            total_count=total,
            percent=percent,
            bar_message=_bar_message(resolved, total),
            pending_issue_codes=[row["issue_code"] for row in pending_rows],
            is_complete=total > 0 and resolved == total,
        )

    def get_history(self, producer_id: str, *, limit: int = 20) -> list[HistoryEntry]:
        """Histórico de retificações para o produtor ver que está avançando."""
        producer_id = producer_id.strip()
        metadata = _load_guide_metadata()

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT issue_code, status, registered_at, resolved_at
                FROM retification_items
                WHERE producer_id = ?
                ORDER BY COALESCE(resolved_at, registered_at) DESC
                LIMIT ?
                """,
                (producer_id, limit),
            ).fetchall()

        history: list[HistoryEntry] = []
        for row in rows:
            issue_code = row["issue_code"]
            info = metadata.get(issue_code, {"title": issue_code, "benefit": None})
            history.append(
                HistoryEntry(
                    issue_code=issue_code,
                    title=info["title"],
                    status=row["status"],
                    registered_at=row["registered_at"],
                    resolved_at=row["resolved_at"],
                    benefit_message=info["benefit"] if row["status"] == "resolved" else None,
                )
            )

        return history


def clear_guide_metadata_cache() -> None:
    """Limpa cache de metadados dos guias (útil em testes)."""
    _load_guide_metadata.cache_clear()
