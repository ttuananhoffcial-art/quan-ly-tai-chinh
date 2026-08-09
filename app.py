from datetime import datetime, timedelta
import hashlib
import random
import sqlite3
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. CẤU HÌNH TRANG
# ==========================================
st.set_page_config(
    page_title="Quản Lý Tài Chính Cá Nhân",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# 2. CẤU HÌNH CSS: ẨN SẠCH GIAO DIỆN HỆ THỐNG & NÚT BÍ MẬT
# ==========================================
st.markdown(
    """
    <style>
    /* Ẩn hoàn toàn Header, Footer, Vương miện, Avatar và Sidebar */
    footer, header,
    [data-testid="stFooter"], [data-testid="stEmbedFooter"],
    [data-testid="stHeader"], [data-testid="stToolbar"],
    [data-testid="stStatusWidget"], [data-testid="stUserAvatar"],
    .stEmbedFooter, .stAppDeployButton,
    div[class*="embedFooter"], div[class*="stEmbedFooter"],
    div[class*="viewerBadge"], div[class*="stAppHeader"], #MainMenu {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0px !important;
        min-height: 0px !important;
        max-height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
        overflow: hidden !important;
        pointer-events: none !important;
    }

    /* Giấu tuyệt đối nút SECRET_TRIPLE_CLICK */
    .my-secret-wrapper,
    div[data-testid="stElementContainer"]:has(.my-secret-wrapper),
    div[data-testid="stButton"]:has(.my-secret-wrapper) {
        position: absolute !important;
        left: -9999px !important;
        top: -9999px !important;
        width: 0px !important;
        height: 0px !important;
        opacity: 0 !important;
        overflow: hidden !important;
        pointer-events: none !important;
    }

    /* Khóa Sidebar */
    [data-testid="stSidebar"], 
    [data-testid="stSidebarCollapseButton"], 
    [data-testid="collapsedControl"],
    button[aria-label="Toggle sidebar"],
    button[data-testid="stHeaderIconButton"] {
        display: none !important;
        width: 0px !important;
    }

    /* Tối ưu tràn màn hình trên di động */
    .block-container {
        max-width: 100% !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        padding-top: 0.2rem !important;
        padding-bottom: 0rem !important;
    }

    .stAppViewMain { padding-bottom: 0px !important; }

    /* Khung tổng quan cố định đỉnh màn hình */
    div[data-testid="stElementContainer"]:has(.sticky-header) {
        position: sticky !important;
        top: 0px !important;
        z-index: 9999 !important;
        background-color: #ffffff !important;
        padding-top: 6px !important;
        padding-bottom: 8px !important;
        margin-top: -10px !important;
        margin-bottom: 12px !important;
        border-bottom: 2px solid #cbd5e1 !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.06) !important;
    }

    .main-app-title {
        font-size: clamp(18px, 4vw, 28px) !important;
        font-weight: 900 !important;
        color: #0f172a !important;
        text-align: center !important;
        margin-bottom: 6px !important;
    }

    /* Bắt buộc 4 ô nằm trên 1 hàng ngang */
    .summary-container {
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 6px !important;
        width: 100% !important;
    }

    .card-box {
        border-radius: 10px !important;
        padding: 8px 4px !important;
        text-align: center !important;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.04) !important;
        cursor: pointer !important;
        user-select: none !important;
        min-width: 0 !important;
    }

    .card-income { background-color: #f0fdf4 !important; border: 2px solid #22c55e !important; }
    .card-expense { background-color: #fef2f2 !important; border: 2px solid #ef4444 !important; }
    .card-debt { background-color: #fff7ed !important; border: 2px solid #f97316 !important; }
    .card-balance { background-color: #eff6ff !important; border: 2px solid #3b82f6 !important; }
    
    .card-title {
        font-size: clamp(9px, 2.2vw, 13px) !important;
        font-weight: 900 !important;
        margin: 0 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    .card-amount {
        font-size: clamp(11px, 3.2vw, 22px) !important;
        font-weight: 900 !important;
        margin: 2px 0 0 0 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    /* Menu chọn chức năng dạng thẻ ngang */
    div[data-testid="stRadio"] > div {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
        justify-content: center !important;
        background-color: #f8fafc !important;
        padding: 8px !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
    }

    div[data-testid="stRadio"] label {
        background-color: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        margin: 0 !important;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.03) !important;
        cursor: pointer !important;
    }

    div[data-testid="stRadio"] label:hover {
        border-color: #2563eb !important;
        background-color: #eff6ff !important;
    }

    div[data-testid="stRadio"] label p {
        font-size: 15px !important;
        font-weight: 800 !important;
        color: #0f172a !important;
    }

    label, p, span, div { font-weight: 800 !important; color: #000000 !important; }
    input, textarea, select { font-size: 16px !important; font-weight: bold !important; }
    .stButton>button {
        width: 100%; font-size: 16px !important; font-weight: bold !important;
        background-color: #2563eb !important; color: white !important; border-radius: 8px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 3. HÀM BỔ TRỢ HỆ THỐNG
# ==========================================
def generate_session_token(user_id):
    return hashlib.sha256(
        f"{user_id}_{datetime.now().timestamp()}_{random.randint(1000, 9999)}".encode()
    ).hexdigest()


def hash_password(password):
    return hashlib.sha256(password.strip().encode()).hexdigest()


def doc_so_vn(so):
    if not so or so <= 0:
        return ""
    so = int(so)
    chieu = [
        "không",
        "một",
        "hai",
        "ba",
        "bốn",
        "năm",
        "sáu",
        "bảy",
        "tám",
        "chín",
    ]

    def read_three_digits(n, has_prefix=True):
        tram = n // 100
        chuc = (n % 100) // 10
        donvi = n % 10
        res = []
        if tram > 0 or has_prefix:
            res.append(f"{chieu[tram]} trăm")
        if chuc == 0 and donvi > 0:
            if tram > 0 or has_prefix:
                res.append("lẻ")
            res.append(chieu[donvi])
        elif chuc == 1:
            res.append("mười")
            if donvi == 1:
                res.append("một")
            elif donvi == 5:
                res.append("lăm")
            elif donvi > 0:
                res.append(chieu[donvi])
        elif chuc > 1:
            res.append(f"{chieu[chuc]} mươi")
            if donvi == 1:
                res.append("mốt")
            elif donvi == 5:
                res.append("lăm")
            elif donvi > 0:
                res.append(chieu[donvi])
        return " ".join(res)

    s = str(so)
    while len(s) % 3 != 0:
        s = "0" + s
    groups = [int(s[i : i + 3]) for i in range(0, len(s), 3)]
    units = ["", "nghìn", "triệu", "tỷ", "nghìn tỷ"]
    n_groups = len(groups)
    parts = []

    for i, val in enumerate(groups):
        if val == 0:
            continue
        unit_idx = n_groups - 1 - i
        group_text = read_three_digits(val, i > 0)
        if unit_idx < len(units) and units[unit_idx]:
            group_text += " " + units[unit_idx]
        parts.append(group_text)

    full_text = " ".join(parts).strip()
    return full_text[0].upper() + full_text[1:] + " đồng" if full_text else ""


# ==========================================
# 4. KHỞI TẠO CƠ SỞ DỮ LIỆU SQLITE
# ==========================================
conn = sqlite3.connect("finance.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute(
    """CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT UNIQUE, username TEXT UNIQUE, password TEXT, session_token TEXT)"""
)
cursor.execute(
    """CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, type TEXT, category TEXT, amount REAL, note TEXT, date TEXT)"""
)
cursor.execute(
    """CREATE TABLE IF NOT EXISTS debts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, person_name TEXT, debt_type TEXT, amount REAL, status TEXT, date TEXT)"""
)
conn.commit()


# ==========================================
# 5. TỰ ĐỘNG KHÔI PHÚC ĐĂNG NHẬP (TỐC ĐỘ CAO)
# ==========================================
if "user" not in st.session_state:
    st.session_state["user"] = None

# Kiểm tra URL parameter
session_param = st.query_params.get("session")

if session_param and st.session_state["user"] is None:
    cursor.execute(
        "SELECT id, phone, username FROM users WHERE session_token = ?",
        (session_param,),
    )
    session_user = cursor.fetchone()
    if session_user:
        st.session_state["user"] = {
            "id": session_user[0],
            "phone": session_user[1],
            "username": session_user[2],
            "session_token": session_param,
        }

current_token_js = (
    st.session_state["user"]["session_token"]
    if st.session_state["user"]
    else ""
)

# JavaScript đồng bộ LocalStorage cho iPhone
components.html(
    f"""
