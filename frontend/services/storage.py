"""Local frontend persistence for uploaded analysis sessions and feedback."""

from __future__ import annotations

import datetime
import getpass
import os
import platform
import secrets
import socket
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import psycopg2
import streamlit as st
from dotenv import load_dotenv

PACKAGE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PACKAGE_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")


def _env_is_configured(*names: str) -> bool:
    return all(os.getenv(name) for name in names)


def _placeholder_sql(sql: str, dialect: str) -> str:
    return sql.replace("%s", "?") if dialect == "sqlite" else sql


def _timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")


def parse_admin_credentials() -> dict[str, str]:
    raw_credentials = os.getenv("ADMIN_CREDENTIALS", "").strip()
    if raw_credentials:
        credentials = {}
        for pair in raw_credentials.split(","):
            if ":" not in pair:
                continue
            username, password = pair.split(":", 1)
            if username.strip() and password.strip():
                credentials[username.strip()] = password.strip()
        if credentials:
            return credentials

    username = os.getenv("ADMIN_USERNAME", "").strip()
    password = os.getenv("ADMIN_PASSWORD", "").strip()
    return {username: password} if username and password else {}


@dataclass
class FrontendDatabase:
    connection: object
    dialect: str
    status_message: str | None = None

    def execute(self, sql: str, params=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(_placeholder_sql(sql, self.dialect), params)
            return cursor
        except Exception:
            cursor.close()
            raise

    def fetch_all(self, sql: str, params=()):
        cursor = self.execute(sql, params)
        try:
            return cursor.fetchall()
        finally:
            cursor.close()

    def read_dataframe(self, sql: str) -> pd.DataFrame:
        cursor = self.execute(sql)
        try:
            columns = [column[0] for column in cursor.description]
            return pd.DataFrame(cursor.fetchall(), columns=columns)
        finally:
            cursor.close()

    def text_cast(self, column_name: str) -> str:
        return f"{column_name}::TEXT" if self.dialect == "postgres" else column_name

    def initialize(self):
        if self.dialect == "postgres":
            user_table_sql = """
                CREATE TABLE IF NOT EXISTS user_data (
                    ID SERIAL PRIMARY KEY,
                    sec_token VARCHAR(20) NOT NULL,
                    ip_add VARCHAR(50) NULL,
                    host_name VARCHAR(50) NULL,
                    dev_user VARCHAR(50) NULL,
                    os_name_ver VARCHAR(50) NULL,
                    latlong VARCHAR(50) NULL,
                    city VARCHAR(50) NULL,
                    state VARCHAR(50) NULL,
                    country VARCHAR(50) NULL,
                    act_name VARCHAR(50) NOT NULL,
                    act_mail VARCHAR(50) NOT NULL,
                    act_mob VARCHAR(20) NOT NULL,
                    Name VARCHAR(500) NOT NULL,
                    Email_ID VARCHAR(500) NOT NULL,
                    resume_score VARCHAR(8) NOT NULL,
                    Timestamp VARCHAR(50) NOT NULL,
                    Page_no VARCHAR(5) NOT NULL,
                    Predicted_Field TEXT NOT NULL,
                    User_level TEXT NOT NULL,
                    Actual_skills TEXT NOT NULL,
                    Recommended_skills TEXT NOT NULL,
                    Recommended_courses TEXT NOT NULL,
                    pdf_name VARCHAR(50) NOT NULL,
                    pdf_content BYTEA
                );
            """
            feedback_table_sql = """
                CREATE TABLE IF NOT EXISTS user_feedback (
                    ID SERIAL PRIMARY KEY,
                    feed_name VARCHAR(50) NOT NULL,
                    feed_email VARCHAR(50) NOT NULL,
                    feed_score VARCHAR(5) NOT NULL,
                    comments VARCHAR(100) NULL,
                    Timestamp VARCHAR(50) NOT NULL
                );
            """
        else:
            user_table_sql = """
                CREATE TABLE IF NOT EXISTS user_data (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    sec_token TEXT NOT NULL,
                    ip_add TEXT,
                    host_name TEXT,
                    dev_user TEXT,
                    os_name_ver TEXT,
                    latlong TEXT,
                    city TEXT,
                    state TEXT,
                    country TEXT,
                    act_name TEXT NOT NULL,
                    act_mail TEXT NOT NULL,
                    act_mob TEXT NOT NULL,
                    Name TEXT NOT NULL,
                    Email_ID TEXT NOT NULL,
                    resume_score TEXT NOT NULL,
                    Timestamp TEXT NOT NULL,
                    Page_no TEXT NOT NULL,
                    Predicted_Field TEXT NOT NULL,
                    User_level TEXT NOT NULL,
                    Actual_skills TEXT NOT NULL,
                    Recommended_skills TEXT NOT NULL,
                    Recommended_courses TEXT NOT NULL,
                    pdf_name TEXT NOT NULL,
                    pdf_content BLOB
                );
            """
            feedback_table_sql = """
                CREATE TABLE IF NOT EXISTS user_feedback (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    feed_name TEXT NOT NULL,
                    feed_email TEXT NOT NULL,
                    feed_score TEXT NOT NULL,
                    comments TEXT,
                    Timestamp TEXT NOT NULL
                );
            """

        cursor = self.connection.cursor()
        try:
            cursor.execute(user_table_sql)
            cursor.execute(feedback_table_sql)
            if self.dialect == "postgres":
                cursor.execute("ALTER TABLE user_data ADD COLUMN IF NOT EXISTS pdf_content BYTEA")
            else:
                cursor.execute("PRAGMA table_info(user_data)")
                sqlite_columns = {column[1] for column in cursor.fetchall()}
                if "pdf_content" not in sqlite_columns:
                    cursor.execute("ALTER TABLE user_data ADD COLUMN pdf_content BLOB")
            self.connection.commit()
        finally:
            cursor.close()

    def save_analysis(self, record: dict):
        insert_sql = """
            INSERT INTO user_data
            (sec_token, ip_add, host_name, dev_user, os_name_ver, latlong, city, state, country,
             act_name, act_mail, act_mob, name, email_id, resume_score, timestamp, page_no,
             predicted_field, user_level, actual_skills, recommended_skills, recommended_courses,
             pdf_name, pdf_content)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cursor = self.execute(
            insert_sql,
            (
                record["sec_token"],
                record["ip_add"],
                record["host_name"],
                record["dev_user"],
                record["os_name_ver"],
                record["latlong"],
                record["city"],
                record["state"],
                record["country"],
                record["act_name"],
                record["act_mail"],
                record["act_mob"],
                record["name"],
                record["email"],
                str(record["resume_score"]),
                record["timestamp"],
                str(record["page_no"]),
                record["predicted_field"],
                record["user_level"],
                str(record["actual_skills"]),
                str(record["recommended_skills"]),
                str(record["recommended_courses"]),
                record["pdf_name"],
                record["pdf_content"],
            ),
        )
        cursor.close()
        self.connection.commit()

    def save_feedback(self, *, name: str, email: str, score: int, comments: str):
        cursor = self.execute(
            """
            INSERT INTO user_feedback (feed_name, feed_email, feed_score, comments, timestamp)
            VALUES (%s,%s,%s,%s,%s)
            """,
            (name, email, str(score), comments, _timestamp()),
        )
        cursor.close()
        self.connection.commit()

    def load_feedback(self) -> pd.DataFrame:
        return self.read_dataframe("SELECT * FROM user_feedback")

    def load_comments(self) -> pd.DataFrame:
        rows = self.fetch_all("SELECT feed_name, comments FROM user_feedback")
        return pd.DataFrame(rows, columns=["User", "Comment"])

    def load_admin_frames(self):
        plot_rows = self.fetch_all(
            f"""
            SELECT ID, ip_add, resume_score, {self.text_cast("Predicted_Field")},
                   {self.text_cast("User_level")}, city, state, country
            FROM user_data
            """
        )
        plot_data = pd.DataFrame(
            plot_rows,
            columns=["Idt", "IP_add", "resume_score", "Predicted_Field", "User_Level", "City", "State", "Country"],
        )

        user_rows = self.fetch_all(
            f"""
            SELECT ID, sec_token, ip_add, act_name, act_mail, act_mob, {self.text_cast("Predicted_Field")},
                   Timestamp, Name, Email_ID, resume_score, Page_no, pdf_name, {self.text_cast("User_level")},
                   {self.text_cast("Actual_skills")}, {self.text_cast("Recommended_skills")},
                   {self.text_cast("Recommended_courses")}, city, state, country, latlong, os_name_ver, host_name, dev_user
            FROM user_data
            """
        )
        users_df = pd.DataFrame(
            user_rows,
            columns=[
                "ID", "Token", "IP Address", "Name", "Mail", "Mobile Number", "Predicted Field", "Timestamp",
                "Predicted Name", "Predicted Mail", "Resume Score", "Total Page", "File Name", "User Level",
                "Actual Skills", "Recommended Skills", "Recommended Course", "City", "State", "Country",
                "Lat Long", "Server OS", "Server Name", "Server User",
            ],
        )

        feedback_rows = self.fetch_all("SELECT * FROM user_feedback")
        feedback_df = pd.DataFrame(
            feedback_rows,
            columns=["ID", "Name", "Email", "Feedback Score", "Comments", "Timestamp"],
        )
        return plot_data, users_df, feedback_df


def _connect_sqlite():
    db_path = os.getenv("SQLITE_DB_PATH") or str(PROJECT_ROOT / "data" / "resume_analyzer.db")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path, check_same_thread=False)
    return FrontendDatabase(connection, "sqlite", f"SQLite prototype storage is active at `{db_path}`.")


@st.cache_resource
def get_database() -> FrontendDatabase:
    postgres_env = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")
    if _env_is_configured(*postgres_env):
        try:
            database = FrontendDatabase(
                psycopg2.connect(
                    host=os.getenv("DB_HOST"),
                    port=os.getenv("DB_PORT"),
                    database=os.getenv("DB_NAME"),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                ),
                "postgres",
            )
        except Exception as error:
            database = _connect_sqlite()
            database.status_message = (
                "PostgreSQL connection failed, so the app switched to local SQLite storage for prototype mode. "
                f"Details: {error}"
            )
    else:
        database = _connect_sqlite()

    database.initialize()
    return database


def build_session_record(
    *,
    contact: dict,
    analysis: dict,
    recommended_courses: list[str],
    pdf_name: str,
    pdf_content: bytes,
) -> dict:
    host_name = socket.gethostname()
    try:
        ip_add = socket.gethostbyname(host_name)
    except Exception:
        ip_add = "Unavailable"

    candidate = analysis["candidate"]
    summary = analysis["summary"]
    return {
        "sec_token": secrets.token_urlsafe(12),
        "ip_add": ip_add,
        "host_name": host_name,
        "dev_user": getpass.getuser(),
        "os_name_ver": f"{platform.system()} {platform.release()}",
        "latlong": "",
        "city": "",
        "state": "",
        "country": "",
        "act_name": contact["name"],
        "act_mail": contact["email"],
        "act_mob": contact["mobile"],
        "name": candidate.get("name") or contact["name"],
        "email": candidate.get("email") or contact["email"],
        "resume_score": summary["resume_score"],
        "timestamp": _timestamp(),
        "page_no": candidate.get("page_count", 0),
        "predicted_field": summary["career_track"],
        "user_level": candidate["candidate_level"],
        "actual_skills": candidate["skills"],
        "recommended_skills": summary["recommended_skills"],
        "recommended_courses": recommended_courses,
        "pdf_name": pdf_name,
        "pdf_content": pdf_content,
    }
