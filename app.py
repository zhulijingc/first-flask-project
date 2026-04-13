from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# ================== 初始化数据库 ==================
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # 用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # 商品表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            description TEXT
        )
    """)

    # 判断商品表是否为空
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]

    # 只在第一次插入测试数据
    if count == 0:
        cursor.execute(
            "INSERT INTO products (name, price, description) VALUES (?, ?, ?)",
            ("iPhone 15", 5999, "苹果手机")
        )
        cursor.execute(
            "INSERT INTO products (name, price, description) VALUES (?, ?, ?)",
            ("耳机", 199, "无线蓝牙耳机")
        )

    conn.commit()
    conn.close()


# 启动时初始化数据库
init_db()


# ================== 首页 ==================
@app.route("/")
def home():
    return render_template("index.html")


# ================== 注册 ==================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "用户已存在"
        except Exception as e:
            conn.close()
            print("错误：", e)
            return "注册失败"

        conn.close()
        return redirect(url_for("login"))

    return render_template("register.html")


# ================== 登录 ==================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()

        conn.close()

        if user:
            return redirect(url_for("products"))
        else:
            return "账号或密码错误"

    return render_template("login.html")


# ================== 商品列表 ==================
@app.route("/products")
def products():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()
    return render_template("products.html", products=products)


# ================== 商品详情 ==================
@app.route("/product/<int:product_id>")
def product_detail(product_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE id=?",
        (product_id,)
    )
    product = cursor.fetchone()

    conn.close()
    return render_template("product_detail.html", product=product)


# ================== 启动 ==================
if __name__ == "__main__":
    app.run(debug=True)