<script>
(function() {{
    try {{
        var topWin = window.top || window.parent || window;
        var activeToken = "{current_token_js}";
        
        if (activeToken) {{
            // Lưu token vào máy khi đã đăng nhập
            topWin.localStorage.setItem('app_fin_session', activeToken);
        }} else {{
            // Tự động khôi phục đăng nhập nếu mở app từ Màn hình chính iPhone
            var storedToken = topWin.localStorage.getItem('app_fin_session');
            var urlParams = new URLSearchParams(topWin.location.search);
            var urlToken = urlParams.get('session');
            
            if (storedToken && storedToken !== urlToken) {{
                urlParams.set('session', storedToken);
                topWin.location.search = urlParams.toString();
            }}
        }}
    }} catch(e) {{}}
}})();

function forceHideElements() {{
    var targets = [document];
    try {{ if (window.parent && window.parent.document) targets.push(window.parent.document); }} catch(e){{}}
    try {{ if (window.top && window.top.document) targets.push(window.top.document); }} catch(e){{}}

    targets.forEach(function(doc) {{
        if (!doc) return;
        if (!doc.querySelector('#st-hide-style')) {{
            var style = doc.createElement('style');
            style.id = 'st-hide-style';
            style.innerHTML = `
                footer, header, [data-testid="stFooter"], [data-testid="stEmbedFooter"],
                [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stStatusWidget"],
                .stEmbedFooter, div[class*="embedFooter"], .my-secret-wrapper {{
                    display: none !important; visibility: hidden !important; opacity: 0 !important; height: 0px !important;
                }}
            `;
            try {{ doc.head.appendChild(style); }} catch(e){{}}
        }}

        var btns = doc.querySelectorAll('button');
        btns.forEach(function(b) {{
            if (b.innerText && b.innerText.includes('SECRET_TRIPLE_CLICK')) {{
                b.style.position = 'absolute';
                b.style.left = '-9999px';
                b.style.top = '-9999px';
                b.style.opacity = '0';
                b.style.height = '0px';
                b.style.width = '0px';
                b.style.overflow = 'hidden';
                var parent = b.closest('[data-testid="stElementContainer"]') || b.closest('[data-testid="stButton"]');
                if (parent) {{
                    parent.style.position = 'absolute';
                    parent.style.left = '-9999px';
                    parent.style.top = '-9999px';
                    parent.style.height = '0px';
                    parent.style.overflow = 'hidden';
                    parent.style.opacity = '0';
                }}
            }}
        }});
    }});
}}

function setupAppScripts() {{
    forceHideElements();
    var pDoc = window.parent.document;

    // Triple click kích hoạt Bảng Điều Chỉnh
    var cards = pDoc.querySelectorAll('.card-box');
    cards.forEach(function(card) {{
        if (card.dataset.tripleSetup) return;
        card.dataset.tripleSetup = "true";
        var clickCount = 0, clickTimer;
        card.addEventListener('click', function() {{
            clickCount++;
            if (clickCount === 1) {{
                clickTimer = setTimeout(function() {{ clickCount = 0; }}, 400);
            }} else if (clickCount === 3) {{
                clearTimeout(clickTimer);
                clickCount = 0;
                var btns = pDoc.querySelectorAll('button');
                for (var i = 0; i < btns.length; i++) {{
                    if (btns[i].innerText && btns[i].innerText.includes('SECRET_TRIPLE_CLICK')) {{
                        btns[i].click(); break;
                    }}
                }}
            }}
        }});
    }});

    // Xem trước số tiền + chữ thời gian thực
    var inputs = pDoc.querySelectorAll('input[type="text"]');
    inputs.forEach(function(input) {{
        if (input.placeholder && input.placeholder.includes("Gõ số tiền")) {{
            if (input.dataset.liveSetup) return;
            input.dataset.liveSetup = "true";
            var container = input.closest('[data-testid="stElementContainer"]');
            if (!container) return;

            var previewBox = pDoc.createElement('div');
            previewBox.style.cssText = 'margin-top: 5px; margin-bottom: 12px; padding: 10px; background-color: #eff6ff; border: 2px solid #3b82f6; border-radius: 8px; font-weight: bold; color: #1e3a8a; font-size: 16px; display: none;';
            container.insertAdjacentElement('afterend', previewBox);

            input.addEventListener('input', function(e) {{
                var val = e.target.value.replace(/\D/g, '');
                if (!val || parseInt(val) === 0) {{
                    previewBox.style.display = 'none'; return;
                }}
                var num = parseInt(val);
                previewBox.style.display = 'block';
                previewBox.innerHTML = '💵 <b>Số tiền:</b> ' + num.toLocaleString('vi-VN') + ' VNĐ<br>🔤 <b>Bằng chữ:</b> <i>' + docSoVNJS(num) + '</i>';
            }});
        }}
    }});
}}

function docSoVNJS(so) {{
    if (!so || so <= 0) return "";
    var chieu = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"];
    function readThreeDigits(n, hasPrefix) {{
        var tram = Math.floor(n / 100), chuc = Math.floor((n % 100) / 10), donvi = n % 10, res = [];
        if (tram > 0 || hasPrefix) res.push(chieu[tram] + " trăm");
        if (chuc === 0 && donvi > 0) {{
            if (tram > 0 || hasPrefix) res.push("lẻ");
            res.push(chieu[donvi]);
        }} else if (chuc === 1) {{
            res.push("mười");
            if (donvi === 1) res.push("một"); else if (donvi === 5) res.push("lăm"); else if (donvi > 0) res.push(chieu[donvi]);
        }} else if (chuc > 1) {{
            res.push(chieu[chuc] + " mươi");
            if (donvi === 1) res.push("mốt"); else if (donvi === 5) res.push("lăm"); else if (donvi > 0) res.push(chieu[donvi]);
        }}
        return res.join(" ");
    }}
    var s = so.toString();
    while (s.length % 3 !== 0) s = "0" + s;
    var groups = [];
    for (var i = 0; i < s.length; i += 3) groups.push(parseInt(s.substring(i, i + 3)));
    var units = ["", "nghìn", "triệu", "tỷ", "nghìn tỷ"], n_groups = groups.length, parts = [];
    for (var i = 0; i < n_groups; i++) {{
        var val = groups[i]; if (val === 0) continue;
        var unit_idx = n_groups - 1 - i, group_text = readThreeDigits(val, i > 0);
        if (unit_idx < units.length && units[unit_idx]) group_text += " " + units[unit_idx];
        parts.push(group_text);
    }}
    var full = parts.join(" ").trim();
    return full ? full.charAt(0).toUpperCase() + full.slice(1) + " đồng" : "";
}}

