from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import sqlite3
import hashlib
import os

# === ตรวจสอบและสร้างฐานข้อมูลอัตโนมัติจากไฟล์ setup.py ===
def init_db_if_needed():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'esports_pro.db')
    if not os.path.exists(db_path) or os.path.getsize(db_path) < 10000:
        import setup
        setup.initialize_database()

init_db_if_needed()

app = Flask(__name__)
app.secret_key = 'super_secure_fspp_esports_support_key'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'esports_pro.db')

def get_database_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ==========================================
# 1. ส่วนแสดงผลหลัก (Dashboard)
# ==========================================
@app.route('/')
def index():
    conn = get_database_connection()
    players_query = '''
        SELECT p.player_id, p.ign, p.real_name, p.role, p.avatar_url, 
               t.team_name, t.region,
               GROUP_CONCAT(gi.item_name || ' (' || gi.category || ')', ', ') AS assigned_gears
        FROM Players p
        LEFT JOIN Teams t ON p.team_id = t.team_id
        LEFT JOIN Player_Gears pg ON p.player_id = pg.player_id
        LEFT JOIN Gear_Inventory gi ON pg.item_id = gi.item_id
        GROUP BY p.player_id
        ORDER BY p.player_id DESC
    '''
    players = conn.execute(players_query).fetchall()
    teams = conn.execute('SELECT * FROM Teams ORDER BY team_name ASC').fetchall()
    inventory = conn.execute('SELECT * FROM Gear_Inventory ORDER BY item_id DESC').fetchall()
    tournaments = conn.execute('SELECT * FROM Tournaments ORDER BY prize_pool DESC').fetchall()
    sponsors = conn.execute('SELECT * FROM Sponsors ORDER BY investment_amt DESC').fetchall()
    members = conn.execute('SELECT * FROM Members ORDER BY join_date DESC').fetchall()
    
    stats = {
        'total_players': conn.execute('SELECT COUNT(*) FROM Players').fetchone()[0],
        'total_inventory_items': conn.execute('SELECT SUM(stock_qty) FROM Gear_Inventory').fetchone()[0] or 0,
        'total_prize_pool': conn.execute('SELECT SUM(prize_pool) FROM Tournaments').fetchone()[0] or 0.0,
        'total_teams': conn.execute('SELECT COUNT(*) FROM Teams').fetchone()[0]
    }
    conn.close()
    return render_template('index.html', players=players, teams=teams, inventory=inventory, tournaments=tournaments, sponsors=sponsors, stats=stats, members=members)

# ==========================================
# 2. ระบบยืนยันตัวตน (Admin Auth)
# ==========================================
@app.route('/login', methods=['POST'])
def process_login():
    username = request.form.get('username')
    password = request.form.get('password')
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_database_connection()
    admin = conn.execute('SELECT * FROM Admins WHERE username = ? AND password_hash = ?', (username, hashed_password)).fetchone()
    conn.close()
    
    if admin:
        session['admin_authorized'] = True
        session['active_admin_user'] = admin['username']
        session['active_admin_name'] = admin['staff_name']
        session['active_admin_role'] = admin['role']
    return redirect(url_for('index'))

@app.route('/logout')
def process_logout():
    session.clear()
    return redirect(url_for('index'))

# ==========================================
# 3. ฟังก์ชันการจัดการข้อมูลนักแข่ง (Player CRUD)
# ==========================================
@app.route('/player/create', methods=['POST'])
def create_player():
    if not session.get('admin_authorized'): return redirect(url_for('index'))
    ign = request.form.get('ign')
    real_name = request.form.get('real_name')
    role = request.form.get('role')
    team_id = request.form.get('team_id', type=int)
    avatar_url = f"https://api.dicebear.com/7.x/bottts/svg?seed={ign}"
    
    conn = get_database_connection()
    try:
        conn.execute('INSERT INTO Players (ign, real_name, role, team_id, avatar_url) VALUES (?, ?, ?, ?, ?)', (ign, real_name, role, team_id, avatar_url))
        conn.commit()
    except sqlite3.IntegrityError: pass
    finally: conn.close()
    return redirect(url_for('index'))

@app.route('/player/delete/<int:player_id>')
def delete_player(player_id):
    if not session.get('admin_authorized'): return redirect(url_for('index'))
    conn = get_database_connection()
    conn.execute('DELETE FROM Players WHERE player_id = ?', (player_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# ==========================================
# 4. ฟังก์ชันการจัดการคลังฮาร์ดแวร์และการเบิกจ่าย
# ==========================================
@app.route('/inventory/create', methods=['POST'])
def create_inventory_item():
    if not session.get('admin_authorized'): return redirect(url_for('index'))
    item_name = request.form.get('item_name')
    category = request.form.get('category')
    brand = request.form.get('brand')
    stock_qty = request.form.get('stock_qty', type=int)
    image_url = request.form.get('image_url') or "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=150&auto=format&fit=crop&q=80"
    
    conn = get_database_connection()
    conn.execute('INSERT INTO Gear_Inventory (item_name, category, brand, stock_qty, image_url) VALUES (?, ?, ?, ?, ?)', (item_name, category, brand, stock_qty, image_url))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/inventory/assign', methods=['POST'])
def assign_player_gear():
    if not session.get('admin_authorized'): return redirect(url_for('index'))
    player_id = request.form.get('player_id', type=int)
    item_id = request.form.get('item_id', type=int)
    assigned_date = request.form.get('assigned_date')
    
    conn = get_database_connection()
    item = conn.execute('SELECT stock_qty FROM Gear_Inventory WHERE item_id = ?', (item_id,)).fetchone()
    if item and item['stock_qty'] > 0:
        conn.execute('INSERT INTO Player_Gears (player_id, item_id, assigned_date) VALUES (?, ?, ?)', (player_id, item_id, assigned_date))
        conn.execute('UPDATE Gear_Inventory SET stock_qty = stock_qty - 1 WHERE item_id = ?', (item_id,))
        conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/inventory/delete/<int:item_id>')
def delete_inventory_item(item_id):
    if not session.get('admin_authorized'): return redirect(url_for('index'))
    conn = get_database_connection()
    conn.execute('DELETE FROM Gear_Inventory WHERE item_id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# ==========================================
# 5. สารสนเทศสาธารณะย่อย
# ==========================================
@app.route('/teams')
def teams_list():
    conn = get_database_connection()
    teams_data = conn.execute('''
        SELECT t.*, COUNT(DISTINCT p.player_id) as player_count
        FROM Teams t LEFT JOIN Players p ON t.team_id = p.team_id
        GROUP BY t.team_id ORDER BY t.team_name
    ''').fetchall()
    conn.close()
    return render_template('teams.html', teams=teams_data)

@app.route('/tournaments')
def tournaments_list():
    conn = get_database_connection()
    tournaments = conn.execute('SELECT * FROM Tournaments ORDER BY tourney_id DESC').fetchall()
    conn.close()
    return render_template('tournaments.html', tournaments=tournaments)

if __name__ == '__main__':
    app.run(debug=True)