import streamlit as st
import math
import re
import ast
import operator

# ---------------- Page config ----------------
st.set_page_config(page_title="Casio fx-991 Ultra Fast", page_icon="🧮", layout="centered")

# ---------------- Minimal Styles ----------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: #f1f1f1;
    font-family: "Roboto Mono", monospace;
}
.calc-container {
    background: linear-gradient(145deg, #131820, #0e1117);
    width: 380px;
    margin: auto;
    border-radius: 20px;
    padding: 18px;
    box-shadow: 0 0 30px rgba(0,255,255,0.3);
}
.display {
    background-color: #05080d;
    color: #00ffc6;
    border-radius: 10px;
    text-align: right;
    font-size: 1.8rem;
    padding: 14px;
    border: 1px solid rgba(0,255,255,0.2);
    margin-bottom: 12px;
    overflow-x: auto;
}
.btn {
    background-color: #1c212b;
    color: white;
    border: none;
    border-radius: 8px;
    height: 48px;
    font-size: 1.05rem;
    transition: all 0.1s ease-in-out;
}
.btn:hover {
    background-color: #00ffff;
    color: #000;
}
.btn.orange { background-color: #ffb347; color: #1b1000; font-weight: bold; }
.btn.blue { background-color: #00b3b3; color: #fff; font-weight: bold; }
.title {
    text-align: center;
    font-size: 1.4rem;
    color: #00ffff;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- State ----------------
if "expr" not in st.session_state:
    st.session_state.expr = ""
if "mode" not in st.session_state:
    st.session_state.mode = "DEG"
if "memory" not in st.session_state:
    st.session_state.memory = 0.0
if "display" not in st.session_state:
    st.session_state.display = "0"

# ---------------- Safe evaluator ----------------
_ops = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def make_names(mode):
    funcs = {
        "sqrt": math.sqrt,
        "log": math.log10,
        "ln": math.log,
        "sin": math.sin if mode == "RAD" else lambda x: math.sin(math.radians(x)),
        "cos": math.cos if mode == "RAD" else lambda x: math.cos(math.radians(x)),
        "tan": math.tan if mode == "RAD" else lambda x: math.tan(math.radians(x)),
        "pi": math.pi,
        "e": math.e,
        "factorial": math.factorial,
        "abs": abs,
    }
    return funcs

FACTORIAL_RE = re.compile(r'(\d+|\))!')

def preprocess(expr):
    expr = expr.replace("^", "**").replace("π", "pi")
    prev = None
    while prev != expr:
        prev = expr
        expr = FACTORIAL_RE.sub(r'factorial(\1)', expr)
    return expr

def safe_eval(expr, mode):
    try:
        code = preprocess(expr)
        tree = ast.parse(code, mode='eval')
        return _eval(tree.body, make_names(mode))
    except Exception:
        return "Error"

def _eval(node, names):
    if isinstance(node, ast.BinOp):
        return _ops[type(node.op)](_eval(node.left, names), _eval(node.right, names))
    if isinstance(node, ast.UnaryOp):
        return _ops[type(node.op)](_eval(node.operand, names))
    if isinstance(node, ast.Call):
        func = names.get(node.func.id)
        args = [_eval(a, names) for a in node.args]
        return func(*args)
    if isinstance(node, ast.Name):
        return names[node.id]
    if isinstance(node, ast.Constant):
        return node.value
    return None

# ---------------- Fast update functions ----------------
def press(k):
    if k == "C":
        st.session_state.expr = ""
        st.session_state.display = "0"
    elif k == "=":
        res = safe_eval(st.session_state.expr, st.session_state.mode)
        st.session_state.display = str(res)
        st.session_state.expr = str(res)
    elif k == "DEG/RAD":
        st.session_state.mode = "RAD" if st.session_state.mode == "DEG" else "DEG"
    elif k == "M+":
        try: st.session_state.memory += float(safe_eval(st.session_state.expr, st.session_state.mode))
        except: pass
    elif k == "M-":
        try: st.session_state.memory -= float(safe_eval(st.session_state.expr, st.session_state.mode))
        except: pass
    elif k == "MR":
        st.session_state.expr += str(st.session_state.memory)
        st.session_state.display = st.session_state.expr
    elif k == "MC":
        st.session_state.memory = 0.0
    else:
        st.session_state.expr += k
        st.session_state.display = st.session_state.expr

# ---------------- UI ----------------
st.markdown("<div class='calc-container'>", unsafe_allow_html=True)
st.markdown("<div class='title'>CASIO fx-991 | Fast Mode</div>", unsafe_allow_html=True)
st.markdown(f"<div class='display'>{st.session_state.display}</div>", unsafe_allow_html=True)

rows = [
    ["MC", "MR", "M+", "M-"],
    ["sin(", "cos(", "tan(", "√("],
    ["log(", "ln(", "(", ")"],
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "^", "+"],
    ["π", "e", "!", "="],
    ["C", "DEG/RAD", "", ""]
]

for r in rows:
    cols = st.columns(4)
    for i, key in enumerate(r):
        if key == "":
            cols[i].write("")
        else:
            css = "btn"
            if key in ["=", "C"]: css += " orange"
            elif key in ["MC", "MR", "M+", "M-", "DEG/RAD"]: css += " blue"
            if cols[i].button(key, key=f"{key}-{i}"):
                press(key)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#888;'>Made with ❤️ using Streamlit</p>", unsafe_allow_html=True)