setInterval(setupAppScripts, 100);
</script>
""",
    height=0,
)

if "auth_show_form" not in st.session_state:
    st.session_state["auth_show_form"] = False
if "auth_mode" not in st.session_state:
    st.session_state["auth_mode"] = "login"

# Nút kích hoạt bí mật
st.markdown('<div class="my-secret-wrapper">', unsafe_allow_html=True)
if st.button("SECRET_TRIPLE_CLICK", key="secret_triple_btn"):
    st.session_state["show_adjust_panel"] = not st.session_state.get(
        "show_adjust_panel", False
    )
    st.rerun()
st.markdown("</div>", unsafe_allow_html=True)


# --- KHI CHƯA ĐĂNG NHẬP ---
if st.session_state["user"] is None:
    st.title("💰 Quản Lý Tài Chính Cá Nhân")

    col_top_auth1, col_top_auth2, _ = st.columns([1, 1, 2])
    with col_top_auth1:
        if st.button("🔐 Đăng Nhập", key="btn_main_login"):
            st.session_state["auth_show_form"] = True
            st.session_state["auth_mode"] = "login"
    with col_top_auth2:
        if st.button("📝 Đăng Ký", key="btn_main_reg"):
            st.session_state["auth_show_form"] = True
            st.session_state["auth_mode"] = "register"

    if st.session_state["auth_show_form"]:
        st.markdown("---")
        if st.session_state["auth_mode"] == "login":
            st.subheader("🔑 Đăng Nhập Tài Khoản")
            login_account = st.text_input(
                "Tên tài khoản hoặc SĐT", key="login_acc"
            )
            login_pass = st.text_input(
                "Mật khẩu", type="password", key="login_pwd"
            )

            col_l1, col_l2, col_l3 = st.columns([2, 1, 1])
            with col_l1:
                if st.button("ĐĂNG NHẬP NGAY", key="btn_login_submit"):
                    acc_clean = login_account.strip()
                    hashed_pwd = hash_password(login_pass)

                    cursor.execute(
                        "SELECT id, phone, username FROM users WHERE (LOWER(username) = LOWER(?) OR phone = ?) AND password = ?",
                        (acc_clean, acc_clean, hashed_pwd),
                    )
                    user_found = cursor.fetchone()

                    if user_found:
                        u_id, u_phone, u_name = user_found
                        sess_token = generate_session_token(u_id)
                        cursor.execute(
                            "UPDATE users SET session_token = ? WHERE id = ?",
                            (sess_token, u_id),
                        )
                        conn.commit()

                        st.query_params["session"] = sess_token
                        st.session_state["user"] = {
                            "id": u_id,
                            "phone": u_phone,
                            "username": u_name,
                            "session_token": sess_token,
                        }
                        st.session_state["auth_show_form"] = False
                        st.rerun()
                    else:
                        st.error("⚠️ Sai Tên tài khoản / SĐT hoặc Mật khẩu!")
            with col_l2:
                if st.button("🔑 Quên MK?", key="btn_to_forgot"):
                    st.session_state["auth_mode"] = "forgot"
                    st.rerun()
            with col_l3:
                if st.button("✖️ Đóng Form", key="btn_close_login"):
                    st.session_state["auth_show_form"] = False
                    st.rerun()

        elif st.session_state["auth_mode"] == "register":
            st.subheader("📝 Đăng Ký Tài Khoản Mới")
            reg_phone = st.text_input(
                "Số điện thoại", placeholder="vd: 0912345678", key="reg_phone"
            )
            reg_user = st.text_input(
                "Tên tài khoản", placeholder="vd: chuong123", key="reg_user"
            )
            reg_pass = st.text_input("Mật khẩu", type="password", key="reg_pass")
            reg_pass_confirm = st.text_input(
                "Nhập lại mật khẩu", type="password", key="reg_pass_confirm"
            )

            col_r1, col_r2 = st.columns([2, 1])
            with col_r1:
                if st.button("TẠO TÀI KHOẢN MỚI", key="btn_reg_submit"):
                    phone_clean = reg_phone.strip()
                    user_clean = reg_user.strip()

                    if not phone_clean or not user_clean or not reg_pass:
                        st.error("⚠️ Vui lòng điền đầy đủ tất cả thông tin!")
                    elif reg_pass != reg_pass_confirm:
                        st.error("⚠️ Mật khẩu xác nhận không trùng khớp!")
                    else:
                        cursor.execute(
                            "SELECT id FROM users WHERE phone = ? OR LOWER(username) = LOWER(?)",
                            (phone_clean, user_clean),
                        )
                        if cursor.fetchone():
                            st.error(
                                "⚠️ Số điện thoại hoặc Tên tài khoản đã tồn tại!"
                            )
                        else:
                            hashed_pwd = hash_password(reg_pass)
                            cursor.execute(
                                "INSERT INTO users (phone, username, password) VALUES (?, ?, ?)",
                                (phone_clean, user_clean, hashed_pwd),
                            )
                            conn.commit()

                            new_user_id = cursor.lastrowid
                            sess_token = generate_session_token(new_user_id)
                            cursor.execute(
                                "UPDATE users SET session_token = ? WHERE id = ?",
                                (sess_token, new_user_id),
                            )
                            conn.commit()

                            st.query_params["session"] = sess_token
                            st.session_state["user"] = {
                                "id": new_user_id,
                                "phone": phone_clean,
                                "username": user_clean,
                                "session_token": sess_token,
                            }
                            st.session_state["auth_show_form"] = False
                            st.session_state["adjust_msg"] = (
                                f"🎉 Đăng ký thành công! Chào mừng {user_clean}."
                            )
                            st.rerun()
            with col_r2:
                if st.button("✖️ Đóng Form", key="btn_close_reg"):
                    st.session_state["auth_show_form"] = False
                    st.rerun()

        elif st.session_state["auth_mode"] == "forgot":
            st.subheader("🔑 Quên Mật Khẩu")
            forgot_phone = st.text_input(
                "Nhập Số Điện Thoại",
                placeholder="vd: 0912345678",
                key="forgot_phone",
            )
            new_pass = st.text_input(
                "Mật khẩu mới", type="password", key="forgot_new_pass"
            )
            new_pass_confirm = st.text_input(
                "Nhập lại mật khẩu mới",
                type="password",
                key="forgot_new_pass_confirm",
            )

            col_f1, col_f2 = st.columns([2, 1])
            with col_f1:
                if st.button("✅ ĐỔI MẬT KHẨU", key="btn_submit_forgot"):
                    phone_clean = forgot_phone.strip()
                    cursor.execute(
                        "SELECT id FROM users WHERE phone = ?", (phone_clean,)
                    )
                    user_found = cursor.fetchone()

                    if not user_found:
                        st.error(
                            "⚠️ Số điện thoại này chưa đăng ký tài khoản nào!"
                        )
                    elif not new_pass or new_pass != new_pass_confirm:
                        st.error("⚠️ Mật khẩu mới chưa khớp hoặc để trống!")
                    else:
                        hashed_pwd = hash_password(new_pass)
                        cursor.execute(
                            "UPDATE users SET password = ? WHERE phone = ?",
                            (hashed_pwd, phone_clean),
                        )
                        conn.commit()

                        st.session_state["auth_mode"] = "login"
                        st.session_state["adjust_msg"] = (
                            "✅ Đổi mật khẩu thành công! Hãy đăng nhập bằng mật khẩu mới."
                        )
                        st.rerun()
            with col_f2:
                if st.button("✖️ Đóng Form", key="btn_close_forgot"):
                    st.session_state["auth_show_form"] = False
                    st.rerun()

    st.info(
        "👋 **Chào mừng bạn!** Hãy ấn nút **🔐 Đăng Nhập** ở trên để bắt đầu sử dụng."
    )
    st.stop()


# --- ĐÃ ĐĂNG NHẬP THÀNH CÔNG ---
current_user = st.session_state["user"]
user_id = current_user["id"]

col_user_info, col_logout = st.columns([4, 1])
with col_user_info:
    st.markdown(
        f"👤 **Tài khoản:** `{current_user['username']}` | 📞 **SĐT:** `{current_user['phone']}`"
    )
with col_logout:
    if st.button("🚪 Đăng Xuất", key="btn_logout_top"):
        if current_user:
            cursor.execute(
                "UPDATE users SET session_token = NULL WHERE id = ?",
                (current_user["id"],),
            )
            conn.commit()
        st.query_params.clear()
        st.session_state["user"] = None
        components.html(
            """
            <script>
            try {
                var topWin = window.top || window.parent || window;
                topWin.localStorage.removeItem('app_fin_session');
            } catch(e){}
            </script>
            """,
            height=0,
        )
        st.rerun()

cursor.execute(
    "SELECT DISTINCT person_name FROM debts WHERE user_id = ? AND person_name IS NOT NULL AND person_name != '' ORDER BY person_name ASC",
    (user_id,),
)
existing_persons = [row[0] for row in cursor.fetchall()]


# ==========================================
# 6. TÍNH DÒNG TIỀN VÀ SỐ DƯ TÀI KHOẢN
# ==========================================
def get_financial_summary():
    cursor.execute(
        "SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type IN ('Thu nhập', 'Thu nợ')",
        (user_id,),
    )
    total_income = cursor.fetchone()[0] or 0.0

    cursor.execute(
        "SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type IN ('Chi tiêu', 'Trả nợ')",
        (user_id,),
    )
    total_expense = cursor.fetchone()[0] or 0.0

    cursor.execute(
        "SELECT SUM(amount) FROM debts WHERE user_id = ? AND debt_type = 'Cho vay (Người khác nợ mình)' AND status = 'Đang nợ'",
        (user_id,),
    )
    total_lent_unpaid = cursor.fetchone()[0] or 0.0

    balance = total_income - total_expense
    return total_income, total_expense, total_lent_unpaid, balance


# ==========================================
# 7. HIỂN THỊ 4 Ô THỐNG KÊ CỐ ĐỊNH TRÊN CÙNG
# ==========================================
total_income, total_expense, total_lent_unpaid, balance = get_financial_summary()

summary_html = f"""
<div class="sticky-header">
    <div class="main-app-title">💰 Quản Lý Tài Chính Cá Nhân</div>
    <div class="summary-container">
        <div class="card-box card-income">
            <p class="card-title" style="color: #15803d;">💵 THU NHẬP</p>
            <p class="card-amount" style="color: #166534;">{total_income:,.0f} đ</p>
        </div>
        <div class="card-box card-expense">
            <p class="card-title" style="color: #b91c1c;">💸 CHI TIÊU</p>
            <p class="card-amount" style="color: #991b1b;">{total_expense:,.0f} đ</p>
        </div>
        <div class="card-box card-debt">
            <p class="card-title" style="color: #c2410c;">🤝 NỢ MÌNH</p>
            <p class="card-amount" style="color: #9a3412;">{total_lent_unpaid:,.0f} đ</p>
        </div>
        <div class="card-box card-balance">
            <p class="card-title" style="color: #1d4ed8;">💳 TỔNG SỐ DƯ</p>
            <p class="card-amount" style="color: #1e40af;">{balance:,.0f} đ</p>
        </div>
    </div>
