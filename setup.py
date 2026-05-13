#!/usr/bin/env python3
"""
FSPP E-Sport (Full Support) - Setup Script with Massive Mock Data
สร้างฐานข้อมูลและเพิ่มข้อมูลจำลอง: 10 ทีม, 35 นักแข่ง, 20 อะไหล่คลัง, 12 ทัวร์นาเมนต์, 30 สปอนเซอร์
"""

import os
import sqlite3
import hashlib

def initialize_database():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'esports_pro.db')
    
    print("=" * 60)
    print("🎮 FSPP E-SPORT SETUP & MASSIVE DATA INITIALIZATION")
    print("=" * 60)
    
    if os.path.exists(db_path):
        os.remove(db_path)
        print("   ✓ อยู่ระหว่างกำลังติดตั้งข้อมูล.....")
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 1. Admins
    c.execute('''
        CREATE TABLE Admins (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            staff_name TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # 2. Teams
    c.execute('''
        CREATE TABLE Teams (
            team_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT UNIQUE NOT NULL,
            region TEXT NOT NULL,
            logo_url TEXT NOT NULL
        )
    ''')
    
    # 3. Players
    c.execute('''
        CREATE TABLE Players (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ign TEXT UNIQUE NOT NULL,
            real_name TEXT NOT NULL,
            role TEXT NOT NULL,
            team_id INTEGER NOT NULL,
            avatar_url TEXT NOT NULL,
            FOREIGN KEY(team_id) REFERENCES Teams(team_id) ON DELETE CASCADE
        )
    ''')
    
    # 4. Gear_Inventory
    c.execute('''
        CREATE TABLE Gear_Inventory (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            brand TEXT NOT NULL,
            stock_qty INTEGER NOT NULL,
            image_url TEXT NOT NULL
        )
    ''')
    
    # 5. Player_Gears
    c.execute('''
        CREATE TABLE Player_Gears (
            assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            assigned_date TEXT NOT NULL,
            FOREIGN KEY(player_id) REFERENCES Players(player_id) ON DELETE CASCADE,
            FOREIGN KEY(item_id) REFERENCES Gear_Inventory(item_id) ON DELETE CASCADE
        )
    ''')
    
    # 6. Tournaments
    c.execute('''
        CREATE TABLE Tournaments (
            tourney_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            game_title TEXT NOT NULL,
            prize_pool REAL NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    
    # 7. Match_Results
    c.execute('''
        CREATE TABLE Match_Results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tourney_id INTEGER NOT NULL,
            team_id INTEGER NOT NULL,
            placement INTEGER NOT NULL,
            kill_points INTEGER NOT NULL,
            FOREIGN KEY(tourney_id) REFERENCES Tournaments(tourney_id) ON DELETE CASCADE,
            FOREIGN KEY(team_id) REFERENCES Teams(team_id) ON DELETE CASCADE
        )
    ''')
    
    # 8. Sponsors
    c.execute('''
        CREATE TABLE Sponsors (
            sponsor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sponsor_name TEXT NOT NULL,
            tier TEXT NOT NULL,
            investment_amt REAL NOT NULL,
            logo_text TEXT NOT NULL
        )
    ''')
    
    # 9. Games
    c.execute('''
        CREATE TABLE Games (
            game_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_title TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL,
            genre TEXT NOT NULL,
            icon_url TEXT NOT NULL
        )
    ''')
    
    # 10. Team_Games
    c.execute('''
        CREATE TABLE Team_Games (
            team_game_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            game_id INTEGER NOT NULL,
            primary_game INTEGER DEFAULT 0,
            FOREIGN KEY(team_id) REFERENCES Teams(team_id) ON DELETE CASCADE,
            FOREIGN KEY(game_id) REFERENCES Games(game_id) ON DELETE CASCADE,
            UNIQUE(team_id, game_id)
        )
    ''')
    
    # 11. Members (เพิ่มฟิลด์ phone สำหรับเก็บเบอร์โทรศัพท์)
    c.execute('''
        CREATE TABLE Members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT DEFAULT '-',
            member_role TEXT NOT NULL,
            join_date TEXT NOT NULL,
            avatar_url TEXT NOT NULL
        )
    ''')
    
    # 12. Roles
    c.execute('''
        CREATE TABLE Roles (
            role_id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL,
            permission_level INTEGER NOT NULL
        )
    ''')
    
    # 13. Match_History
    c.execute('''
        CREATE TABLE Match_History (
            match_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tourney_id INTEGER NOT NULL,
            game_id INTEGER NOT NULL,
            team_id INTEGER NOT NULL,
            opponent_team_id INTEGER,
            match_date TEXT NOT NULL,
            placement INTEGER NOT NULL,
            kill_points INTEGER NOT NULL,
            result TEXT NOT NULL,
            FOREIGN KEY(tourney_id) REFERENCES Tournaments(tourney_id) ON DELETE CASCADE,
            FOREIGN KEY(game_id) REFERENCES Games(game_id) ON DELETE CASCADE,
            FOREIGN KEY(team_id) REFERENCES Teams(team_id) ON DELETE CASCADE,
            FOREIGN KEY(opponent_team_id) REFERENCES Teams(team_id) ON DELETE CASCADE
        )
    ''')
    
    # 14. Tournament_Participation
    c.execute('''
        CREATE TABLE Tournament_Participation (
            participation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tourney_id INTEGER NOT NULL,
            team_id INTEGER NOT NULL,
            join_date TEXT NOT NULL,
            status TEXT NOT NULL,
            final_placement INTEGER,
            FOREIGN KEY(tourney_id) REFERENCES Tournaments(tourney_id) ON DELETE CASCADE,
            FOREIGN KEY(team_id) REFERENCES Teams(team_id) ON DELETE CASCADE,
            UNIQUE(tourney_id, team_id)
        )
    ''')
    
    def hash_pw(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    # 1. Admins
    c.executemany("INSERT INTO Admins (username, password_hash, staff_name, role) VALUES (?, ?, ?, ?)", [
        ("admin", hash_pw("password123"), "Executive Director", "SuperAdmin"),
        ("manager_fspp", hash_pw("fspp2026"), "Full Support Operations Lead", "Manager"),
        ("tech_support", hash_pw("gearsup"), "Hardware Engineer", "InventoryAdmin")
    ])
    
    # 2. Teams (10 ทีมสังกัดย่อยภายใต้เครือข่าย FSPP E-Sport)
    teams_data = [
        ("FSPP E-Sport (Main)", "SEA", "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=400&auto=format&fit=crop&q=80"),
        ("FSPP Academy", "SEA", "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=400&auto=format&fit=crop&q=80"),
        ("FSPP Europe Roster", "EU", "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=400&auto=format&fit=crop&q=80"),
        ("FSPP North America", "NA", "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=400&auto=format&fit=crop&q=80"),
        ("FSPP Korea Force", "KR", "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=400&auto=format&fit=crop&q=80"),
        ("FSPP Japan Apex", "JP", "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=400&auto=format&fit=crop&q=80"),
        ("FSPP Latin America", "SA", "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=400&auto=format&fit=crop&q=80"),
        ("FSPP Oceania Impact", "OCE", "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=400&auto=format&fit=crop&q=80"),
        ("FSPP Middle East", "MEA", "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=400&auto=format&fit=crop&q=80"),
        ("FSPP China Dragon", "CN", "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=400&auto=format&fit=crop&q=80")
    ]
    c.executemany("INSERT INTO Teams (team_name, region, logo_url) VALUES (?, ?, ?)", teams_data)
    
    # 3. Players (นักแข่ง 35 คน กระจายตัวตามทีมต่างๆ)
    players_data = [
        ("GodAim", "Somchai K.", "Attacker", 1, "https://api.dicebear.com/7.x/bottts/svg?seed=GodAim"),
        ("SniperZ", "John D.", "Sniper", 1, "https://api.dicebear.com/7.x/bottts/svg?seed=SniperZ"),
        ("FullSupportX", "Pitipan K.", "Support", 1, "https://api.dicebear.com/7.x/bottts/svg?seed=FullSupportX"),
        ("CarryGod", "Anawin S.", "Flex", 1, "https://api.dicebear.com/7.x/bottts/svg?seed=CarryGod"),
        ("ScoutMaster", "Nattawut P.", "Scout", 1, "https://api.dicebear.com/7.x/bottts/svg?seed=ScoutMaster"),
        ("ViperX", "Lee Sang-hyeok", "IGL", 2, "https://api.dicebear.com/7.x/bottts/svg?seed=ViperX"),
        ("RushB", "Kenji Yamato", "Attacker", 2, "https://api.dicebear.com/7.x/bottts/svg?seed=RushB"),
        ("AlphaAim", "David Miller", "Attacker", 2, "https://api.dicebear.com/7.x/bottts/svg?seed=AlphaAim"),
        ("OmegaHeal", "Chloe Chen", "Support", 2, "https://api.dicebear.com/7.x/bottts/svg?seed=OmegaHeal"),
        ("Shadow", "Ali Mustafa", "Scout", 3, "https://api.dicebear.com/7.x/bottts/svg?seed=Shadow"),
        ("IceStorm", "Alex Petrov", "Sniper", 3, "https://api.dicebear.com/7.x/bottts/svg?seed=IceStorm"),
        ("BlitzKrieg", "Hans Weber", "Attacker", 3, "https://api.dicebear.com/7.x/bottts/svg?seed=BlitzKrieg"),
        ("CyberNaut", "Siddharth R.", "Flex", 3, "https://api.dicebear.com/7.x/bottts/svg?seed=CyberNaut"),
        ("TankerPro", "Mike Tyson", "Support", 4, "https://api.dicebear.com/7.x/bottts/svg?seed=TankerPro"),
        ("ThunderForce", "James Wilson", "Attacker", 4, "https://api.dicebear.com/7.x/bottts/svg?seed=ThunderForce"),
        ("DragonClaw", "Wei Zhang", "Attacker", 4, "https://api.dicebear.com/7.x/bottts/svg?seed=DragonClaw"),
        ("PhoenixRise", "Kim Min-su", "IGL", 4, "https://api.dicebear.com/7.x/bottts/svg?seed=PhoenixRise"),
        ("HealerQueen", "Sarah Connor", "Support", 5, "https://api.dicebear.com/7.x/bottts/svg?seed=HealerQueen"),
        ("SilentKill", "Emma White", "Scout", 5, "https://api.dicebear.com/7.x/bottts/svg?seed=SilentKill"),
        ("TitanShield", "Boris Novikov", "Support", 5, "https://api.dicebear.com/7.x/bottts/svg?seed=TitanShield"),
        ("ViperStrike", "Elena Rostova", "Attacker", 5, "https://api.dicebear.com/7.x/bottts/svg?seed=ViperStrike"),
        ("EagleEye", "Tom Hollander", "Sniper", 6, "https://api.dicebear.com/7.x/bottts/svg?seed=EagleEye"),
        ("AstroBoy", "Hiroshi Sato", "Scout", 6, "https://api.dicebear.com/7.x/bottts/svg?seed=AstroBoy"),
        ("NebulaX", "Sariel L.", "Support", 6, "https://api.dicebear.com/7.x/bottts/svg?seed=NebulaX"),
        ("Cyborg", "Adam West", "Flex", 7, "https://api.dicebear.com/7.x/bottts/svg?seed=Cyborg"),
        ("QuantumAim", "Lucas Silva", "Sniper", 7, "https://api.dicebear.com/7.x/bottts/svg?seed=QuantumAim"),
        ("ChronoShift", "Liam O'Connor", "IGL", 7, "https://api.dicebear.com/7.x/bottts/svg?seed=ChronoShift"),
        ("GhostRider", "Kevin Lopez", "Scout", 8, "https://api.dicebear.com/7.x/bottts/svg?seed=GhostRider"),
        ("Spectra", "Amira F.", "Flex", 8, "https://api.dicebear.com/7.x/bottts/svg?seed=Spectra"),
        ("VoidWalker", "Tariq M.", "Attacker", 8, "https://api.dicebear.com/7.x/bottts/svg?seed=VoidWalker"),
        ("PhantomX", "Maria Garcia", "IGL", 9, "https://api.dicebear.com/7.x/bottts/svg?seed=PhantomX"),
        ("Mirage", "Camille B.", "Scout", 9, "https://api.dicebear.com/7.x/bottts/svg?seed=Mirage"),
        ("Eclipse", "Ravi P.", "Support", 9, "https://api.dicebear.com/7.x/bottts/svg?seed=Eclipse"),
        ("NeonBlade", "Yuki Tanaka", "Flex", 10, "https://api.dicebear.com/7.x/bottts/svg?seed=NeonBlade"),
        ("Zephyr", "Sven Lindstrom", "Sniper", 10, "https://api.dicebear.com/7.x/bottts/svg?seed=Zephyr")
    ]
    c.executemany("INSERT INTO Players (ign, real_name, role, team_id, avatar_url) VALUES (?, ?, ?, ?, ?)", players_data)
    
    # 4. Gear_Inventory (20 รายการฮาร์ดแวร์และเกมมิ่งเกียร์)
    gears_data = [
        ("Logitech G PRO X SUPERLIGHT 2 DEX", "Mouse", "Logitech", 0, "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=150&auto=format&fit=crop&q=80"),
        ("Razer DeathAdder V3 Pro Smooth", "Mouse", "Razer", 12, "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=150&auto=format&fit=crop&q=80"),
        ("Wooting 60HE+ Magnetic Custom", "Keyboard", "Wooting", 8, "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=150&auto=format&fit=crop&q=80"),
        ("SteelSeries Apex Pro TKL 2026", "Keyboard", "SteelSeries", 10, "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=150&auto=format&fit=crop&q=80"),
        ("HyperX Cloud III Wireless Red", "Headset", "HyperX", 20, "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=150&auto=format&fit=crop&q=80"),
        ("Zowie XL2566K 360Hz DyAc⁺", "Monitor", "Zowie", 6, "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=150&auto=format&fit=crop&q=80"),
        ("Artisan Zero FX Soft XL Pad", "Mousepad", "Artisan", 25, "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=150&auto=format&fit=crop&q=80"),
        ("Lethal Gaming Gear Saturn Pro", "Mousepad", "LGG", 30, "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=150&auto=format&fit=crop&q=80"),
        ("ASUS ROG Swift Pro PG248QP 540Hz", "Monitor", "ASUS", 3, "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=150&auto=format&fit=crop&q=80"),
        ("Sennheiser IE 600 Audiophile IEM", "Headset", "Sennheiser", 10, "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=150&auto=format&fit=crop&q=80"),
        ("Pulsar X2V2 Premium Black Edition", "Mouse", "Pulsar", 14, "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=150&auto=format&fit=crop&q=80"),
        ("Lamzu Atlantis OG V2 4K Polling", "Mouse", "Lamzu", 11, "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=150&auto=format&fit=crop&q=80"),
        ("Razer BlackShark V2 Pro 2026", "Headset", "Razer", 18, "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=150&auto=format&fit=crop&q=80"),
        ("Corsair K70 RGB PRO OPX Switches", "Keyboard", "Corsair", 9, "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=150&auto=format&fit=crop&q=80"),
        ("Finalmouse UltralightX Lion Gold", "Mouse", "Finalmouse", 5, "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=150&auto=format&fit=crop&q=80"),
        ("Logitech G915 X TKL Wireless", "Keyboard", "Logitech", 12, "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=150&auto=format&fit=crop&q=80"),
        ("SteelSeries QcK Heavy XXL Cloth", "Mousepad", "SteelSeries", 40, "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=150&auto=format&fit=crop&q=80"),
        ("Alienware AW2524H 500Hz Fast IPS", "Monitor", "Alienware", 4, "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=150&auto=format&fit=crop&q=80"),
        ("Audeze QD-MAX Pro Gaming Headset", "Headset", "Audeze", 7, "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=150&auto=format&fit=crop&q=80"),
        ("Zowie U2 Wireless Esports Mouse", "Mouse", "Zowie", 16, "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=150&auto=format&fit=crop&q=80")
    ]
    c.executemany("INSERT INTO Gear_Inventory (item_name, category, brand, stock_qty, image_url) VALUES (?, ?, ?, ?, ?)", gears_data)
    
    # 5. Player_Gears (ตัวอย่างประวัติการถือครองอุปกรณ์)
    c.executemany("INSERT INTO Player_Gears (player_id, item_id, assigned_date) VALUES (?, ?, ?)", [
        (1, 1, "2026-01-10"), (1, 3, "2026-01-10"), (1, 7, "2026-02-01"),
        (2, 2, "2026-02-15"), (2, 6, "2026-02-15"), (3, 1, "2026-03-01")
    ])
    
    # 6. Tournaments (12 รายการแข่งขันระดับนานาชาติ)
    tourneys_data = [
        ("World Cyber Games 2026 Grand Finals", "PUBG Mobile", 3500000.0, "Ongoing"),
        ("FSPP Official Masters Challenge", "Valorant", 800000.0, "Upcoming"),
        ("Intel Extreme Masters Season VI", "CS2", 1500000.0, "Ongoing"),
        ("Valorant Champions Tour Seoul", "Valorant", 2250000.0, "Completed"),
        ("ESL Pro League Season 22 Summer", "CS2", 900000.0, "Ongoing"),
        ("PMGO Global Open 2026 Showdown", "PUBG Mobile", 500000.0, "Completed"),
        ("Apex Legends Global Series Split 2", "Apex Legends", 1000000.0, "Upcoming"),
        ("BLAST Premier Spring Showdown", "CS2", 600000.0, "Completed"),
        ("League of Legends Mid-Season Cup", "LoL", 2000000.0, "Ongoing"),
        ("Dota 2 Riyadh Masters 2026 Circuit", "Dota 2", 5000000.0, "Upcoming"),
        ("Overwatch Championship Series Show", "Overwatch", 400000.0, "Completed"),
        ("Rainbow Six Major Invitational Pro", "Rainbow Six", 750000.0, "Upcoming")
    ]
    c.executemany("INSERT INTO Tournaments (name, game_title, prize_pool, status) VALUES (?, ?, ?, ?)", tourneys_data)
    
    # 7. Match_Results
    c.executemany("INSERT INTO Match_Results (tourney_id, team_id, placement, kill_points) VALUES (?, ?, ?, ?)", [
        (1, 1, 1, 68), (1, 2, 3, 45), (2, 1, 2, 38), (3, 3, 1, 72)
    ])
    
    # 8. Sponsors (30 แบรนด์ผู้สนับสนุนสโมสร)
    sponsors_data = [
        ("Logitech G", "Title Sponsor", 2500000.0, "LOGITECH G EXCELLENCE"),
        ("ASUS ROG", "Title Sponsor", 2200000.0, "REPUBLIC OF GAMERS"),
        ("Intel Corporation", "Platinum", 3000000.0, "INTEL CORE ULTRA PROCESSORS"),
        ("Razer Inc.", "Gold Partner", 1500000.0, "FOR GAMERS. BY GAMERS."),
        ("Monster Energy", "Beverage Partner", 1200000.0, "UNLEASH THE BEAST"),
        ("Secretlab Chairs", "Silver Partner", 800000.0, "ULTIMATE GAMING SEATS"),
        ("Zowie BenQ Pro", "Hardware Partner", 1000000.0, "STRIVE FOR PERFECTION"),
        ("Nike Esports Gear", "Apparel Partner", 1800000.0, "JUST DO IT. GAMING"),
        ("Aim Lab Official", "Training Partner", 400000.0, "TRAIN LIKE A PRO"),
        ("Discord Nitro", "Community Partner", 600000.0, "IMAGINE A PLACE"),
        ("Red Bull Gaming", "Beverage Partner", 1100000.0, "GIVES YOU WINGS"),
        ("AMD Ryzen Processors", "Hardware Partner", 2000000.0, "TOGETHER WE ADVANCE_GAMING"),
        ("Corsair Gaming", "Gold Partner", 900000.0, "YOUR SETUP. COMMANDED."),
        ("SteelSeries Pro", "Hardware Partner", 850000.0, "FOR GLORY"),
        ("NVIDIA GeForce", "Platinum", 2800000.0, "THE ULTIMATE PLAY"),
        ("HyperX Excellence", "Silver Partner", 700000.0, "WE'RE ALL GAMERS"),
        ("Wooting Custom Keyboards", "Hardware Partner", 500000.0, "ANALOG ADVANTAGE"),
        ("Twitch Interactive", "Streaming Partner", 1300000.0, "YOU'RE ALREADY ONE OF US"),
        ("Puma Digital", "Apparel Partner", 950000.0, "FOREVER FASTER"),
        ("Mountain Dew", "Beverage Partner", 750000.0, "DO THE DEW"),
        ("Artisan Mousepads Japan", "Hardware Partner", 300000.0, "THE ART OF SLIDE"),
        ("Lethal Gaming Gear", "Hardware Partner", 250000.0, "GEAR FOR WINNERS"),
        ("G FUEL", "Beverage Partner", 650000.0, "THE ORIGINAL ENERGY DRINK"),
        ("Alienware PC Systems", "Platinum", 1900000.0, "DEFY BOUNDARIES"),
        ("Sennheiser Audio", "Audiophile Partner", 600000.0, "THE PURSUIT OF PERFECT SOUND"),
        ("Lamzu Esports", "Hardware Partner", 350000.0, "CREATE FOR EXTREME"),
        ("Pulsar Gaming Gears", "Hardware Partner", 400000.0, "BEYOND GAMING"),
        ("Finalmouse Lab", "Elite Partner", 1200000.0, "AIM IS AN ART"),
        ("Audeze Acoustic", "Audiophile Partner", 450000.0, "HEAR THE DIFFERENCE"),
        ("YouTube Gaming Hub", "Streaming Partner", 1600000.0, "BROADCAST YOUR PLAY")
    ]
    c.executemany("INSERT INTO Sponsors (sponsor_name, tier, investment_amt, logo_text) VALUES (?, ?, ?, ?)", sponsors_data)
    
    # 9. Games
    c.executemany("INSERT INTO Games (game_title, description, genre, icon_url) VALUES (?, ?, ?, ?)", [
        ("Valorant", "5v5 tactical hero shooter", "Tactical Shooter", "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=150&auto=format&fit=crop&q=80"),
        ("CS2", "Counter-Strike 2 competitive FPS", "FPS", "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=150&auto=format&fit=crop&q=80"),
        ("PUBG Mobile", "Battle Royale intense survival", "BR", "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=150&auto=format&fit=crop&q=80")
    ])
    
    # 10. Team_Games
    c.executemany("INSERT INTO Team_Games (team_id, game_id, primary_game) VALUES (?, ?, ?)", [
        (1, 1, 1), (1, 3, 1), (2, 2, 1), (3, 1, 0)
    ])
    
    # 11. Members (บรรจุพาร์ทเนอร์ตั้งต้น)
    members_data = [
        ("fspp_partner", "partner@fspp.com", hash_pw("Partner2026!"), "สมชาย พาร์ทเนอร์", "SuperAdmin", "2026-01-15", "https://api.dicebear.com/7.x/bottts/svg?seed=partner"),
        ("fspp_fanclub", "fan@fspp.com", hash_pw("Fanclub2026!"), "ปิติพันธ์ แฟนคลับ", "Member", "2026-02-01", "https://api.dicebear.com/7.x/bottts/svg?seed=fanclub")
    ]
    c.executemany("INSERT INTO Members (username, email, password_hash, full_name, member_role, join_date, avatar_url) VALUES (?, ?, ?, ?, ?, ?, ?)", members_data)
    
    # 12. Roles
    c.executemany("INSERT INTO Roles (role_name, description, permission_level) VALUES (?, ?, ?)", [
        ("SuperAdmin", "สิทธิ์ระดับผู้บริหารสูงสุด ควบคุมข้อมูลและแก้ไขสิทธิ์สมาชิกได้ทุกประการ", 100),
        ("Manager", "สิทธิ์ระดับผู้จัดการทีม สามารถจัดการรายชื่อนักแข่งและวางแผนทัวร์นาเมนต์", 80),
        ("InventoryAdmin", "สิทธิ์ระดับเจ้าหน้าที่ฝ่ายเทคนิค ควบคุมและสั่งจ่ายคลังอุปกรณ์ฮาร์ดแวร์", 60),
        ("Member", "สิทธิ์ระดับพาร์ทเนอร์ทั่วไปหรือแฟนคลับ เข้าถึงสารสนเทศสถิติการแข่งขัน", 20)
    ])
    
    conn.commit()
    conn.close()
    print("\n" + "=" * 60)
    print("✅ ฐานข้อมูลพร้อมใช้งานแล้ว!")
    print("=" * 60)

if __name__ == '__main__':
    initialize_database()