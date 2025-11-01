import streamlit as st
import math, re, ast, operator

# ---------------- Page Setup ----------------
st.set_page_config(page_title="Casio fx-991 | Ultra-Fast", page_icon="🧮", layout="centered")

# ---------------- CSS Styling ----------------
st.markdown("""
<style>
body {
    background: radial-gradient(circle at top, #0a0f18, #010409);
    font-family: 'Orbitron', sans-serif;
    color: #00eaff;
}
.calc-container {
    width: 380px;
    margin: auto;
    padding: 20px 25px 30px 25px;
    border-radius: 25px;
    background: rgba(15, 25, 40, 0.85);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(0, 255, 255, 0.2);
    box-shadow: 0 0 25px rgba(0,255,255,0.2);
}
.display {
    background: linear-gradient(145deg, #030608, #0b1118);
    color: #00ffc8;
    border-radius: 10px;
    text-align: right;
    font-size: 1.8rem;
    padding: 14px;
    margin-bottom: 15px;
    border: 1px solid rgba(0,255,255,0.25);
    overflow-x: auto;
}
.title {
    text-align: center;
    font-size: 1.2rem;
    color: #00ffff;
    margin-bottom: 10px;
}
button[kind="primary"] {
    transition: transform 0.05s ease-in-out;
}
button[kind="primary"]:active {
    transform: scale(0.96);
}
.btn {
    background-color: #1a1f28 !important;
    color: #e6e6e6 !important;
    border-radius: 8px !important;
    height: 45px !important;
    font-size: 1rem !important;
    border: 0.5px solid rgba(0,255,255,0.15) !important;
}
.btn:hover {
    background-color: #00ffff !important;
    color: #000 !important;
}
.btn-orange { background-color: #ffaa33 !important; color: #000 !important; font-weight: bold; }
.btn-blue { background-color: #00b3ff !important; color: #fff !important; font-weight: bold; }
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

# ---------------- Safe Evaluation ----------------
_ops = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def make_names(mode):
    funcs = {
        "sqrt": math.sqrt, "log": math.log10, "ln": math.log,
        "sin": math.sin if mode == "RAD" else lambda x: math.sin(math.radians(x)),
        "cos": math.cos if mode == "RAD" else lambda x: math.cos(math.radians(x)),
        "tan": math.tan if mode == "RAD" else lambda x: math.tan(math.radians(x)),
        "pi": math.pi, "e": math.e, "factorial": math.factorial, "abs": abs
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
    if isinstance(node, ast.BinOp): return _ops[type(node.op)](_eval(node.left, names), _eval(node.right, names))
    if isinstance(node, ast.UnaryOp): return _ops[type(node.op)](_eval(node.operand, names))
    if isinstance(node, ast.Call): return names.get(node.func.id)(*_eval_args(node.args, names))
    if isinstance(node, ast.Name): return names[node.id]
    if isinstance(node, ast.Constant): return node.value
    return None

def _eval_args(args, names): return [_eval(a, names) for a in args]

# ---------------- Update Functions ----------------
def press(k):
    if k == "C":
        st.session_state.expr, st.session_state.display = "", "0"
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
st.markdown("<div class='title'>CASIO fx-991 | Hyper-Fast Mode</div>", unsafe_allow_html=True)
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
            if key in ["=", "C"]: css += " btn-orange"
            elif key in ["MC", "MR", "M+", "M-", "DEG/RAD"]: css += " btn-blue"
            if cols[i].button(key, key=f"{key}-{i}", use_container_width=True):
                press(key)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- JavaScript Live Update (instant typing feel) ----------------
st.markdown("""
<script>
const display = window.parent.document.querySelector('.display');
let buffer = '';
document.addEventListener('keydown', (e) => {
  if(/^[0-9.+\\-*/()^]$/.test(e.key)) {
    buffer += e.key;
    display.innerText = buffer;
    window.parent.postMessage({type: 'key', value: e.key}, '*');
  }
  if(e.key === 'Enter'){
    window.parent.postMessage({type: 'key', value: '='}, '*');
  }
  if(e.key === 'Backspace'){
    buffer = buffer.slice(0,-1);
    display.innerText = buffer || '0';
  }
});
</script>
""", unsafe_allow_html=True)

st.markdown("<p style='text-align:center;color:#777;'>Made with ❤️ by Ameya | Streamlit Casio fx-991</p>", unsafe_allow_html=True)