</div>
"""
st.markdown(summary_html, unsafe_allow_html=True)

if "adjust_msg" in st.session_state:
    st.success(st.session_state["adjust_msg"])
    del st.session_state["adjust_msg"]


# ==========================================
# BẢNG ĐIỀU CHỈNH BÍ MẬT (TRIPLE CLICK VÀO 4 Ô)
# ==========================================
if st.session_state.get("show_adjust_panel", False):
    st.markdown("---")
    col_title_adj, col_close_adj = st.columns([5, 1])
    with col_title_adj:
        st.subheader(
            "⚙️ Bảng Điều Chỉnh Số Tiền Chính Xác & Reset Dữ Liệu"
        )
    with col_close_adj:
        if st.button("❌ Đóng Bảng"):
            st.session_state["show_adjust_panel"] = False
            st.rerun()

    tab_adj1, tab_adj2, tab_adj3 = st.tabs(
        [
            "✏️ Thiết Lập Số Dư / Tổng Thu",
            "🗑️ Xóa Lịch Sử Chi Tiêu / Nợ",
            "🔄 Reset Phần Mềm Về 0",
        ]
    )

    with tab_adj1:
        st.write("💡 **Cài đặt Tổng Số Dư Còn Lại chính xác theo thực tế:**")
        raw_new_bal = st.text_input(
            "Nhập Tổng Số Dư Chính Xác Bạn Đang Có (VNĐ)",
            placeholder="Gõ số tiền... (vd: 50000000)",
            key="input_new_bal",
        )
        clean_new_bal = (
            "".join(c for c in raw_new_bal if c.isdigit())
            if raw_new_bal
            else ""
        )
        target_bal = int(clean_new_bal) if clean_new_bal else None

        if target_bal is not None:
            st.info(
                f"💵 **Số tiền thiết lập:** `{target_bal:,.0f} VNĐ` (*{doc_so_vn(target_bal)}*)"
            )

        if st.button("LƯU ĐIỀU CHỈNH SỐ DƯ"):
            if target_bal is None:
                st.error("⚠️ Vui lòng gõ số tiền hợp lệ!")
            else:
                diff = target_bal - balance
                today_str = datetime.now().strftime("%Y-%m-%d")
                if diff > 0:
                    cursor.execute(
                        "INSERT INTO transactions (user_id, type, category, amount, note, date) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            user_id,
                            "Thu nhập",
                            "Cài đặt số dư ban đầu",
                            float(diff),
                            "Điều chỉnh số dư trực tiếp",
                            today_str,
                        ),
                    )
                elif diff < 0:
                    cursor.execute(
                        "INSERT INTO transactions (user_id, type, category, amount, note, date) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            user_id,
                            "Chi tiêu",
                            "Cài đặt số dư ban đầu",
                            float(abs(diff)),
                            "Điều chỉnh số dư trực tiếp",
                            today_str,
                        ),
                    )
                conn.commit()
                st.session_state["show_adjust_panel"] = False
                st.session_state["adjust_msg"] = (
                    f"✅ Đã điều chỉnh Tổng số dư còn lại về đúng: {target_bal:,.0f} đ!"
                )
                st.rerun()

    with tab_adj2:
        st.write("⚠️ **Chọn mục bạn muốn xóa dữ liệu:**")
        col_reset_exp, col_reset_debt = st.columns(2)
        with col_reset_exp:
            if st.button("🗑️ XÓA TOÀN BỘ LỊCH SỬ CHI TIÊU"):
                cursor.execute(
                    "DELETE FROM transactions WHERE user_id = ?", (user_id,)
                )
                conn.commit()
                st.session_state["show_adjust_panel"] = False
                st.session_state["adjust_msg"] = (
                    "✅ Đã xóa sạch toàn bộ lịch sử Giao dịch!"
                )
                st.rerun()

        with col_reset_debt:
            if st.button("🗑️ XÓA TOÀN BỘ KHOẢN NỢ"):
                cursor.execute("DELETE FROM debts WHERE user_id = ?", (user_id,))
                conn.commit()
                st.session_state["show_adjust_panel"] = False
                st.session_state["adjust_msg"] = (
                    "✅ Đã xóa sạch toàn bộ danh sách Nợ!"
                )
                st.rerun()

    with tab_adj3:
        st.write("💥 **Cảnh báo:** Thao tác này sẽ xóa sạch tất cả thu, chi, nợ nần về 0 đ.")
        if st.button("🔥 RESET TOÀN BỘ PHẦN MỀM VỀ 0"):
            cursor.execute(
                "DELETE FROM transactions WHERE user_id = ?", (user_id,)
            )
            cursor.execute("DELETE FROM debts WHERE user_id = ?", (user_id,))
            conn.commit()
            st.session_state["show_adjust_panel"] = False
            st.session_state["adjust_msg"] = (
                "🔄 Phần mềm đã được reset hoàn toàn về 0 đ!"
            )
            st.rerun()


# ==========================================
# 8. MENU ĐIỀU HƯỚNG CHÍNH
# ==========================================
menu = st.radio(
    "📌 CHỌN CHỨC NĂNG",
    [
        "🏠 Tổng Quan",
        "➕ Thêm Giao Dịch",
        "🤝 Quản Lý Nợ",
        "🍕 Chia Bill",
        "📊 Báo Cáo Chi Tiết",
    ],
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("---")


# ==========================================
# 9. XỬ LÝ NỘI DUNG TỪNG TAB CHỨC NĂNG
# ==========================================

if menu == "🏠 Tổng Quan":
    st.subheader("📋 Giao Dịch Gần Đây")
    df_recent = pd.read_sql_query(
        f"SELECT date AS 'Ngày', type AS 'Loại', category AS 'Danh Mục', amount AS 'Số Tiền', note AS 'Ghi Chú' FROM transactions WHERE user_id = {user_id} ORDER BY date DESC, id DESC LIMIT 10",
        conn,
    )
    if not df_recent.empty:
        st.dataframe(df_recent, use_container_width=True)
    else:
        st.info("Chưa có giao dịch nào. Chọn '➕ Thêm Giao Dịch' để nhập nhé!")

elif menu == "➕ Thêm Giao Dịch":
    st.subheader("➕ Nhập Giao Dịch / Khoản Nợ Mới")

    if st.session_state.get("clear_trans_form"):
        st.session_state["trans_category"] = ""
        st.session_state["trans_amount"] = ""
        st.session_state["trans_note"] = ""
        if "trans_person_new" in st.session_state:
            st.session_state["trans_person_new"] = ""
        st.session_state["clear_trans_form"] = False

    if "trans_success" in st.session_state:
        st.success(st.session_state["trans_success"])
        del st.session_state["trans_success"]

    trans_date = st.date_input(
        "🗓️ Ngày thực hiện", datetime.now(), key="trans_date"
    )
    t_type = st.selectbox(
        "Loại giao dịch",
        [
            "Chi tiêu",
            "Thu nhập",
            "Cho vay (Người khác nợ mình)",
            "Đi vay (Mình nợ người khác)",
        ],
        key="trans_type",
    )

    person = ""
    is_debt_transaction = t_type in [
        "Cho vay (Người khác nợ mình)",
        "Đi vay (Mình nợ người khác)",
    ]

    if is_debt_transaction:
        if existing_persons:
            person_options = [
                "-- Chọn người từ danh bạ --",
                "➕ Nhập tên người mới...",
            ] + existing_persons
            selected_p = st.selectbox(
                "👤 Tên đối phương", person_options, key="trans_person_select"
            )

            if selected_p == "➕ Nhập tên người mới...":
                person = st.text_input(
                    "Gõ tên người mới",
                    placeholder="Nhập tên người mới...",
                    key="trans_person_new",
                )
            elif selected_p != "-- Chọn người từ danh bạ --":
                person = selected_p
        else:
            person = st.text_input(
                "👤 Tên đối phương",
                placeholder="Nhập tên đối phương...",
                key="trans_person_new",
            )
        category = "Cho vay" if "Cho vay" in t_type else "Đi vay"
    else:
        category = st.text_input(
            "Danh mục (vd: Cafe, Ăn uống, Lương...)", key="trans_category"
        )

    raw_amount = st.text_input(
        "Số tiền (VNĐ)", placeholder="Gõ số tiền...", key="trans_amount"
    )
    clean_amount_str = (
        "".join(c for c in raw_amount if c.isdigit()) if raw_amount else ""
    )
    amount = int(clean_amount_str) if clean_amount_str else 0
    note = st.text_area("Ghi chú", key="trans_note")

    if st.button("LƯU GIAO DỊCH"):
        if amount <= 0:
            st.error("⚠️ Vui lòng nhập số tiền hợp lệ (lớn hơn 0)!")
        elif is_debt_transaction and not person.strip():
            st.error("⚠️ Vui lòng chọn hoặc nhập tên đối phương!")
        else:
            date_str = trans_date.strftime("%Y-%m-%d")

            if t_type == "Cho vay (Người khác nợ mình)":
                note_final = (
                    f"Cho {person.strip()} vay"
                    + (f": {note.strip()}" if note.strip() else "")
                )
                cursor.execute(
                    "INSERT INTO transactions (user_id, type, category, amount, note, date) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        user_id,
                        "Chi tiêu",
                        "Cho vay",
                        float(amount),
                        note_final,
                        date_str,
                    ),
                )
                cursor.execute(
                    "INSERT INTO debts (user_id, person_name, debt_type, amount, status, date) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        user_id,
                        person.strip(),
                        "Cho vay (Người khác nợ mình)",
                        float(amount),
                        "Đang nợ",
                        date_str,
                    ),
                )
            elif t_type == "Đi vay (Mình nợ người khác)":
                note_final = (
                    f"Mượn tiền từ {person.strip()}"
                    + (f": {note.strip()}" if note.strip() else "")
                )
                cursor.execute(
                    "INSERT INTO transactions (user_id, type, category, amount, note, date) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        user_id,
                        "Thu nhập",
                        "Đi vay",
                        float(amount),
                        note_final,
                        date_str,
                    ),
                )
                cursor.execute(
                    "INSERT INTO debts (user_id, person_name, debt_type, amount, status, date) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        user_id,
                        person.strip(),
                        "Đi vay (Mình nợ người khác)",
                        float(amount),
                        "Đang nợ",
                        date_str,
                    ),
                )
            else:
                cursor.execute(
                    "INSERT INTO transactions (user_id, type, category, amount, note, date) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, t_type, category, float(amount), note, date_str),
                )

            conn.commit()
            st.session_state["clear_trans_form"] = True
            st.session_state["trans_success"] = "✅ Đã lưu giao dịch thành công!"
            st.rerun()

elif menu == "🤝 Quản Lý Nợ":
    st.subheader("📋 Danh Sách Khoản Nợ & Cho Vay Chi Tiết")

    if "debt_success" in st.session_state:
        st.success(st.session_state["debt_success"])
        del st.session_state["debt_success"]

    df_active_debts = pd.read_sql_query(
        f"SELECT id, date, person_name, debt_type, amount FROM debts WHERE user_id = {user_id} AND status = 'Đang nợ' ORDER BY id DESC",
        conn,
    )

    if not df_active_debts.empty:
        persons = df_active_debts["person_name"].unique()
        for p_name in persons:
            p_df = df_active_debts[df_active_debts["person_name"] == p_name]
            sum_cho_vay = p_df[p_df["debt_type"].str.contains("Cho vay")][
                "amount"
            ].sum()
            sum_di_vay = p_df[p_df["debt_type"].str.contains("Đi vay")][
                "amount"
            ].sum()

            info_texts = []
            if sum_cho_vay > 0:
                info_texts.append(
                    f"Nợ bạn: {sum_cho_vay:,.0f} đ".replace(",", ".")
                )
            if sum_di_vay > 0:
                info_texts.append(
                    f"Bạn nợ: {sum_di_vay:,.0f} đ".replace(",", ".")
                )

            label_str = f"👤 {p_name} — ({' | '.join(info_texts)})"

            with st.expander(label_str):
                for idx, row in p_df.iterrows():
                    d_id = row["id"]
                    d_type_text = row["debt_type"]
                    d_amt = row["amount"]
                    d_dt = row["date"]

                    col_d1, col_d2, col_d3 = st.columns([2, 1, 1])
                    with col_d1:
                        st.write(
                            f"🗓️ **{d_dt}** | {d_type_text}: **{d_amt:,.0f} đ**. *({doc_so_vn(d_amt)})*"
                        )

                    # NÚT TRẢ BỚT (TRẢ TRƯỚC 1 ÍT)
                    with col_d2:
                        with st.popover("💵 Trả bớt"):
                            partial_val_raw = st.text_input(
                                "Số tiền trả bớt (VNĐ)",
                                placeholder="Gõ số tiền...",
                                key=f"partial_amt_{d_id}",
                            )
                            clean_p = (
                                "".join(
                                    c for c in partial_val_raw if c.isdigit()
                                )
                                if partial_val_raw
                                else ""
                            )
                            p_amt = int(clean_p) if clean_p else 0

                            if st.button("XÁC NHẬN", key=f"btn_confirm_p_{d_id}"):
                                today_now = datetime.now().strftime("%Y-%m-%d")
                                is_cho_vay = "Cho vay" in d_type_text

                                if p_amt <= 0:
                                    st.error("⚠️ Số tiền không hợp lệ!")
                                elif p_amt >= d_amt:
                                    cursor.execute(
                                        "UPDATE debts SET status = 'Đã trả' WHERE id = ? AND user_id = ?",
                                        (d_id, user_id),
                                    )
                                    if is_cho_vay:
                                        cursor.execute(
                                            "INSERT INTO transactions (user_id, type, category, amount, note, date) VALUES (?, ?, ?, ?, ?, ?)",
                                            (
                                                user_id,
                                                "Thu nợ",
                                                "Thu hồi nợ",
                                                float(d_amt),
                                                f"Thu nợ từ {p_name} (Thanh toán xong)",
                                                today_now,
                                            ),
                                        )
                                    else:
                                        cursor.execute(
                                            "INSERT INTO transactions (user_id, type, category, amount, note, date) VALUES (?, ?, ?, ?, ?, ?)",
                                            (
                                                user_id,
                                                "Trả nợ",
                                                "Trả nợ",
                                                float(d_amt),
                                                f"Trả nợ cho {p_name} (Thanh toán xong)",
                                                today_now,
                                            ),
                                        )

                                    conn.commit()
                                    st.session_state["debt_success"] = (
                                        f"🎉 Đã thu/trả xong toàn bộ khoản {d_amt:,.0f}đ!"
                                    )
                                    st.rerun()
                                else:
                                    new_amt = d_amt - p_amt
                                    cursor.execute(
                                        "UPDATE debts SET amount = ? WHERE id = ? AND user_id = ?",
                                        (new_amt, d_id, user_id),
                                    )
                                    if is_cho_vay:
                                        cursor.execute(
                                            "INSERT INTO transactions (user_id, type, category, amount, note, date) VALUES (?, ?, ?, ?, ?, ?)",
                                            (
                                                user_id,
                                                "Thu nợ",
                                                "Thu hồi nợ",
                                                float(p_amt),
                                                f"Thu nợ từ {p_name} (Trả bớt {p_amt:,.0f}đ)",
                                                today_now,
                                            ),
                                        )
                                    else:
                                        cursor.execute(
                                            "INSERT INTO transactions (user_id, type, category, amount, note, date) VALUES (?, ?, ?, ?, ?, ?)",
                                            (
                                                user_id,
                                                "Trả nợ",
                                                "Trả nợ",
                                                float(p_amt),
                                                f"Trả nợ cho {p_name} (Trả bớt {p_amt:,.0f}đ)",
                                                today_now,
                                            ),
                                        )

                                    conn.commit()
                                    st.session_state["debt_success"] = (
                                        f"✅ Đã thu/trả bớt {p_amt:,.0f}đ của {p_name}! Số tiền còn lại: {new_amt:,.0f}đ."
                                    )
                                    st.rerun()

                    # NÚT TRẢ HẾT HOÀN TOÀN
                    with col_d3:
                        btn_label = (
                            "✅ Đã Thu Xong"
                            if "Cho vay" in d_type_text
                            else "✅ Đã Trả Nợ"
                        )
                        if st.button(btn_label, key=f"pay_debt_{d_id}"):
                            today_now = datetime.now().strftime("%Y-%m-%d")
                            is_cho_vay = "Cho vay" in d_type_text

                            cursor.execute(
                                "UPDATE debts SET status = 'Đã trả' WHERE id = ? AND user_id = ?",
                                (d_id, user_id),
                            )
                            if is_cho_vay:
                                cursor.execute(
                                    "INSERT INTO transactions (user_id, type, category, amount, note, date) VALUES (?, ?, ?, ?, ?, ?)",
                                    (
                                        user_id,
                                        "Thu nợ",
                                        "Thu hồi nợ",
                                        float(d_amt),
                                        f"Thu xong toàn bộ nợ từ {p_name}",
                                        today_now,
                                    ),
                                )
                            else:
                                cursor.execute(
                                    "INSERT INTO transactions (user_id, type, category, amount, note, date) VALUES (?, ?, ?, ?, ?, ?)",
                                    (
                                        user_id,
                                        "Trả nợ",
                                        "Trả nợ",
                                        float(d_amt),
                                        f"Thanh toán xong toàn bộ nợ cho {p_name}",
                                        today_now,
                                    ),
                                )

                            conn.commit()
                            st.session_state["debt_success"] = (
                                f"🎉 Đã thu/trả xong khoản {d_amt:,.0f}đ của {p_name}!"
                            )
                            st.rerun()
    else:
        st.info("Hiện không có khoản nợ nào chưa thanh toán.")

elif menu == "🍕 Chia Bill":
    st.subheader("🍕 Chia Tiền Hóa Đơn Mới")

    if "bill_member_count" not in st.session_state:
        st.session_state["bill_member_count"] = 1

    if st.session_state.get("clear_bill_form"):
        st.session_state["bill_title"] = ""
        st.session_state["bill_amount"] = ""
        st.session_state["bill_member_count"] = 1
        for k in list(st.session_state.keys()):
            if k.startswith("member_name_") or k.startswith("bill_sel_"):
                del st.session_state[k]
        st.session_state["clear_bill_form"] = False

    if "bill_success" in st.session_state:
        st.success(st.session_state["bill_success"])
        del st.session_state["bill_success"]

    bill_date = st.date_input(
        "🗓️ Ngày ăn uống / chia bill", datetime.now(), key="bill_date"
    )
    bill_title = st.text_input(
        "Tên bữa ăn / Hóa đơn (vd: Lẩu Kichi, Thuê sân bóng...)",
        key="bill_title",
    )

    raw_amount = st.text_input(
        "Tổng số tiền hóa đơn (VNĐ)",
        placeholder="Gõ số tiền...",
        key="bill_amount",
    )
    clean_amount_str = (
        "".join(c for c in raw_amount if c.isdigit()) if raw_amount else ""
    )
    total_bill = int(clean_amount_str) if clean_amount_str else 0

    st.markdown("---")
    st.markdown("### 👥 Danh Sách Những Người Nợ Bạn")
    st.caption("Mặc định hóa đơn đã bao gồm **Bạn**. Bấm nút dưới để thêm từng người nợ:")

    col_b1, col_b2, _ = st.columns([1, 1, 2])
    with col_b1:
        if st.button("➕ Thêm người nợ"):
            st.session_state["bill_member_count"] += 1
            st.rerun()
    with col_b2:
        if st.button("➖ Xóa bớt"):
            if st.session_state["bill_member_count"] > 1:
                st.session_state["bill_member_count"] -= 1
                st.rerun()

    members_list = []
    num_added = st.session_state["bill_member_count"]

    for i in range(num_added):
        st.markdown(f"**👤 Tên người nợ thứ {i+1}:**")
        m_name = ""
        if existing_persons:
            b_opts = [
                "-- Chọn người từ danh bạ --",
                "➕ Nhập tên người mới...",
            ] + existing_persons
            sel_b = st.selectbox(
                f"Danh bạ #{i+1}",
                b_opts,
                key=f"bill_sel_{i}",
                label_visibility="collapsed",
            )
            if sel_b == "➕ Nhập tên người mới...":
                m_name = st.text_input(
                    f"Gõ tên mới #{i+1}",
                    placeholder=f"Nhập tên người thứ {i+1}...",
                    key=f"member_name_{i}",
                    label_visibility="collapsed",
                )
            elif sel_b != "-- Chọn người từ danh bạ --":
                m_name = sel_b
        else:
            m_name = st.text_input(
                f"Tên người #{i+1}",
                placeholder=f"Nhập tên người thứ {i+1}...",
                key=f"member_name_{i}",
                label_visibility="collapsed",
            )

        if m_name and m_name.strip():
            members_list.append(m_name.strip())

    total_people = num_added + 1

    if total_bill > 0:
        per_person = total_bill / total_people
        st.markdown(
            f"""
            <div style="background-color: #f0fdf4; border: 2px solid #22c55e; border-radius: 10px; padding: 12px; margin-top: 10px; margin-bottom: 10px;">
                <p style="font-size: 16px; color: #15803d; margin: 0;">👥 <b>Tổng cộng:</b> {total_people} người (Bạn + {num_added} người khác)</p>
                <p style="font-size: 20px; color: #15803d; margin: 4px 0 0 0;">💰 <b>Mỗi người trả:</b> <span style="font-size: 24px; font-weight: 900; color: #166534;">{per_person:,.0f} đ</span></p>
                <p style="font-size: 15px; color: #15803d; margin: 4px 0 0 0;">🔤 <b>Bằng chữ:</b> <i>{doc_so_vn(per_person)}</i></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    auto_record_debt = st.checkbox(
        "🤝 Tự động lưu phần của bạn vào 'Chi tiêu' và ghi nợ cho những người trên",
        value=True,
    )

    if st.button("LƯU & TỰ ĐỘNG PHÂN CHIA"):
        if total_bill <= 0:
            st.error("⚠️ Vui lòng nhập số tiền hóa đơn hợp lệ!")
        elif auto_record_debt and len(members_list) == 0:
            st.error(
                "⚠️ Vui lòng chọn hoặc nhập tên ít nhất 1 người nợ hợp lệ!"
            )
        else:
            per_person = total_bill / total_people
            date_str = bill_date.strftime("%Y-%m-%d")
            title_name = bill_title.strip() if bill_title.strip() else "Chia bill"

            if auto_record_debt:
                cursor.execute(
                    "INSERT INTO transactions (user_id, type, category, amount, note, date) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        user_id,
                        "Chi tiêu",
                        title_name,
                        float(per_person),
                        f"Phần tiền của bạn trong bill {total_bill:,.0f}đ",
                        date_str,
                    ),
                )
                for member in members_list:
                    cursor.execute(
                        "INSERT INTO debts (user_id, person_name, debt_type, amount, status, date) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            user_id,
                            member,
                            "Cho vay (Người khác nợ mình)",
                            float(per_person),
                            "Đang nợ",
                            date_str,
                        ),
                    )
                conn.commit()
                st.session_state["bill_success"] = (
                    f"✅ Đã chia bill thành công! Đã lưu {per_person:,.0f}đ vào Chi tiêu và ghi nợ cho {len(members_list)} người."
                )
            else:
                st.session_state["bill_success"] = (
                    f"✅ Đã tính xong: Mỗi người trả {per_person:,.0f} đ!"
                )

            st.session_state["clear_bill_form"] = True
            st.rerun()

