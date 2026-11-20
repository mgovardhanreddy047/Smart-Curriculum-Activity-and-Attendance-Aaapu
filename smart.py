import time
import math
import base64
import hashlib
from io import BytesIO
from datetime import datetime
import cv2
import numpy as np
import qrcode
from nicegui import ui, app

# ==============================================================================
# 1. INITIAL DATA & SHARED REAL-TIME STATE (100% PYTHON)
# ==============================================================================
INITIAL_USERS = [
    {
        "id": "92500133046", "name": "M. Madhu Mohan Kumar", "email": "madhu.kumar9250@marwadi.edu",
        "role": "student", "pass": "Madhu@123", "dept": "ICT Sem 3 - Div A", "roll": "92500133046",
        "face_sig": "BIO-FACE-33046-9A8F", "face_vector": None, "photo_b64": None
    },
    {
        "id": "92500133047", "name": "M. Govardhan Reddy", "email": "govardhan.reddy@marwadi.edu",
        "role": "student", "pass": "Govardhan@123", "dept": "ICT Sem 3 - Div A", "roll": "92500133047",
        "face_sig": "BIO-FACE-33047-4C2E", "face_vector": None, "photo_b64": None
    },
    {
        "id": "92500133026", "name": "M. Shivanag", "email": "shivanag.m@marwadi.edu",
        "role": "student", "pass": "Shivanag@123", "dept": "ICT Sem 3 - Div B", "roll": "92500133026",
        "face_sig": "BIO-FACE-33026-7D1B", "face_vector": None, "photo_b64": None
    },
    {
        "id": "92500133034", "name": "K. Preetham", "email": "preetham.k@marwadi.edu",
        "role": "student", "pass": "Preetham@123", "dept": "ICT Sem 3 - Div B", "roll": "92500133034",
        "face_sig": "BIO-FACE-33034-2E9D", "face_vector": None, "photo_b64": None
    },
    # Faculty
    {"id": "FAC-102", "name": "Prof. R. K. Sharma", "email": "prof.sharma@marwadi.edu", "role": "faculty", "pass": "Sharma@123", "dept": "Python Programming", "subject": "PWP"},
    {"id": "FAC01", "name": "Prof. Kawal Kaur", "email": "pwp@marwadi.edu", "role": "faculty", "pass": "Kawal@123", "dept": "Python Web Programming", "subject": "PWP"},
    {"id": "FAC02", "name": "Prof. Biswajit", "email": "dmgt@marwadi.edu", "role": "faculty", "pass": "Biswajit@123", "dept": "Discrete Math & Graph Theory", "subject": "DMGT"},
    {"id": "FAC03", "name": "Prof. Vijay Dubey", "email": "coa@marwadi.edu", "role": "faculty", "pass": "Vijay@123", "dept": "Computer Architecture", "subject": "COA"},
    {"id": "FAC04", "name": "Prof. Alam", "email": "dsc@marwadi.edu", "role": "faculty", "pass": "Alam@123", "dept": "Data Structures in C", "subject": "DSC"},
    # Admin
    {"id": "ADMIN-01", "name": "Class Coordinator (HOD)", "email": "admin.ict@marwadi.edu", "role": "admin", "pass": "Admin@123", "dept": "ICT Department Head", "roll": "ADMIN-01"},
]

def create_default_state():
    return {
        "users": [dict(u) for u in INITIAL_USERS],
        "attendance": {
            "92500133046": {"PWP": {"present": 28, "total": 30}, "DMGT": {"present": 25, "total": 28}, "COA": {"present": 26, "total": 26}, "DSC": {"present": 24, "total": 27}},
            "92500133047": {"PWP": {"present": 26, "total": 30}, "DMGT": {"present": 24, "total": 28}, "COA": {"present": 22, "total": 26}, "DSC": {"present": 25, "total": 27}},
            "92500133026": {"PWP": {"present": 18, "total": 30}, "DMGT": {"present": 15, "total": 28}, "COA": {"present": 14, "total": 26}, "DSC": {"present": 16, "total": 27}},
            "92500133034": {"PWP": {"present": 30, "total": 30}, "DMGT": {"present": 28, "total": 28}, "COA": {"present": 25, "total": 26}, "DSC": {"present": 27, "total": 27}},
        },
        "results": {
            "92500133046": {"sgpa": {"Sem 1": 8.4, "Sem 2": 8.6, "Sem 3": 8.9}, "cgpa": 8.63, "backlogs": 0, "subjects": {"PWP": "AA", "DMGT": "AB", "COA": "AA", "DSC": "BB"}},
            "92500133047": {"sgpa": {"Sem 1": 7.8, "Sem 2": 8.2, "Sem 3": 8.0}, "cgpa": 8.00, "backlogs": 0, "subjects": {"PWP": "AB", "DMGT": "BB", "COA": "AA", "DSC": "AB"}},
            "92500133026": {"sgpa": {"Sem 1": 6.5, "Sem 2": 6.8, "Sem 3": 6.2}, "cgpa": 6.50, "backlogs": 1, "subjects": {"PWP": "BC", "DMGT": "FF", "COA": "CC", "DSC": "BC"}},
            "92500133034": {"sgpa": {"Sem 1": 9.0, "Sem 2": 9.2, "Sem 3": 9.4}, "cgpa": 9.20, "backlogs": 0, "subjects": {"PWP": "AA", "DMGT": "AA", "COA": "AA", "DSC": "AA"}},
        },
        "campus_updates": [
            {"id": "UPD-101", "category": "Assignment", "subject": "PWP", "title": "Django REST API & JWT Auth Lab Assignment", "date": "2026-11-24", "details": "Build a complete CRUD endpoint with token verification and upload your GitHub link.", "postedBy": "Prof. R. K. Sharma"},
            {"id": "UPD-102", "category": "Holiday", "subject": "ALL", "title": "Guru Nanak Jayanti University Holiday", "date": "2026-11-20", "details": "All ICT lectures and laboratory sessions remain suspended.", "postedBy": "Prof. R. K. Sharma"},
            {"id": "UPD-103", "category": "Event", "subject": "ICT Dept", "title": "MU-HACK 2026 Smart Campus Hackathon", "date": "2026-11-28", "details": "24-hour coding sprint in Main Auditorium. Registered participants get On-Duty attendance.", "postedBy": "Prof. Kawal Kaur"},
        ],
        "is_session_live": False,
        "live_subject": "PWP",
        "live_date": datetime.now().strftime("%Y-%m-%d"),
        "live_start_time": datetime.now().strftime("%I:%M %p"),
        "manual_qr_offset": 0,
        "session_marks": {},          # student_id -> {status, source, time}
        "used_qr_tokens": {},         # student_id -> set(tokens)
        "recorded_sessions": [
            {
                "id": "SES-INIT-101",
                "facultyName": "Prof. R. K. Sharma",
                "subject": "PWP",
                "date": "19 Nov 2026",
                "startTime": "10:00 AM",
                "endTime": "10:50 AM",
                "presentCount": 3,
                "absentCount": 1,
                "students": [
                    {"id": "92500133046", "roll": "92500133046", "name": "M. Madhu Mohan Kumar", "status": "Present", "source": "Optical QR (PWP)", "time": "10:02 AM"},
                    {"id": "92500133047", "roll": "92500133047", "name": "M. Govardhan Reddy", "status": "Present", "source": "Optical QR (PWP)", "time": "10:04 AM"},
                    {"id": "92500133026", "roll": "92500133026", "name": "M. Shivanag", "status": "Absent", "source": "Unscanned / Absent", "time": "-"},
                    {"id": "92500133034", "roll": "92500133034", "name": "K. Preetham", "status": "Present", "source": "Optical QR (PWP)", "time": "10:05 AM"},
                ],
            }
        ],
        "mismatch_logs": [],
        "biometric_threshold": 75,
        "live_poll": None,
    }

