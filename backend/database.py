import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'rca_database.db')


def get_db():
    """Open a connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # lets us use result['column_name']
    return conn


def init_db():
    """Create all tables if they do not already exist."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS incidents (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            title            TEXT    NOT NULL,
            severity         TEXT    NOT NULL,
            incident_date    TEXT,
            affected_systems TEXT,
            timeline         TEXT    NOT NULL,
            created_at       TEXT    DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS rca_reports (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id      INTEGER NOT NULL,
            full_report_text TEXT    NOT NULL,
            generated_at     TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (incident_id) REFERENCES incidents(id)
        );
    """)
    conn.commit()
    conn.close()
    print("[OK] Database ready.")


def save_incident(title, severity, timeline, incident_date, affected_systems):
    """Insert a new incident row and return its auto-generated id."""
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO incidents
               (title, severity, timeline, incident_date, affected_systems)
           VALUES (?, ?, ?, ?, ?)""",
        (title, severity, timeline, incident_date, affected_systems),
    )
    incident_id = cur.lastrowid
    conn.commit()
    conn.close()
    return incident_id


def save_rca(incident_id, rca_text):
    """Store the AI-generated RCA text linked to an incident."""
    conn = get_db()
    conn.execute(
        "INSERT INTO rca_reports (incident_id, full_report_text) VALUES (?, ?)",
        (incident_id, rca_text),
    )
    conn.commit()
    conn.close()


def get_all_incidents():
    """Return every incident (newest first) as a list of dicts."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM incidents ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_incident_with_rca(incident_id):
    """Return one incident together with its RCA report (if available)."""
    conn = get_db()
    incident = conn.execute(
        "SELECT * FROM incidents WHERE id = ?", (incident_id,)
    ).fetchone()
    rca = conn.execute(
        "SELECT * FROM rca_reports WHERE incident_id = ? ORDER BY generated_at DESC LIMIT 1",
        (incident_id,),
    ).fetchone()
    conn.close()
    if incident:
        result = dict(incident)
        result['rca'] = dict(rca) if rca else None
        return result
    return None


def delete_incident(incident_id):
    """Delete an incident and its associated RCA."""
    conn = get_db()
    conn.execute("DELETE FROM rca_reports WHERE incident_id = ?", (incident_id,))
    conn.execute("DELETE FROM incidents WHERE id = ?", (incident_id,))
    conn.commit()
    conn.close()
