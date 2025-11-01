import streamlit as st
import math, ast, operator, re

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Casio fx-991 Ultra-Fast", page_icon="🧮", layout="centered")

# ---------- STYLES ----------
st.markdown("""
<style>
body {
    background: radial-gradient(circle at 20% 20%, #0a0f18, #000);
    font-family: 'Orbitron', sans-serif;
    color: #00eaff;
}
.calc-container {
    width: 380px;
    margin: auto;
    padding: 25px;
    border-radius: 20px;
    background: rgba(10, 20, 30, 0.9);
    border: 1px solid rgba(0,255,255,0.2);
    box-shadow: 0 0 30px rgba(0,255,255,0.2);
}
.display {
    background: linear-gradient(145deg, #010509, #0b1118);
    color: #00ffc6;
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
    font-size: 1.3rem;
    color: #00ffff;
    margin-bottom: 10px;
}
div[data-testid="stButton"] button {
    background-color: #1a1f28 !important;
    color: #e6e6e6 !important;
    border-radius: 8px !important;
    height: 48px !important;
    font-size: 1rem !important;
    border: 0.5px solid rgba(0,255,255,0.2) !important;
    transition: all 0.1s ease-in-out;
    box-shadow: 0 0 0 rgba(0,255,255,0);
}
div[data-testid="stButton"] button:hover {
    background-color: #00ffff !important;
    color: #000 !important;
    box-shadow: 0 0 10px #00ffff;
}
div[data-testid="stButton"] button:active {
    transform: scale(0.95);
    box-shadow: 0 0 20px #00ffff;
}
.orange { background-color: #ffaa33 !important; color: #000 !important; font-weight: bold !important; }
.blue { background-color: #0096ff !important; color: #fff !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

# ---------- STATE ----------
if "expr" not in st.session_state:
    st.session_state.expr = ""
if "mode" not in st.session_state:
    st.session_state.mode = "DEG"
if "memory" not in st.session_state:
    st.session_state.memory = 0.0
if "display" not in st.session_state:
    st.session_state.display = "0"

# ---------- SAFE EVALUATION ----------
_ops = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}
def make_names(mode):
    f = {
        "sqrt": math.sqrt, "log": math.log10, "ln": math.log,
        "sin": math.sin if mode=="RAD" else lambda x: math.sin(math.radians(x)),
        "cos": math.cos if mode=="RAD" else lambda x: math.cos(math.radians(x)),
        "tan": math.tan if mode=="RAD" else lambda x: math.tan(math.radians(x)),
        "pi": math.pi, "e": math.e, "factorial": math.factorial, "abs": abs
    }
    return f
FACTORIAL_RE = re.compile(r'(\d+|\))!')
def preprocess(expr):
    expr = expr.replace("^","**").replace("π","pi")
    prev=None
    while prev!=expr:
        prev=expr
        expr=FACTORIAL_RE.sub(r'factorial(\\1)',expr)
    return expr
def safe_eval(expr, mode):
    try:
        tree=ast.parse(preprocess(expr),mode='eval')
        return _eval(tree.body, make_names(mode))
    except Exception:
        return "Error"
def _eval(node,names):
    if isinstance(node,ast.BinOp): return _ops[type(node.op)](_eval(node.left,names),_eval(node.right,names))
    if isinstance(node,ast.UnaryOp): return _ops[type(node.op)](_eval(node.operand,names))
    if isinstance(node,ast.Call): return names[node.func.id](*[_eval(a,names) for a in node.args])
    if isinstance(node,ast.Name): return names[node.id]
    if isinstance(node,ast.Constant): return node.value
    return None

# ---------- LOGIC ----------
def press(k):
    if k=="C":
        st.session_state.expr=""
        st.session_state.display="0"
    elif k=="=":
        res=safe_eval(st.session_state.expr,st.session_state.mode)
        st.session_state.display=str(res)
        st.session_state.expr=str(res)
    elif k=="DEG/RAD":
        st.session_state.mode="RAD" if st.session_state.mode=="DEG" else "DEG"
    elif k=="M+":
        try: st.session_state.memory+=float(safe_eval(st.session_state.expr,st.session_state.mode))
        except: pass
    elif k=="M-":
        try: st.session_state.memory-=float(safe_eval(st.session_state.expr,st.session_state.mode))
        except: pass
    elif k=="MR":
        st.session_state.expr+=str(st.session_state.memory)
        st.session_state.display=st.session_state.expr
    elif k=="MC":
        st.session_state.memory=0.0
    else:
        st.session_state.expr+=k
        st.session_state.display=st.session_state.expr

# ---------- UI ----------
st.markdown("<div class='calc-container'>", unsafe_allow_html=True)
st.markdown("<div class='title'>CASIO fx-991 | Ultra-Fast</div>", unsafe_allow_html=True)
st.markdown(f"<div class='display'>{st.session_state.display}</div>", unsafe_allow_html=True)

layout = [
    ["MC","MR","M+","M-"],
    ["sin(","cos(","tan(","√("],
    ["log(","ln(","(",")"],
    ["7","8","9","/"],
    ["4","5","6","*"],
    ["1","2","3","-"],
    ["0",".","^","+"],
    ["π","e","!","="],
    ["C","DEG/RAD","",""]
]

# Build once, use callbacks (fast!)
for row in layout:
    cols = st.columns(4)
    for i,key in enumerate(row):
        if not key: cols[i].write("")
        else:
            classes = ""
            if key in ["=", "C"]: classes = "orange"
            elif key in ["MC","MR","M+","M-","DEG/RAD"]: classes = "blue"
            cols[i].button(key, key=key, on_click=press, args=(key,), use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)
st.caption("Made with ❤️ using Streamlit | Instant Mode")