STATE = create_default_state()

# ==============================================================================
# 2. PYTHON 30s ROLLING QR & OPENCV BIOMETRIC ENGINE
# ==============================================================================
def get_rolling_qr(offset: int = 0):
    epoch30 = int(time.time() // 30)
    valid_until_ms = (epoch30 + 1) * 30000
    seed = f"MU-ICT-ROLLING-QR-{epoch30}-{offset}".encode()
    digest = hashlib.sha256(seed).hexdigest().upper()
    token = f"MU-QR-{int(digest[:6], 16) % 900000 + 100000}-{digest[6:10]}"
    remaining = 30 - (int(time.time()) % 30)
    return token, valid_until_ms, remaining

def make_qr_data_url(payload: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def capture_webcam_frame():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None
    ret, frame = cap.read()
    cap.release()
    return frame if ret else None

def frame_to_b64(frame) -> str:
    _, buf = cv2.imencode(".jpg", frame)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

def compute_biometric_vector(frame) -> np.ndarray:
    h, w, _ = frame.shape
    crop = frame[int(h * 0.175):int(h * 0.825), int(w * 0.175):int(w * 0.825)]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (24, 24)).astype(np.float32).flatten()
    std = np.std(small) or 1.0
    return (small - np.mean(small)) / std

def cosine_similarity_pct(vec_a, vec_b) -> int:
    if vec_a is None or vec_b is None:
        return 0
    denom = (np.linalg.norm(vec_a) * np.linalg.norm(vec_b)) or 1.0
    cos = float(np.dot(vec_a, vec_b) / denom)
    return int(round(max(0.0, min(1.0, (cos + 1.0) / 2.0)) * 100))

def decode_qr_from_bytes(raw_bytes: bytes):
    arr = np.frombuffer(raw_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return None
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)
    return data.strip() if data else None

# ==============================================================================
# 3. MAIN PAGE & ROUTING
# ==============================================================================
@ui.page("/")
def main_page():
    ui.dark_mode().enable()
    ui.colors(primary="#5852f2", secondary="#0f1523", accent="#22d3ee")

    user_id = app.storage.user.get("user_id")
    current_user = next((u for u in STATE["users"] if u["id"] == user_id), None)

    with ui.column().classes("w-full min-h-screen bg-[#090d16] text-slate-100 p-0 m-0"):
        if not current_user:
            render_login_portal()
        else:
            render_portal_dashboard(current_user)

# ==============================================================================
# 4. SYSTEM ACCESS PORTAL (LOGIN SCREEN)
# ==============================================================================
def render_login_portal():
    with ui.column().classes("w-full min-h-screen items-center justify-center p-4"):
        ui.badge("⚡ Marwadi University ICT Department").classes("bg-indigo-950 text-indigo-300 px-3 py-1 rounded-full mb-2")
        ui.label("Smart Curriculum Activity and Attendance App").classes("text-2xl sm:text-3xl font-extrabold text-white text-center")
        ui.label("100% Pure Python Multi-Factor Biometric & Activity Management System").classes("text-xs text-slate-400 mb-6")

        with ui.card().classes("w-full max-w-md bg-[#0f1523] border border-slate-800 rounded-3xl p-6 space-y-4 shadow-2xl"):
            ui.label("System Access Portal").classes("text-lg font-bold text-white")

            role_tabs = ui.tabs(value="Student").classes("w-full bg-[#070a12] rounded-xl")
            with role_tabs:
                ui.tab("Student", icon="school")
                ui.tab("Faculty", icon="groups")
                ui.tab("Admin", icon="shield")

            id_input = ui.input("Enrollment Number / Staff ID", value="92500133046").props("outlined dense dark").classes("w-full")
            pass_input = ui.input("Password", value="Madhu@123", password=True, password_toggle_button=True).props("outlined dense dark").classes("w-full")

            preset_box = ui.column().classes("w-full gap-1.5 pt-2")

            def refresh_presets():
                preset_box.clear()
                role = (role_tabs.value or "Student").lower()
                role_users = [u for u in STATE["users"] if u["role"] == role]
                if role_users:
                    id_input.value = role_users[0].get("roll", role_users[0]["id"])
                    pass_input.value = role_users[0]["pass"]
                with preset_box:
                    ui.label("QUICK DEMO ACCESS PRESETS").classes("text-[10px] font-bold text-slate-500 text-center w-full")
                    for u in role_users:
                        def quick_login(u_obj=u):
                            app.storage.user["user_id"] = u_obj["id"]
                            ui.navigate.to("/")
                        with ui.button(on_click=quick_login).props("flat no-caps").classes("w-full justify-between bg-[#070a12] border border-slate-800 rounded-xl px-3 py-1.5 text-xs"):
                            ui.label(u["name"]).classes("text-slate-200 font-semibold")
                            ui.label(u.get("roll", u["id"])).classes("text-indigo-400 font-mono text-[11px]")

            role_tabs.on_value_change(lambda _: refresh_presets())
            refresh_presets()

            def handle_login():
                role = (role_tabs.value or "Student").lower()
                found = next((
                    u for u in STATE["users"]
                    if (u["id"].lower() == id_input.value.strip().lower()
                        or u["email"].lower() == id_input.value.strip().lower()
                        or u.get("roll", "").lower() == id_input.value.strip().lower())
                    and u["pass"] == pass_input.value
                ), None)
                if not found:
                    ui.notify("Invalid ID / Enrollment Number or Password.", type="negative")
                    return
                if found["role"] != role:
                    ui.notify(f"This user is registered as {found['role'].upper()}. Select that tab.", type="warning")
                    return
                app.storage.user["user_id"] = found["id"]
                ui.navigate.to("/")

            ui.button("Sign In to Portal", on_click=handle_login).classes("w-full bg-[#5852f2] text-white font-bold rounded-xl py-2.5")

# ==============================================================================
# 5. MAIN PORTAL DASHBOARD (ROLE-BASED NAVIGATION)
# ==============================================================================
def render_portal_dashboard(user: dict):
    role = user["role"]
    default_tab = "directory" if role == "admin" else ("live" if role == "faculty" else "student-dashboard")
    active_tab = {"name": default_tab}

    # Top Header
    with ui.row().classes("w-full h-14 border-b border-slate-800 bg-[#0c101c] items-center justify-between px-6"):
        with ui.row().classes("items-center gap-3"):
            ui.avatar("MU", color="indigo").classes("font-bold text-xs")
            with ui.column().classes("gap-0"):
                ui.label("Marwadi University ICT").classes("text-sm font-bold text-white")
                ui.label("● Smart Attendance & Activity System (Pure Python)").classes("text-[10px] text-emerald-400 font-semibold")

        with ui.row().classes("items-center gap-3"):
            ui.badge(f"{user['name']} ({role.upper()})").classes("bg-slate-900 border border-slate-700 text-slate-200 px-3 py-1")
            ui.button("Logout", icon="logout", on_click=lambda: (app.storage.user.clear(), ui.navigate.to("/"))).props("dense").classes("bg-red-600 text-white font-bold rounded-xl px-3")

    with ui.row().classes("w-full flex-1 no-wrap items-stretch"):
        sidebar = ui.column().classes("w-64 border-r border-slate-800 bg-[#0c101c] p-4 gap-1.5 shrink-0")
        content = ui.column().classes("flex-1 p-6 gap-5 overflow-y-auto")

        nav_config = {
            "admin": [
                ("analytics", "System Analytics", "bar_chart"),
                ("directory", "User Directory & Keys", "group"),
                ("defaulters", "Defaulter Alerts (<75%)", "warning"),
                ("curriculum", "Master Curriculum", "menu_book"),
                ("logs", "Activity Logs", "receipt_long"),
                ("allocator", "Classroom Allocator", "place"),
                ("sensitivity", "Biometric Sensitivity", "tune"),
            ],
            "faculty": [
                ("live", "Live Attendance Engine", "videocam"),
                ("recorded", "Recorded Sessions & List", "history"),
                ("updates", "Assignments, Holidays & Events", "event"),
                ("grades", "Grade & Result Entry", "emoji_events"),
                ("polls", "Live Quiz & Polls", "poll"),
                ("plagiarism", "Assignment Plagiarism", "fact_check"),
                ("alerts", "Low Attendance Alerts", "notifications"),
            ],
            "student": [
                ("student-dashboard", "Student Dashboard", "dashboard"),
                ("scan", "Scan Faculty QR", "qr_code_scanner"),
                ("timetable", "Timetable & Schedule", "schedule"),
                ("assignments", "Assignments Hub", "code"),
                ("results", "Results & Transcript", "school"),
                ("curriculum-progress", "Curriculum Progress", "auto_stories"),
                ("holidays-events", "Holidays & Events", "celebration"),
            ],
        }[role]

        def render_view():
            sidebar.clear()
            with sidebar:
                for key, label, icon_name in nav_config:
                    is_act = active_tab["name"] == key
                    cls = "bg-[#5852f2] text-white font-bold" if is_act else "text-slate-400 hover:bg-slate-800"
                    ui.button(label, icon=icon_name, on_click=lambda k=key: (active_tab.update({"name": k}), render_view())).props("flat align=left no-caps").classes(f"w-full rounded-xl text-xs px-3 py-2 {cls}")

            content.clear()
            with content:
                t = active_tab["name"]
                # Admin
                if t == "directory": render_admin_directory(render_view)
                elif t == "analytics": render_admin_analytics()
                elif t == "defaulters": render_admin_defaulters()
                elif t == "curriculum": render_admin_curriculum()
                elif t == "logs": render_admin_logs()
                elif t == "allocator": render_admin_allocator()
                elif t == "sensitivity": render_admin_sensitivity()
                # Faculty
                elif t == "live": render_faculty_live(user, render_view)
                elif t == "recorded": render_faculty_recorded(user, render_view)
                elif t == "updates": render_faculty_updates(user, render_view)
                elif t == "grades": render_faculty_grades()
                elif t == "polls": render_faculty_polls(render_view)
                elif t == "plagiarism": render_faculty_plagiarism()
                elif t == "alerts": render_faculty_alerts()
                # Student
                elif t == "student-dashboard": render_student_dashboard(user, lambda k: (active_tab.update({"name": k}), render_view()))
                elif t == "scan": render_student_qr_scanner(user)
                elif t == "timetable": render_student_timetable()
                elif t == "assignments": render_student_assignments(render_view)
                elif t == "results": render_student_results(user)
                elif t == "curriculum-progress": render_student_curriculum()
                elif t == "holidays-events": render_student_holidays()

        render_view()

# ==============================================================================
# 6. ADMIN VIEWS
# ==============================================================================
def render_admin_directory(refresh_fn):
    with ui.row().classes("w-full items-center justify-between"):
        ui.label("USER DIRECTORY & BIOMETRIC KEYS").classes("text-base font-bold text-white")
        def reset_demo():
            STATE.clear()
            STATE.update(create_default_state())
            ui.notify("Demo data reset to defaults.", type="positive")
            refresh_fn()
        ui.button("Reset Demo Data", icon="refresh", on_click=reset_demo).props("dense").classes("bg-slate-800 text-slate-200 text-xs px-3 rounded-xl")

    with ui.card().classes("w-full bg-[#0e1422] border border-slate-800 rounded-2xl p-4"):
        for u in STATE["users"]:
            with ui.row().classes("w-full items-center justify-between border-b border-slate-800/70 py-2.5"):
                with ui.column().classes("gap-0"):
                    ui.label(f"{u['name']} ({u.get('roll', u['id'])})").classes("font-bold text-white text-xs")
                    ui.label(f"Role: {u['role'].upper()} • Email: {u['email']} • Pass: {u['pass']}").classes("text-[11px] font-mono text-slate-400")
                with ui.row().classes("gap-2"):
                    if u["role"] == "student":
                        def enroll_face(stu=u):
                            frame = capture_webcam_frame()
                            if frame is None:
                                ui.notify("Webcam unavailable on host machine.", type="warning")
                                return
                            stu["face_vector"] = compute_biometric_vector(frame)
                            stu["photo_b64"] = frame_to_b64(frame)
                            ui.notify(f"Enrolled live face vector for {stu['name']}!", type="positive")
                            refresh_fn()
                        lbl = "✓ Enrolled (Update)" if u.get("face_vector") is not None else "Enroll Webcam Face"
                        ui.button(lbl, icon="photo_camera", on_click=enroll_face).props("dense").classes("bg-indigo-600 text-white text-xs px-3 rounded-xl")

def render_admin_analytics():
    ui.label("SYSTEM ANALYTICS OVERVIEW").classes("text-base font-bold text-white")
    with ui.row().classes("w-full gap-4"):
        for title, val, cls in [
            ("Total Registered Users", str(len(STATE["users"])), "text-white"),
            ("Overall Attendance Avg", "84.2%", "text-emerald-400"),
            ("Defaulter Students (<75%)", "1", "text-red-400"),
            ("Biometric & QR Mismatches", f"{len(STATE['mismatch_logs'])} Alerts", "text-amber-400"),
        ]:
            with ui.card().classes("flex-1 bg-[#0e1422] border border-slate-800 rounded-2xl p-4"):
                ui.label(title).classes("text-xs text-slate-400")
                ui.label(val).classes(f"text-2xl font-extrabold {cls}")

def render_admin_defaulters():
    ui.label("DEFAULTER ALERTS (<75%)").classes("text-base font-bold text-white")
    with ui.card().classes("w-full bg-red-950/40 border border-red-800 rounded-2xl p-4"):
        with ui.row().classes("w-full items-center justify-between"):
            ui.label("M. Shivanag (92500133026) — Current Attendance: 57.1% (PWP: 60%, DMGT: 53%)").classes("font-bold text-red-300 text-xs")
            ui.button("Dispatch Warning Letter", on_click=lambda: ui.notify("Warning letter sent to student & parent!", type="positive")).classes("bg-red-600 text-white text-xs")

def render_admin_curriculum():
    ui.label("MASTER CURRICULUM TRACKER").classes("text-base font-bold text-white")
    with ui.row().classes("w-full gap-4"):
        with ui.card().classes("flex-1 bg-[#0e1422] border border-slate-800 rounded-2xl p-4"):
            ui.label("PWP - Python Web Programming").classes("font-bold text-indigo-300 text-sm")
            ui.label("Modules: NiceGUI, Django, Flask, REST APIs, ORM Database Layer").classes("text-xs text-slate-400")
        with ui.card().classes("flex-1 bg-[#0e1422] border border-slate-800 rounded-2xl p-4"):
            ui.label("DMGT - Discrete Math & Graph Theory").classes("font-bold text-indigo-300 text-sm")
            ui.label("Modules: Combinatorics, Euler Graphs, Propositional Logic").classes("text-xs text-slate-400")

def render_admin_logs():
    ui.label("SYSTEM SECURITY & ACTIVITY LOGS").classes("text-base font-bold text-white")
    with ui.card().classes("w-full bg-[#0e1422] border border-slate-800 rounded-2xl p-4 font-mono text-xs"):
        ui.label("[SYSTEM] Multi-factor 30s dynamic class QR & OpenCV biometric engine active").classes("text-emerald-400")
        for log in STATE["mismatch_logs"]:
            ui.label(f"[SECURITY MISMATCH @ {log['time']}] {log['student']}").classes("text-red-400")

def render_admin_allocator():
    ui.label("CLASSROOM LOCATION ALLOCATOR").classes("text-base font-bold text-white")
    with ui.card().classes("w-full bg-[#0e1422] border border-slate-800 rounded-2xl p-4 space-y-2"):
        ui.label("Lab ICT 301 — Prof. Kawal Kaur (PWP - Python Web Programming)").classes("text-xs font-bold text-white")
        ui.label("Hall ICT 204 — Prof. Biswajit (DMGT - Discrete Math)").classes("text-xs font-bold text-white")

def render_admin_sensitivity():
    ui.label("BIOMETRIC SENSITIVITY CONTROLS").classes("text-base font-bold text-white")
    with ui.card().classes("w-full max-w-md bg-[#0e1422] border border-slate-800 rounded-2xl p-5"):
        lbl = ui.label(f"Adaptive Face Matching Confidence Threshold: {STATE['biometric_threshold']}%").classes("text-xs font-bold text-indigo-300")
        def on_change(e):
            STATE["biometric_threshold"] = int(e.value)
            lbl.text = f"Adaptive Face Matching Confidence Threshold: {STATE['biometric_threshold']}%"
        ui.slider(min=65, max=92, value=STATE["biometric_threshold"], on_change=on_change)

# ==============================================================================
# 7. FACULTY VIEWS
# ==============================================================================
def render_faculty_live(faculty_user: dict, refresh_fn):
    students = [u for u in STATE["users"] if u["role"] == "student"]
    ui.label("LIVE ATTENDANCE ENGINE").classes("text-base font-bold text-white")

    if not STATE["is_session_live"]:
        with ui.card().classes("w-full max-w-lg bg-[#0e1422] border border-slate-800 rounded-3xl p-6 space-y-3"):
            ui.label("Start New Live Class Session").classes("text-base font-bold text-white")
            subj_sel = ui.select(["PWP", "DMGT", "COA", "DSC"], value=faculty_user.get("subject", "PWP"), label="Subject").props("outlined dense dark").classes("w-full")
            date_inp = ui.input("Session Date", value=datetime.now().strftime("%Y-%m-%d")).props("outlined dense dark").classes("w-full")
            time_inp = ui.input("Start Time", value=datetime.now().strftime("%I:%M %p")).props("outlined dense dark").classes("w-full")

            def start_live():
                STATE["live_subject"] = subj_sel.value
                STATE["live_date"] = date_inp.value
                STATE["live_start_time"] = time_inp.value
                STATE["session_marks"] = {}
                STATE["manual_qr_offset"] += 1
                STATE["is_session_live"] = True
                refresh_fn()

            ui.button("Start Live Session", icon="videocam", on_click=start_live).classes("w-full bg-[#5852f2] text-white font-bold rounded-xl py-2.5")
        return

    subj = STATE["live_subject"]
    with ui.row().classes("w-full bg-indigo-950/50 border border-indigo-500/40 rounded-2xl p-4 items-center justify-between"):
        ui.label(f"LIVE: {subj} • Date: {STATE['live_date']} • Start Time: {STATE['live_start_time']}").classes("font-bold text-cyan-300 text-xs")

        def stop_session():
            end_t = datetime.now().strftime("%I:%M %p")
            breakdown = []
            present_cnt = 0
            for s in students:
                m = STATE["session_marks"].get(s["id"])
                is_p = bool(m and m["status"] == "Marked as Present")
                if is_p:
                    present_cnt += 1
                breakdown.append({
                    "id": s["id"], "roll": s["roll"], "name": s["name"],
                    "status": "Present" if is_p else "Absent",
                    "source": m["source"] if is_p else "Unscanned / Absent",
                    "time": m["time"] if is_p else "-"
                })
            STATE["recorded_sessions"].insert(0, {
                "id": f"SES-{int(time.time())}",
                "facultyName": faculty_user["name"],
                "subject": subj,
                "date": STATE["live_date"],
                "startTime": STATE["live_start_time"],
                "endTime": end_t,
                "presentCount": present_cnt,
                "absentCount": len(students) - present_cnt,
                "students": breakdown
            })
            STATE["is_session_live"] = False
            STATE["session_marks"] = {}
            ui.notify("Live Session Stopped & Saved to Recorded Sessions!", type="positive")
            refresh_fn()

        ui.button("Stop Live Session & Save Record", icon="stop_circle", on_click=stop_session).classes("bg-red-600 text-white font-bold rounded-xl px-4 text-xs")

    # 30-Second Rolling QR Panel
    with ui.card().classes("w-full max-w-xl bg-[#0e1422] border border-indigo-500/30 rounded-2xl p-5 items-center text-center"):
        ui.label(f"Dynamic 30-Second Class QR Code ({subj})").classes("text-sm font-bold text-white")
        timer_lbl = ui.label("").classes("text-xs font-mono text-indigo-300")
        qr_img = ui.image("").classes("w-52 h-52 bg-white p-3 rounded-2xl")
        code_lbl = ui.label("").classes("text-[11px] font-mono text-slate-400")

        def tick_qr():
            token, valid_until, rem = get_rolling_qr(STATE["manual_qr_offset"])
            payload = f"MU-CLASS-QR|{token}|{subj}|{valid_until}"
            qr_img.set_source(make_qr_data_url(payload))
            timer_lbl.text = f"Token: {token} • Refreshes in {rem}s"
            code_lbl.text = payload

        tick_qr()
        ui.timer(1.0, tick_qr)
        ui.button("Generate New QR Pattern Now", icon="refresh", on_click=lambda: (STATE.update({"manual_qr_offset": STATE["manual_qr_offset"] + 1}), tick_qr())).classes("bg-indigo-600 text-white text-xs rounded-xl mt-2")

    # OpenCV Face Photo Verification
    with ui.card().classes("w-full max-w-xl bg-[#0e1422] border border-slate-800 rounded-2xl p-5 space-y-3"):
        ui.label("AI Face Photo Scanner (OpenCV Python Engine)").classes("text-sm font-bold text-white")
        target_sel = ui.select({s["id"]: f"{s['name']} ({s['roll']})" for s in students}, value=students[0]["id"], label="Target Student").props("outlined dense dark").classes("w-full")

        def scan_face():
            stu = next(s for s in students if s["id"] == target_sel.value)
            if stu.get("face_vector") is None:
                ui.notify(f"{stu['name']} has no enrolled reference photo in Admin Directory.", type="negative")
                return
            frame = capture_webcam_frame()
            if frame is None:
                ui.notify("Webcam unavailable on server.", type="warning")
                return
            live_vec = compute_biometric_vector(frame)
            sim = cosine_similarity_pct(live_vec, stu["face_vector"])
            if sim >= STATE["biometric_threshold"]:
                mark_present(stu["id"], subj, f"Python Face Photo Match ({sim}%)")
                ui.notify(f"Marked as Present! Matched {stu['name']} ({sim}% similarity).", type="positive")
                refresh_fn()
            else:
                STATE["mismatch_logs"].append({"student": f"Face Mismatch: {stu['name']} ({sim}%)", "time": datetime.now().strftime("%H:%M:%S")})
                ui.notify(f"Mismatch! Similarity {sim}% < {STATE['biometric_threshold']}%", type="negative")

        ui.button("Scan & Compare Face Photo", icon="photo_camera", on_click=scan_face).classes("w-full bg-indigo-600 text-white font-bold rounded-xl")

    # Live Roster & Manual Override
    with ui.card().classes("w-full bg-[#0e1422] border border-slate-800 rounded-2xl p-5"):
        ui.label("Live Manual Attendance Roster").classes("text-sm font-bold text-white mb-2")
        for s in students:
            m = STATE["session_marks"].get(s["id"])
            with ui.row().classes("w-full items-center justify-between border-b border-slate-800 py-2"):
                ui.label(f"{s['name']} ({s['roll']})").classes("text-xs font-bold text-white")
                ui.label(f"{m['status']} via {m['source']} ({m['time']})" if m else "Awaiting Student QR / Face Scan").classes("text-xs font-mono text-emerald-400" if m else "text-xs text-slate-500")
                with ui.row().classes("gap-1"):
                    ui.button("Present", on_click=lambda sid=s["id"]: (mark_present(sid, subj, "Faculty Manual Roster"), refresh_fn())).props("dense").classes("bg-emerald-600 text-white text-xs px-2.5 rounded-lg")
                    ui.button("Absent", on_click=lambda sid=s["id"]: (mark_absent(sid, subj), refresh_fn())).props("dense").classes("bg-red-600 text-white text-xs px-2.5 rounded-lg")

def mark_present(student_id: str, subj: str, source: str):
    rec = STATE["attendance"].setdefault(student_id, {}).setdefault(subj, {"present": 0, "total": 0})
    rec["present"] += 1
    rec["total"] += 1
    STATE["session_marks"][student_id] = {
        "status": "Marked as Present",
        "source": source,
        "time": datetime.now().strftime("%I:%M %p"),
    }

def mark_absent(student_id: str, subj: str):
    rec = STATE["attendance"].setdefault(student_id, {}).setdefault(subj, {"present": 0, "total": 0})
    rec["total"] += 1
    STATE["session_marks"][student_id] = {
        "status": "Marked Absent",
        "source": "Faculty Manual Roster",
        "time": datetime.now().strftime("%I:%M %p"),
    }

def render_faculty_recorded(faculty_user: dict, refresh_fn):
    ui.label("RECORDED SESSIONS & STUDENT ATTENDANCE LIST").classes("text-base font-bold text-white")
    for rec in STATE["recorded_sessions"]:
        with ui.card().classes("w-full bg-[#0e1422] border border-slate-800 rounded-2xl p-4 space-y-2"):
            ui.label(f"{rec['subject']} • {rec['date']} ({rec['startTime']} to {rec['endTime']}) • {rec['presentCount']} Present / {rec['absentCount']} Absent").classes("font-bold text-cyan-300 text-xs")
            for st in rec["students"]:
                with ui.row().classes("w-full items-center justify-between border-t border-slate-800/70 pt-2"):
                    ui.label(f"{st['name']} ({st['roll']})").classes("text-xs text-white")
                    ui.badge(st["status"], color="green" if st["status"] == "Present" else "red")
                    def toggle(r=rec, row=st):
                        row["status"] = "Absent" if row["status"] == "Present" else "Present"
                        r["presentCount"] = sum(1 for x in r["students"] if x["status"] == "Present")
                        r["absentCount"] = len(r["students"]) - r["presentCount"]
                        refresh_fn()
                    ui.button("Toggle Present / Absent", on_click=toggle).props("dense flat").classes("text-xs text-indigo-400")

def render_faculty_updates(faculty_user: dict, refresh_fn):
    ui.label("ASSIGNMENTS, HOLIDAYS & CAMPUS EVENTS").classes("text-base font-bold text-white")
    with ui.card().classes("w-full max-w-lg bg-[#0e1422] border border-slate-800 rounded-2xl p-5 space-y-3"):
        cat = ui.select(["Assignment", "Holiday", "Event"], value="Assignment", label="Category").props("outlined dense dark").classes("w-full")
        subj = ui.select(["PWP", "DMGT", "COA", "DSC", "ALL"], value="PWP", label="Subject").props("outlined dense dark").classes("w-full")
        title = ui.input("Title").props("outlined dense dark").classes("w-full")
        dt = ui.input("Date", value="2026-11-26").props("outlined dense dark").classes("w-full")
        desc = ui.textarea("Description").props("outlined dense dark").classes("w-full")
        def publish():
            if not title.value.strip(): return
            STATE["campus_updates"].insert(0, {
                "id": f"UPD-{int(time.time())}", "category": cat.value, "subject": subj.value,
                "title": title.value.strip(), "date": dt.value, "details": desc.value, "postedBy": faculty_user["name"]
            })
            ui.notify("Published to Student Dashboard!", type="positive")
            refresh_fn()
        ui.button("Publish to Student Dashboard", on_click=publish).classes("w-full bg-[#5852f2] text-white font-bold rounded-xl")

def render_faculty_grades():
    ui.label("GRADE & RESULT ENTRY").classes("text-base font-bold text-white")
    for s in [u for u in STATE["users"] if u["role"] == "student"]:
        res = STATE["results"][s["id"]]
        with ui.row().classes("w-full bg-[#0e1422] border border-slate-800 rounded-xl p-3 items-center justify-between"):
            ui.label(f"{s['name']} ({s['roll']})").classes("font-bold text-white text-xs")
            ui.number("CGPA", value=res["cgpa"], step=0.01, on_change=lambda e, r=res: r.update({"cgpa": float(e.value)})).props("dense dark outlined").classes("w-28")
            ui.number("Backlogs", value=res["backlogs"], on_change=lambda e, r=res: r.update({"backlogs": int(e.value)})).props("dense dark outlined").classes("w-28")

def render_faculty_polls(refresh_fn):
    ui.label("LIVE CLASS 1-MIN QUIZ RUNNER").classes("text-base font-bold text-white")
    with ui.card().classes("w-full max-w-lg bg-[#0e1422] border border-slate-800 rounded-2xl p-5 space-y-3"):
        q = ui.input("Quiz Question", value="What is the average search time complexity of a Binary Search Tree?").props("outlined dense dark").classes("w-full")
        opts = ui.input("Options (comma-separated)", value="O(log n), O(n^2), O(1), O(n!)").props("outlined dense dark").classes("w-full")
        def launch():
            STATE["live_poll"] = {"question": q.value, "options": [x.strip() for x in opts.value.split(",") if x.strip()], "votes": {}}
            ui.notify("Live Poll Launched to Students!", type="positive")
            refresh_fn()
        ui.button("Launch Live Poll", on_click=launch).classes("bg-[#5852f2] text-white font-bold rounded-xl")

def render_faculty_plagiarism():
    ui.label("ASSIGNMENT PLAGIARISM & SIMILARITY CHECKER").classes("text-base font-bold text-white")
    with ui.card().classes("w-full bg-[#0e1422] border border-slate-800 rounded-2xl p-4"):
        ui.label("Django REST API Microservices — 38 Submissions Processed • 12% Low Risk").classes("text-xs font-bold text-emerald-400")

def render_faculty_alerts():
    ui.label("LOW ATTENDANCE MASS ALERTS").classes("text-base font-bold text-white")
    ui.button("Send Alert Reminders to All Defaulters (<75%)", on_click=lambda: ui.notify("Alerts sent to defaulters!", type="positive")).classes("bg-indigo-600 text-white font-bold rounded-xl text-xs")

# ==============================================================================
# 8. STUDENT VIEWS
# ==============================================================================
def render_student_dashboard(student: dict, navigate_fn):
    att = STATE["attendance"].get(student["id"], {})
    res = STATE["results"].get(student["id"], {})
    tot_p = sum(v["present"] for v in att.values())
    tot_s = sum(v["total"] for v in att.values())
    pct = round((tot_p / tot_s) * 100, 1) if tot_s else 100.0

    with ui.row().classes("w-full items-center justify-between"):
        ui.label(f"STUDENT DASHBOARD — {student['name'].upper()}").classes("text-base font-bold text-white")
        ui.button("Scan Live Faculty QR", icon="qr_code_scanner", on_click=lambda: navigate_fn("scan")).classes("bg-[#5852f2] text-white font-bold rounded-xl")

    with ui.row().classes("w-full gap-4"):
        with ui.card().classes("flex-1 bg-[#0e1422] border border-slate-800 rounded-2xl p-4"):
            ui.label("Overall Attendance").classes("text-xs text-slate-400")
            ui.label(f"{pct}%").classes(f"text-2xl font-extrabold {'text-red-400' if pct < 75 else 'text-emerald-400'}")
            ui.label(f"{tot_p} / {tot_s} Sessions Attended").classes("text-[10px] text-slate-500")
        with ui.card().classes("flex-1 bg-[#0e1422] border border-slate-800 rounded-2xl p-4"):
            ui.label("Current CGPA").classes("text-xs text-slate-400")
            ui.label(str(res.get("cgpa", 8.63))).classes("text-2xl font-extrabold text-cyan-400")
            ui.label(f"Active Backlogs: {res.get('backlogs', 0)}").classes("text-[10px] text-slate-500")

    if STATE["live_poll"]:
        poll = STATE["live_poll"]
        with ui.card().classes("w-full bg-indigo-950/50 border border-indigo-500 rounded-2xl p-4 space-y-2"):
            ui.label(f"LIVE CLASS QUIZ POLL: {poll['question']}").classes("font-bold text-white text-sm")
            for idx, opt in enumerate(poll["options"]):
                ui.button(opt, on_click=lambda i=idx: (poll["votes"].update({student["id"]: i}), ui.notify("Vote recorded!", type="positive"))).props("outline").classes("text-xs text-indigo-200")

    with ui.card().classes("w-full bg-[#0e1422] border border-slate-800 rounded-2xl p-4"):
        ui.label("Subject-Wise Attendance").classes("text-sm font-bold text-white mb-2")
        for subj, d in att.items():
            sp = round((d["present"] / d["total"]) * 100) if d["total"] else 100
            ui.label(f"{subj}: {d['present']} / {d['total']} Sessions ({sp}%)").classes("text-xs font-mono text-cyan-300")

def render_student_qr_scanner(student: dict):
    ui.label("SCAN FACULTY LIVE QR CODE").classes("text-base font-bold text-white")

    with ui.card().classes("w-full max-w-md bg-[#0e1422] border border-slate-800 rounded-2xl p-6 space-y-4"):
        ui.label(f"Student: {student['name']} ({student['roll']})").classes("text-xs font-bold text-indigo-300")

        def verify_qr(raw_text: str):
            if not raw_text or not raw_text.startswith("MU-CLASS-QR|"):
                ui.notify("Invalid QR Code — Unrecognized QR pattern.", type="negative")
                return
            _, token, subj, valid_until_str = raw_text.split("|")
            used = STATE["used_qr_tokens"].setdefault(student["id"], set())
            if token in used:
                ui.notify("Invalid QR Code — Already scanned by you.", type="negative")
                return
            active_token, _, _ = get_rolling_qr(STATE["manual_qr_offset"])
            if token != active_token and int(time.time() * 1000) > int(valid_until_str) + 2500:
                ui.notify("Invalid QR Code — QR pattern expired before scan.", type="negative")
                return

            used.add(token)
            mark_present(student["id"], subj, f"Optical QR ({subj})")
            ui.notify(f"Marked as Present for {subj} ({token})!", type="positive")

        def scan_webcam():
            frame = capture_webcam_frame()
            if frame is None:
                ui.notify("Webcam unavailable. Upload a QR screenshot below.", type="warning")
                return
            detector = cv2.QRCodeDetector()
            data, _, _ = detector.detectAndDecode(frame)
            verify_qr(data.strip() if data else "")

        async def handle_upload(e):
            raw = await e.file.read()
            decoded = decode_qr_from_bytes(raw)
            verify_qr(decoded or "")

        ui.button("Scan Live QR via Webcam", icon="photo_camera", on_click=scan_webcam).classes("w-full bg-emerald-600 text-white font-bold rounded-xl py-2.5")
        ui.upload(label="Or Upload Faculty QR Screenshot", auto_upload=True, on_upload=handle_upload).props("accept=image/* dark").classes("w-full")

def render_student_timetable():
    ui.label("TIMETABLE & SCHEDULE").classes("text-base font-bold text-white")
    slots = [
        ("09:00 AM - 10:00 AM", "PWP (Python Web Programming)", "Prof. Kawal Kaur", "Lab ICT 301"),
        ("10:00 AM - 11:00 AM", "DMGT (Discrete Math & Graph Theory)", "Prof. Biswajit", "Hall ICT 204"),
        ("11:15 AM - 12:15 PM", "COA (Computer Organization & Arch)", "Prof. Vijay Dubey", "Hall ICT 204"),
        ("01:00 PM - 02:00 PM", "DSC (Data Structures in C)", "Prof. Alam", "Lab ICT 302"),
    ]
    for t, s, f, r in slots:
        with ui.card().classes("w-full bg-[#0e1422] border border-slate-800 rounded-xl p-3"):
            ui.label(f"{t} • {s}").classes("text-xs font-bold text-white")
            ui.label(f"{f} — {r}").classes("text-[11px] font-mono text-cyan-300")

def render_student_assignments(refresh_fn):
    ui.label("ASSIGNMENTS HUB").classes("text-base font-bold text-white")
    for a in [u for u in STATE["campus_updates"] if u["category"] == "Assignment"]:
        with ui.card().classes("w-full bg-[#0e1422] border border-slate-800 rounded-xl p-4"):
            ui.label(f"[{a['subject']}] {a['title']} (Due: {a['date']})").classes("font-bold text-white text-xs")
            ui.label(a["details"]).classes("text-xs text-slate-400")
            ui.button("Submit Work", on_click=lambda: ui.notify("Assignment Submitted!", type="positive")).props("dense").classes("bg-indigo-600 text-white text-xs px-3 rounded-lg mt-2")

def render_student_results(student: dict):
    res = STATE["results"].get(student["id"], {})
    ui.label("RESULTS & TRANSCRIPT (SEM 3)").classes("text-base font-bold text-white")
    with ui.card().classes("w-full bg-[#0e1422] border border-slate-800 rounded-2xl p-5 space-y-2"):
        ui.label(f"CGPA: {res.get('cgpa')} • Active Backlogs: {res.get('backlogs')}").classes("text-lg font-extrabold text-cyan-400")
        for sem, val in res.get("sgpa", {}).items():
            ui.label(f"{sem} SGPA: {val}").classes("text-xs font-mono text-slate-300")
        for sub, grd in res.get("subjects", {}).items():
            ui.label(f"{sub}: Grade {grd}").classes("text-xs font-mono text-emerald-400")

def render_student_curriculum():
    ui.label("CURRICULUM PROGRESS").classes("text-base font-bold text-white")
    courses = [
        ("PWP — Python Web Programming", 82),
        ("DMGT — Discrete Math & Graph Theory", 75),
        ("COA — Computer Organization & Architecture", 90),
        ("DSC — Data Structures in C", 80),
    ]
    for name, pct in courses:
        with ui.card().classes("w-full bg-[#0e1422] border border-slate-800 rounded-xl p-4"):
            ui.label(f"{name} ({pct}%)").classes("text-xs font-bold text-white")
            ui.linear_progress(value=pct / 100.0).classes("mt-1")

def render_student_holidays():
    ui.label("HOLIDAYS & CAMPUS EVENTS").classes("text-base font-bold text-white")
    for item in [u for u in STATE["campus_updates"] if u["category"] in ("Holiday", "Event")]:
        with ui.card().classes("w-full bg-[#0e1422] border border-slate-800 rounded-xl p-4"):
            ui.label(f"[{item['category'].upper()}] {item['title']} — {item['date']}").classes("font-bold text-amber-300 text-xs")
            ui.label(item["details"]).classes("text-xs text-slate-400")

ui.run(title="Marwadi University ICT - Smart Attendance & Activity System", port=8080, storage_secret="mu_ict_2026")