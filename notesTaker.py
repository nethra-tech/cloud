import streamlit as st
import sqlite3
from datetime import datetime

# ---------------------------
# PAGE CONFIG
# ---------------------------

st.set_page_config(
    page_title="AI Notes Taker",
    page_icon="📝",
    layout="wide"
)

# ---------------------------
# BLUE THEME CSS
# ---------------------------

st.markdown("""
<style>

.main {
    background-color: #0f172a;
}

.stApp {
    background: linear-gradient(
        135deg,
        #0f172a,
        #1e3a8a
    );
}

h1,h2,h3 {
    color:white !important;
}

.note-card{
    background:#1e293b;
    padding:15px;
    border-radius:12px;
    margin-bottom:10px;
    border-left:5px solid #3b82f6;
}

.small-text{
    color:#cbd5e1;
    font-size:13px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------
# DATABASE
# ---------------------------

conn = sqlite3.connect(
    "notes.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS notes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    created_at TEXT
)
""")

conn.commit()

# ---------------------------
# FUNCTIONS
# ---------------------------

def add_note(title, content):

    cursor.execute(
        """
        INSERT INTO notes
        (title, content, created_at)
        VALUES (?, ?, ?)
        """,
        (
            title,
            content,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        )
    )

    conn.commit()


def get_notes():

    cursor.execute("""
    SELECT * FROM notes
    ORDER BY id DESC
    """)

    return cursor.fetchall()


def update_note(note_id, title, content):

    cursor.execute(
        """
        UPDATE notes
        SET title=?,
            content=?
        WHERE id=?
        """,
        (
            title,
            content,
            note_id
        )
    )

    conn.commit()


def delete_note(note_id):

    cursor.execute(
        """
        DELETE FROM notes
        WHERE id=?
        """,
        (note_id,)
    )

    conn.commit()


# ---------------------------
# HEADER
# ---------------------------

st.title("📝 AI Notes Taker")

st.write(
    "Create, Save, Edit and Manage Notes with SQLite Database"
)

tab1, tab2 = st.tabs(
    [
        "➕ Create Note",
        "📚 View Notes"
    ]
)

# ---------------------------
# CREATE NOTE
# ---------------------------

with tab1:

    st.subheader("Create New Note")

    title = st.text_input(
        "Note Title"
    )

    content = st.text_area(
        "Write Your Notes",
        height=250
    )

    if st.button("💾 Save Note"):

        if title and content:

            add_note(
                title,
                content
            )

            st.success(
                "Note Saved Successfully!"
            )

        else:

            st.warning(
                "Enter title and content"
            )

# ---------------------------
# VIEW NOTES
# ---------------------------

with tab2:

    st.subheader("Saved Notes")

    notes = get_notes()

    if not notes:

        st.info(
            "No notes available."
        )

    for note in notes:

        note_id = note[0]
        note_title = note[1]
        note_content = note[2]
        created = note[3]

        with st.expander(
            f"📝 {note_title}"
        ):

            st.markdown(
                f"""
                <div class='note-card'>
                <div class='small-text'>
                Created: {created}
                </div>
                <br>
                {note_content}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write("### Edit Note")

            new_title = st.text_input(
                "Edit Title",
                value=note_title,
                key=f"title{note_id}"
            )

            new_content = st.text_area(
                "Edit Content",
                value=note_content,
                key=f"content{note_id}"
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "✏ Update",
                    key=f"update{note_id}"
                ):

                    update_note(
                        note_id,
                        new_title,
                        new_content
                    )

                    st.success(
                        "Updated Successfully!"
                    )

                    st.rerun()

            with col2:

                if st.button(
                    "🗑 Delete",
                    key=f"delete{note_id}"
                ):

                    delete_note(
                        note_id
                    )

                    st.success(
                        "Deleted Successfully!"
                    )

                    st.rerun()