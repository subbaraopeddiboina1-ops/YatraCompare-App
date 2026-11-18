from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_key_travel_app'

def init_db():
    conn = sqlite3.connect('travel_v2.db') # Changed name to avoid old cache error
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS buses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operator TEXT,
            from_city TEXT,
            to_city TEXT,
            base_price INTEGER,
            platform TEXT,
            bus_type TEXT,
            departure_time TEXT,
            link TEXT
        )
    ''')
    cursor.execute('SELECT COUNT(*) FROM buses')
    count = cursor.fetchone()[0]
    if count == 0:
        sample_buses = [
            ("Kaveri Travels", "Hyderabad", "Vijayawada", 600, "RedBus", "AC Sleeper", "Night", "https://www.redbus.in"),
            ("Orange Travels", "Hyderabad", "Vijayawada", 650, "AbhiBus", "AC Seater", "Evening", "https://www.abhibus.com"),
            ("VRL Travels", "Hyderabad", "Vijayawada", 580, "Paytm Bus", "Non-AC Sleeper", "Morning", "https://paytm.com/bus-tickets"),
            ("Morning Star", "Hyderabad", "Vijayawada", 900, "AbhiBus", "AC Sleeper", "Night", "https://www.abhibus.com")
        ]
        cursor.executemany('''
            INSERT INTO buses (operator, from_city, to_city, base_price, platform, bus_type, departure_time, link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_buses)
        conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html', results=None)

@app.route('/search', methods=['POST'])
def search():
    from_city = request.form.get('from_city').strip().title()
    to_city = request.form.get('to_city').strip().title()
    selected_platform = request.form.get('platform', 'All')
    bus_type = request.form.get('bus_type', 'All')
    departure_time = request.form.get('departure_time', 'All')
    max_price = request.form.get('max_price', '10000')
    
    if not max_price:
        max_price = '10000'

    conn = sqlite3.connect('travel_v2.db')
    cursor = conn.cursor()
    
    query = '''
        SELECT operator, from_city, to_city, base_price, platform, bus_type, departure_time, link 
        FROM buses 
        WHERE from_city = ? AND to_city = ? AND base_price <= ?
    '''
    params = [from_city, to_city, int(max_price)]
    
    if selected_platform != 'All':
        query += ' AND platform = ?'
        params.append(selected_platform)
    if bus_type != 'All':
        query += ' AND bus_type = ?'
        params.append(bus_type)
    if departure_time != 'All':
        query += ' AND departure_time = ?'
        params.append(departure_time)
        
    query += ' ORDER BY base_price ASC'
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    matched_buses = []
    for row in rows:
        matched_buses.append({
            "operator": row[0], "from_city": row[1], "to_city": row[2],
            "base_price": row[3], "platform": row[4], "bus_type": row[5],
            "departure_time": row[6], "link": row[7]
        })
    
    return render_template('index.html', results=matched_buses, from_city=from_city, to_city=to_city)

@app.route('/admin-login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username == 'admin' and password == 'admin123':
        session['logged_in'] = True
    else:
        session['logged_in'] = False
        
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/add', methods=['POST'])
def add_bus():
    if not session.get('logged_in'):
        return "Unauthorized Access!", 403
        
    operator = request.form.get('operator')
    from_city = request.form.get('from_city').strip().title()
    to_city = request.form.get('to_city').strip().title()
    base_price = request.form.get('base_price')
    platform = request.form.get('platform')
    bus_type = request.form.get('bus_type')
    departure_time = request.form.get('departure_time')
    link = request.form.get('link')
    
    conn = sqlite3.connect('travel_v2.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO buses (operator, from_city, to_city, base_price, platform, bus_type, departure_time, link)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (operator, from_city, to_city, base_price, platform, bus_type, departure_time, link))
    conn.commit()
    conn.close()
    
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)