elif menu == "📊 Báo Cáo Chi Tiết":
    st.subheader("📊 Báo Cáo Chi Tiết Lịch Sử Dòng Tiền & Nợ")

    filter_type = st.selectbox(
        "🔍 Chọn khoảng thời gian muốn lọc:",
        [
            "🌐 Tất cả thời gian",
            "📆 Theo Ngày",
            "🗓️ Theo Tuần (Từ T2 -> CN)",
            "📅 Theo Tháng",
            "📅 Theo Năm",
        ],
    )

    today = datetime.now().date()

    df_trans_all = pd.read_sql_query(
        f"SELECT id, date, type, category, amount, note FROM transactions WHERE user_id = {user_id} ORDER BY date DESC, id DESC",
        conn,
    )
    df_debts_all = pd.read_sql_query(
        f"SELECT * FROM debts WHERE user_id = {user_id} ORDER BY date DESC, id DESC",
        conn,
    )

    df_trans_filtered = df_trans_all.copy()
    df_debts_filtered = df_debts_all.copy()

    if filter_type == "📆 Theo Ngày":
        sel_date = st.date_input("🗓️ Chọn ngày xem báo cáo:", today)
        date_str = sel_date.strftime("%Y-%m-%d")
        if not df_trans_filtered.empty:
            df_trans_filtered = df_trans_filtered[
                df_trans_filtered["date"] == date_str
            ]
        if not df_debts_filtered.empty:
            df_debts_filtered = df_debts_filtered[
                df_debts_filtered["date"] == date_str
            ]

    elif filter_type == "🗓️ Theo Tuần (Từ T2 -> CN)":
        sel_date = st.date_input("🗓️ Chọn 1 ngày nằm trong tuần cần xem:", today)
        start_of_week = sel_date - timedelta(days=sel_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        st.info(
            f"📆 **Tuần đang xem:** từ ngày `{start_of_week.strftime('%d/%m/%Y')}` đến ngày `{end_of_week.strftime('%d/%m/%Y')}`"
        )
        start_str = start_of_week.strftime("%Y-%m-%d")
        end_str = end_of_week.strftime("%Y-%m-%d")

        if not df_trans_filtered.empty:
            df_trans_filtered = df_trans_filtered[
                (df_trans_filtered["date"] >= start_str)
                & (df_trans_filtered["date"] <= end_str)
            ]
        if not df_debts_filtered.empty:
            df_debts_filtered = df_debts_filtered[
                (df_debts_filtered["date"] >= start_str)
                & (df_debts_filtered["date"] <= end_str)
            ]

    elif filter_type == "📅 Theo Tháng":
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            sel_month = st.selectbox(
                "🗓️ Chọn Tháng", list(range(1, 13)), index=today.month - 1
            )
        with col_m2:
            sel_year = st.number_input(
                "📅 Chọn Năm", min_value=2000, max_value=2100, value=today.year
            )
        month_prefix = f"{sel_year:04d}-{sel_month:02d}"

        if not df_trans_filtered.empty:
            df_trans_filtered = df_trans_filtered[
                df_trans_filtered["date"].str.startswith(
                    month_prefix, na=False
                )
            ]
        if not df_debts_filtered.empty:
            df_debts_filtered = df_debts_filtered[
                df_debts_filtered["date"].str.startswith(
                    month_prefix, na=False
                )
            ]

    elif filter_type == "📅 Theo Năm":
        sel_year = st.number_input(
            "📅 Chọn Năm", min_value=2000, max_value=2100, value=today.year
        )
        year_prefix = f"{sel_year:04d}"

        if not df_trans_filtered.empty:
            df_trans_filtered = df_trans_filtered[
                df_trans_filtered["date"].str.startswith(
                    year_prefix, na=False
                )
            ]
        if not df_debts_filtered.empty:
            df_debts_filtered = df_debts_filtered[
                df_debts_filtered["date"].str.startswith(year_prefix, na=False)
            ]

    f_income = (
        df_trans_filtered[
            df_trans_filtered["type"].isin(["Thu nhập", "Thu nợ"])
        ]["amount"].sum()
        if not df_trans_filtered.empty
        else 0.0
    )
    f_expense = (
        df_trans_filtered[
            df_trans_filtered["type"].isin(["Chi tiêu", "Trả nợ"])
        ]["amount"].sum()
        if not df_trans_filtered.empty
        else 0.0
    )
    f_balance = f_income - f_expense

    st.markdown(
        f"""
        <div style="background-color: #f8fafc; border: 2px solid #cbd5e1; border-radius: 10px; padding: 12px; margin-top: 8px; margin-bottom: 15px;">
            <p style="font-size: 16px; margin: 0; font-weight: bold;">📊 TỔNG QUAN KỲ ĐANG XEM:</p>
            <div style="display: flex; gap: 15px; flex-wrap: wrap; margin-top: 6px;">
                <span style="font-size: 16px; color: #166534;">💵 Thu vào: <b>{f_income:,.0f} đ</b></span>
                <span style="font-size: 16px; color: #991b1b;">💸 Chi ra: <b>{f_expense:,.0f} đ</b></span>
                <span style="font-size: 16px; color: #1e40af;">💳 Dư kỳ này: <b>{f_balance:,.0f} đ</b></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.subheader("📋 Lịch Sử Giao Dịch Thu / Chi")
    if not df_trans_filtered.empty:
        df_trans_display = df_trans_filtered.copy()
        df_trans_display = df_trans_display[
            ["id", "date", "type", "category", "amount", "note"]
        ]
        df_trans_display.columns = [
            "ID",
            "Ngày",
            "Loại",
            "Danh Mục",
            "Số Tiền",
            "Ghi Chú",
        ]
        df_trans_display["Số Tiền Bằng Chữ"] = df_trans_display[
            "Số Tiền"
        ].apply(doc_so_vn)
        df_trans_display["Số Tiền"] = df_trans_display["Số Tiền"].apply(
            lambda x: f"{x:,.0f} đ".replace(",", ".")
        )
        st.dataframe(df_trans_display, use_container_width=True)
    else:
        st.info("Không có giao dịch thu/chi nào trong khoảng thời gian này.")

    st.markdown("---")
    st.subheader("💳 Danh Sách Khoản Nợ")
    if not df_debts_filtered.empty:
        unique_persons = df_debts_filtered["person_name"].unique()
        for person_name in unique_persons:
            p_df = df_debts_filtered[
                df_debts_filtered["person_name"] == person_name
            ]
            cho_vay_unpaid = p_df[
                (p_df["debt_type"].str.contains("Cho vay"))
                & (p_df["status"] == "Đang nợ")
            ]["amount"].sum()
            di_vay_unpaid = p_df[
                (p_df["debt_type"].str.contains("Đi vay"))
                & (p_df["status"] == "Đang nợ")
            ]["amount"].sum()

            summary_parts = []
            if cho_vay_unpaid > 0:
                summary_parts.append(
                    f"Nợ bạn: {cho_vay_unpaid:,.0f} đ".replace(",", ".")
                )
            if di_vay_unpaid > 0:
                summary_parts.append(
                    f"Bạn nợ: {di_vay_unpaid:,.0f} đ".replace(",", ".")
                )
            if not summary_parts:
                summary_parts.append("Đã thanh toán hết ✅")

            expander_label = f"👤 **{person_name}** — ({' | '.join(summary_parts)})"

            with st.expander(expander_label):
                display_df = p_df[
                    ["id", "date", "debt_type", "amount", "status"]
                ].copy()
                display_df.columns = [
                    "ID",
                    "Ngày Vay/Mượn",
                    "Loại Nợ",
                    "Số Tiền",
                    "Trạng Thái",
                ]
                display_df["Số Tiền Bằng Chữ"] = display_df["Số Tiền"].apply(
                    doc_so_vn
                )
                display_df["Số Tiền"] = display_df["Số Tiền"].apply(
                    lambda x: f"{x:,.0f} đ".replace(",", ".")
                )
                st.dataframe(display_df, use_container_width=True)
    else:
        st.info("Không có khoản nợ nào trong khoảng thời gian này.")