import pygame
import random
import math


pygame.init()
WIDTH, HEIGHT = 960, 540 #<-chỉnh giúp
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Gunsmith: The House v4.0")
clock = pygame.time.Clock()

# BẢNG MÀU THEO KHÔNG GIAN
BASEMENT_COLOR = (25, 25, 30)      # Tầng hầm tối, cơ khí
HOUSE_COLOR = (75, 55, 40)         # Nhà trên ấm áp, sàn gỗ
YARD_COLOR = (35, 50, 35)          # Sân sau bãi cỏ
UI_BG = (45, 50, 60)
WHITE, GRAY, BLACK = (240, 240, 240), (140, 145, 150), (15, 15, 20)
ACCENT = {"RED": (255, 60, 60), "GREEN": (50, 225, 100), "BLUE": (60, 160, 255), "GOLD": (245, 190, 40)}

font_sm = pygame.font.SysFont("Consolas", 14, bold=True)
font_md = pygame.font.SysFont("Consolas", 18, bold=True)
font_lg = pygame.font.SysFont("Consolas", 28, bold=True)


# MÃ HÓA CHUỖI PIXEL

COLORS = {"1": (60, 65, 70), "2": (105, 110, 115), "3": (170, 175, 180), "4": (25, 25, 30), "5": (130, 80, 40), "6": (255, 50, 50)}

SPRITES = {
    "REC_PISTOL": ["  3333333 ", " 222222222", " 111111111", "    441   ", "   555    ", "   555    "],
    "REC_SMG":    ["  33333333333  ", " 2222222222222 ", " 1111111111111 ", "      1114     ", "     1411      ", "     111       "],
    "REC_AR":     [" 4333333333333334 ", " 2222222222222222 ", " 1111111111111111 ", "        1111      ", "       1411       ", "       111        "],
    "BAR_SHORT":  ["3334", "2222", "1111"],
    "BAR_MED":    ["33333334", "22222222", "11111111"],
    "BAR_LONG":   ["4444444444", "3333333334", "2222222222", "1111111111"],
    "BAR_SIL":    ["44444444", "11111111", "11111111", "44444444"],
    "STK_NONE":   [" "],
    "STK_LIGHT":  ["4444 ", "1  4 ", "1  4 ", "4444 "],
    "STK_SOLID":  ["45555", "45555", "45555", " 444 "],
    "SCP_NONE":   [" "],
    "SCP_REDDOT": [" 444 ", " 464 ", " 111 "],
    "SCP_SNIPER": ["433334", "611116", "411114", " 4444 "],
    "MAG_SMALL":  ["11", "11", "11"],
    "MAG_LONG":   ["111", "111", " 111", "  111"],
    "MAG_DRUM":   [" 111 ", "11111", " 111 "]
}

def draw_sprite(surface, sprite_id, x, y, scale=4):
    if sprite_id not in SPRITES or SPRITES[sprite_id] == [" "]: return
    data = SPRITES[sprite_id]
    for row in range(len(data)):
        for col in range(len(data[row])):
            char = data[row][col]
            if char in COLORS:
                pygame.draw.rect(surface, COLORS[char], (x + col * scale, y + row * scale, scale, scale))

# id súng
PARTS = {
    "RECEIVER": [
        {"name": "Khung Pistol", "spr": "REC_PISTOL", "dmg": 18, "rate": 350, "acc": 65, "cost": 50, "bar_x": 9, "scp_x": 3, "mag_x": 4},
        {"name": "Khung SMG",    "spr": "REC_SMG",    "dmg": 22, "rate": 850, "acc": 55, "cost": 150, "bar_x": 13, "scp_x": 5, "mag_x": 5},
        {"name": "Khung Rifle",  "spr": "REC_AR",     "dmg": 38, "rate": 650, "acc": 78, "cost": 320, "bar_x": 16, "scp_x": 6, "mag_x": 7}
    ],
    "BARREL": [
        {"name": "Nòng Ngắn",    "spr": "BAR_SHORT",  "dmg": -3, "rate": 0, "acc": -5, "cost": 20, "y_off": 0},
        {"name": "Nòng Tiêu Chuẩn","spr": "BAR_MED",   "dmg": 5,  "rate": 0, "acc": 12, "cost": 60, "y_off": 0},
        {"name": "Nòng Dài Heavy", "spr": "BAR_LONG",  "dmg": 18, "rate": -40, "acc": 28, "cost": 130, "y_off": 0},
        {"name": "Ống Giảm Thanh", "spr": "BAR_SIL",   "dmg": -4, "rate": 10, "acc": 8,  "cost": 160, "y_off": 0}
    ],
    "STOCK": [
        {"name": "Không Báng",   "spr": "STK_NONE",   "dmg": 0, "rate": 0, "acc": -12, "cost": 0, "x_off": 0},
        {"name": "Báng Gấp Nhẹ", "spr": "STK_LIGHT",  "dmg": 0, "rate": 0, "acc": 18,  "cost": 60, "x_off": -4},
        {"name": "Báng Gỗ Cố Định","spr": "STK_SOLID",  "dmg": 2, "rate": 0, "acc": 40,  "cost": 120, "x_off": -5}
    ],
    "SCOPE": [
        {"name": "Thước Ngắm Cơ Bản","spr": "SCP_NONE",  "dmg": 0, "rate": 0, "acc": 0, "cost": 0, "type": "IRON"},
        {"name": "Kính Red Dot",   "spr": "SCP_REDDOT","dmg": 0, "rate": 0, "acc": 22, "cost": 90, "type": "REDDOT"},
        {"name": "Ống Ngắm Sniper", "spr": "SCP_SNIPER","dmg": 12,"rate": -30,"acc": 45, "cost": 220, "type": "SNIPER"}
    ],
    "MAG": [
        {"name": "Băng Tiêu Chuẩn", "spr": "MAG_SMALL", "cap": 15, "cost": 20},
        {"name": "Băng Kéo Dài",   "spr": "MAG_LONG",  "cap": 32, "cost": 70},
        {"name": "Hộp Đạn Tròn",   "spr": "MAG_DRUM",  "cap": 65, "cost": 190}
    ]
}

# TRẠNG THÁI HỆ THỐNG
current_room = "BASEMENT" # BASEMENT (Lắp), HOUSE (Đơn hàng), BACKYARD (Bắn thử)
money = 800
selections = {"RECEIVER": 0, "BARREL": 0, "STOCK": 0, "SCOPE": 0, "MAG": 0}
active_tab = "RECEIVER"

# HỆ THỐNG ĐƠN HÀNG (PRE-ORDERS) Ở PHÒNG KHÁCH
pre_orders = [
    {"client": "John Wick", "stat": "rate", "req": 700, "reward": 500, "desc": "Cần một khẩu SMG quét sạch phòng khép kín.", "done": False},
    {"client": "Thợ Săn Rừng", "stat": "dmg", "req": 50, "reward": 650, "desc": "Cần súng trường lực sát thương cực cao.", "done": False},
    {"client": "Đặc Nhiệm", "stat": "acc", "req": 85, "reward": 600, "desc": "Yêu cầu độ chính xác tuyệt đối để ám sát.", "done": False}
]

# CAMERA VÀ BẮN SÚNG (FPS ADS) Ở SÂN SAU
cam_x, cam_y = 500, 200
recoil_y = 0
recoil_x = 0
last_shot_time = 0
bullets = 15
bullet_holes = [] # Lưu (world_x, world_y)

WORLD_W, WORLD_H = 2000, 900
targets = [{"x": random.randint(200, WORLD_W-200), "y": random.randint(200, WORLD_H-300), "hp": 100, "vx": random.choice([-2, 2])} for _ in range(6)]

def get_gun_stats():
    r = PARTS["RECEIVER"][selections["RECEIVER"]]
    b = PARTS["BARREL"][selections["BARREL"]]
    st = PARTS["STOCK"][selections["STOCK"]]
    sc = PARTS["SCOPE"][selections["SCOPE"]]
    m = PARTS["MAG"][selections["MAG"]]
    
    dmg = max(5, r["dmg"] + b.get("dmg",0) + st.get("dmg",0) + sc.get("dmg",0))
    rate = max(60, r["rate"] + b.get("rate",0) + st.get("rate",0) + sc.get("rate",0))
    acc = min(100, max(15, r["acc"] + b.get("acc",0) + st.get("acc",0) + sc.get("acc",0)))
    val = r["cost"] + b["cost"] + st["cost"] + sc["cost"] + m["cost"]
    return {"dmg": dmg, "rate": rate, "acc": acc, "value": val, "cap": m["cap"]}

def render_gun_assembly(surface, cx, cy, scale=6):
    r = PARTS["RECEIVER"][selections["RECEIVER"]]
    b = PARTS["BARREL"][selections["BARREL"]]
    st = PARTS["STOCK"][selections["STOCK"]]
    sc = PARTS["SCOPE"][selections["SCOPE"]]
    m = PARTS["MAG"][selections["MAG"]]
    
    rx = cx - (len(SPRITES[r["spr"]][0]) * scale) // 2
    draw_sprite(surface, st["spr"], rx + st["x_off"] * scale, cy, scale)
    draw_sprite(surface, m["spr"], rx + r["mag_x"] * scale, cy + 3 * scale, scale)
    draw_sprite(surface, r["spr"], rx, cy, scale)
    draw_sprite(surface, b["spr"], rx + r["bar_x"] * scale, cy + b["y_off"] * scale, scale)
    draw_sprite(surface, sc["spr"], rx + r["scp_x"] * scale, cy - 3 * scale, scale)

def render_gun_fps_ads(surface, recoil_shift_x, recoil_shift_y):
    """Vẽ súng nằm dọc giữa màn hình tạo cảm giác ngắm bắn thật (ADS)"""
    r = PARTS["RECEIVER"][selections["RECEIVER"]]
    b = PARTS["BARREL"][selections["BARREL"]]
    st = PARTS["STOCK"][selections["STOCK"]]
    m = PARTS["MAG"][selections["MAG"]]
    
    scale = 14  # Phóng to súng lên vì ở ngay sát mắt
    cx = WIDTH // 2 + int(recoil_shift_x)
    cy = HEIGHT - 120 + int(recoil_shift_y)
    
    # Căn lề súng nằm dọc thẳng tắp ngay giữa tầm mắt
    rx = cx - (len(SPRITES[r["spr"]][0]) * scale) // 2
    
    # Vẽ các thành phần khuất phía dưới mặt (Không vẽ Scope vì mắt đang nhìn XUYÊN QUA ống ngắm)
    draw_sprite(surface, st["spr"], rx + st["x_off"] * scale, cy, scale)
    draw_sprite(surface, m["spr"], rx + r["mag_x"] * scale, cy + 2 * scale, scale)
    draw_sprite(surface, r["spr"], rx, cy, scale)
    draw_sprite(surface, b["spr"], rx + r["bar_x"] * scale, cy + b["y_off"] * scale, scale)

# GAME LOOP
running = True
is_touching = False
bullets = get_gun_stats()["cap"]

while running:
    mx, my = pygame.mouse.get_pos()
    click = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                is_touching = True
                click = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_touching = False

    # Khởi tạo khung hình
    game_surf = pygame.Surface((WIDTH, HEIGHT))
    stats = get_gun_stats()
    
    # Phục hồi độ giật dần dần theo thời gian
    recoil_y = max(0, recoil_y - 1.2)
    recoil_x *= 0.8

    
    # TẦNG HẦM: NƠI CHẾ TẠO SÚNG (BASEMENT)
    
    if current_room == "BASEMENT":
        game_surf.fill(BASEMENT_COLOR)
        # Lưới kỹ thuật kỹ sư
        for i in range(0, 500, 25): pygame.draw.line(game_surf, (40, 40, 50), (i, 0), (i, HEIGHT - 70))
        for i in range(0, HEIGHT - 70, 25): pygame.draw.line(game_surf, (40, 40, 50), (0, i), (500, i))
        
        game_surf.blit(font_lg.render("🔧 TẦNG HẦM: CHẾ TẠO", True, WHITE), (20, 20))
        game_surf.blit(font_md.render(f"NGÂN SÁCH: ${money}", True, ACCENT["GREEN"]), (20, 60))
        
        # Chỉ số vũ khí
        sy = HEIGHT - 210
        game_surf.blit(font_sm.render(f"SAT THUONG: {stats['dmg']}", True, ACCENT["RED"]), (20, sy))
        game_surf.blit(font_sm.render(f"TOC DO BAN: {stats['rate']} RPM", True, ACCENT["GOLD"]), (20, sy+22))
        game_surf.blit(font_sm.render(f"CHINH XAC:  {stats['acc']}%", True, ACCENT["BLUE"]), (20, sy+44))
        game_surf.blit(font_sm.render(f"GIÁ TRỊ SÚNG: ${stats['value']}", True, WHITE), (20, sy+70))

        render_gun_assembly(game_surf, 240, 200, scale=7)

        # Cửa hàng Menu bên phải linh kiện
        menu_x = 520
        pygame.draw.rect(game_surf, UI_BG, (menu_x, 15, 420, HEIGHT - 100), border_radius=8)
        
        tabs = ["RECEIVER", "BARREL", "STOCK", "SCOPE", "MAG"]
        tw = 400 // len(tabs)
        for i, t in enumerate(tabs):
            t_rect = pygame.Rect(menu_x + 10 + i*tw, 25, tw - 3, 35)
            c = ACCENT["BLUE"] if active_tab == t else (70, 75, 85)
            pygame.draw.rect(game_surf, c, t_rect, border_radius=4)
            game_surf.blit(font_sm.render(t[:3], True, WHITE), (t_rect.x + 8, t_rect.y + 10))
            if click and t_rect.collidepoint(mx, my): active_tab = t

        # Danh sách linh kiện mở rộng có ảnh thu nhỏ
        for i, item in enumerate(PARTS[active_tab]):
            i_rect = pygame.Rect(menu_x + 10, 75 + i*55, 400, 48)
            eq = (selections[active_tab] == i)
            pygame.draw.rect(game_surf, (30, 35, 45) if not eq else (60, 70, 90), i_rect, border_radius=4)
            
            draw_sprite(game_surf, item["spr"], menu_x + 20, 85 + i*55, scale=2)
            game_surf.blit(font_md.render(item["name"], True, WHITE), (menu_x + 85, 88 + i*55))
            
            if not eq:
                game_surf.blit(font_md.render(f"${item['cost']}", True, ACCENT["GOLD"]), (menu_x + 330, 88 + i*55))
            else:
                game_surf.blit(font_md.render("ON", True, ACCENT["GREEN"]), (menu_x + 350, 88 + i*55))
                
            if click and i_rect.collidepoint(mx, my):
                selections[active_tab] = i
                bullets = get_gun_stats()["cap"]

  
    # NHÀ TRÊN: BẢNG NHẬN ĐƠN HÀNG TRƯỚC (HOUSE)
    
    elif current_room == "HOUSE":
        game_surf.fill(HOUSE_COLOR)
        pygame.draw.rect(game_surf, (50, 35, 25), (40, 80, WIDTH-80, HEIGHT-180), border_radius=12) # Bảng gỗ treo tường
        
        game_surf.blit(font_lg.render("🏛️ PHÒNG KHÁCH: ĐƠN ĐẶT HÀNG TRƯỚC", True, ACCENT["GOLD"]), (60, 30))
        game_surf.blit(font_md.render(f"Quỹ cửa hàng: ${money}", True, WHITE), (60, 95))

        for i, order in enumerate(pre_orders):
            o_rect = pygame.Rect(60, 140 + i * 95, WIDTH - 120, 80)
            pygame.draw.rect(game_surf, (70, 55, 45) if not order["done"] else (40, 60, 45), o_rect, border_radius=6)
            
            # Text thông tin đơn hàng
            game_surf.blit(font_md.render(f"Khách hàng: {order['client']}", True, WHITE), (80, 150 + i*95))
            game_surf.blit(font_sm.render(order["desc"], True, GRAY), (80, 175 + i*95))
            
            # Yêu cầu kỹ thuật
            st_name = {"dmg": "Sát thương", "rate": "Tốc bắn (RPM)", "acc": "Chính xác (%)"}
            req_txt = f"Yêu cầu: {st_name[order['stat']]} >= {order['req']}"
            game_surf.blit(font_sm.render(req_txt, True, ACCENT["GOLD"]), (80, 195 + i*95))
            
            # Trạng thái kiểm tra súng hiện tại
            cur_val = stats[order["stat"]]
            qualified = cur_val >= order["req"]
            
            if not order["done"]:
                btn_rect = pygame.Rect(WIDTH - 240, 155 + i*95, 150, 50)
                btn_color = ACCENT["GREEN"] if qualified else GRAY
                pygame.draw.rect(game_surf, btn_color, btn_rect, border_radius=6)
                txt = "GIAO SÚNG" if qualified else "CHƯA ĐẠT"
                game_surf.blit(font_md.render(txt, True, BLACK), (btn_rect.x + 28, btn_rect.y + 15))
                game_surf.blit(font_md.render(f"+${order['reward']}", True, ACCENT["GREEN"]), (WIDTH - 340, 168 + i*95))
                
                if click and btn_rect.collidepoint(mx, my) and qualified:
                    money += order["reward"]
                    order["done"] = True
                    # Trả súng về trạng thái mặc định sau khi bán thành công
                    for k in selections: selections[k] = 0
            else:
                game_surf.blit(font_lg.render("ĐÃ HOÀN THÀNH", True, ACCENT["GREEN"]), (WIDTH - 280, 160 + i*95))

    # SÂN SAU: BÃI TẬP BẮN FPS THỰC THỤ (BACKYARD)
   
    elif current_room == "BACKYARD":
        # Điều khiển ngắm bắn: Vuốt/Kéo màn hình để dịch chuyển TÂM/CAMERA tự do
        if is_touching and mx < WIDTH - 160:
            rel = pygame.mouse.get_rel()
            cam_x = max(WIDTH//2, min(cam_x - rel[0], WORLD_W - WIDTH//2))
            cam_y = max(HEIGHT//2, min(cam_y - rel[1], WORLD_H - HEIGHT//2))
        else:
            pygame.mouse.get_rel() # Reset chuột

        # Áp dụng độ giật súng lên góc nhìn camera trực quan
        current_view_x = cam_x + recoil_x
        current_view_y = cam_y - recoil_y

        # Vẽ môi trường Sân sau
        game_surf.fill(YARD_COLOR)
        # Vẽ các đường ranh giới sân tập bắn
        for x in range(0, WORLD_W, 120):
            pygame.draw.line(game_surf, (28, 42, 28), (x - (current_view_x - WIDTH//2), 0), (x - (current_view_x - WIDTH//2), HEIGHT), 2)
        for y in range(0, WORLD_H, 120):
            pygame.draw.line(game_surf, (28, 42, 28), (0, y - (current_view_y - HEIGHT//2)), (WIDTH, y - (current_view_y - HEIGHT//2)), 2)

        # Vẽ lỗ đạn trên bia/tường theo tọa độ 
        for hx, hy in bullet_holes:
            sx = hx - (current_view_x - WIDTH//2)
            sy = hy - (current_view_y - HEIGHT//2)
            if 0 < sx < WIDTH and 0 < sy < HEIGHT:
                pygame.draw.circle(game_surf, (10, 10, 10), (int(sx), int(sy)), 4)
                pygame.draw.circle(game_surf, (70, 70, 70), (int(sx), int(sy)), 6, 1)

        # Cập nhật và vẽ các bia tập bắn di động
        for t in targets:
            t["x"] += t["vx"]
            if t["x"] < 150 or t["x"] > WORLD_W - 150: t["vx"] *= -1
            
            tx = t["x"] - (current_view_x - WIDTH//2)
            ty = t["y"] - (current_view_y - HEIGHT//2)
            
            if 0 < tx < WIDTH + 50 and 0 < ty < HEIGHT + 50:
                pygame.draw.rect(game_surf, (220, 225, 220), (tx-25, ty-35, 50, 70), border_radius=4)
                pygame.draw.circle(game_surf, ACCENT["RED"], (tx, ty), 16)
                pygame.draw.circle(game_surf, WHITE, (tx, ty), 7)

        # KHAI HỎA (Bắn ngay giữa tâm màn hình)
        fire_btn = pygame.Rect(WIDTH - 140, HEIGHT - 220, 110, 110)
        pygame.draw.circle(game_surf, UI_BG, fire_btn.center, 55)
        pygame.draw.circle(game_surf, ACCENT["RED"], fire_btn.center, 45)
        game_surf.blit(font_md.render("FIRE", True, WHITE), (fire_btn.centerx - 20, fire_btn.centery - 10))

        now = pygame.time.get_ticks()
        shoot_trigger = is_touching and fire_btn.collidepoint(mx, my)
        
        if shoot_trigger and bullets > 0:
            if now - last_shot_time > (60000 / stats["rate"]):
                bullets -= 1
                last_shot_time = now
                
                # Tính toán lực giật camera + súng nảy lên
                recoil_y += 18
                recoil_x += random.choice([-6, 6])
                
                # Độ lệnh đạn (Spread) dựa trên độ chính xác lắp ráp
                spread = max(0, (100 - stats["acc"]) // 2)
                hit_w_x = current_view_x + random.randint(-spread, spread)
                hit_w_y = current_view_y + random.randint(-spread, spread)
                
                # Xử lý bắn trúng bia
                hit_any = False
                for t in targets:
                    if math.hypot(hit_w_x - t["x"], hit_w_y - t["y"]) < 20:
                        hit_any = True
                        t["x"] = random.randint(200, WORLD_W - 200) # Reset bia ra chỗ khác
                        break
                if not hit_any:
                    bullet_holes.append((hit_w_x, hit_w_y)) # Để lại lỗ đạn

        # VẼ KHẨU SÚNG DỌC GIỮA MÀN HÌNH (GÓC NHÌN ADS THẬT SỰ)
        render_gun_fps_ads(game_surf, recoil_x * 0.5, recoil_y * 0.4)

        # HỆ THỐNG KÍNH NGẮM DỰA TRÊN LINK KIỆN ĐÃ CHỌN
        sc_type = PARTS["SCOPE"][selections["SCOPE"]]["type"]
        cx, cy = WIDTH // 2, HEIGHT // 2
        
        if sc_type == "IRON": # Thước ngắm cơ khí cơ bản
            pygame.draw.line(game_surf, BLACK, (cx - 10, cy + 20), (cx, cy), 3)
            pygame.draw.line(game_surf, BLACK, (cx + 10, cy + 20), (cx, cy), 3)
            pygame.draw.circle(game_surf, ACCENT["RED"], (cx, cy), 2)
        elif sc_type == "REDDOT": # Kính Reddot tầm gần
            pygame.draw.circle(game_surf, (40, 45, 55), (cx, cy), 45, 6)
            pygame.draw.circle(game_surf, ACCENT["RED"], (cx, cy), 4)
        elif sc_type == "SNIPER": # Kính Ngắm Bắn Tỉa Toàn Màn Hình
            # Che mờ xung quanh ngoài ống kính ngắm sniper
            scope_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            scope_mask.fill((0, 0, 0, 200))
            pygame.draw.circle(scope_mask, (0, 0, 0, 0), (cx, cy), 130) # Lỗ ngắm trong suốt
            game_surf.blit(scope_mask, (0, 0))
            
            # Khung viền thép ống ngắm & Vạch dấu thập ngắm Mil-dot
            pygame.draw.circle(game_surf, BLACK, (cx, cy), 130, 8)
            pygame.draw.line(game_surf, BLACK, (cx - 130, cy), (cx + 130, cy), 2)
            pygame.draw.line(game_surf, BLACK, (cx, cy - 130), (cx, cy + 130), 2)
            pygame.draw.circle(game_surf, ACCENT["GREEN"], (cx, cy), 3)

        # UI Bổ Trợ Cho Mobile Sân Sau
        game_surf.blit(font_lg.render(f"AMMO: {bullets}/{stats['cap']}", True, WHITE), (30, HEIGHT - 150))
        game_surf.blit(font_sm.render("Vuốt nửa trái để xoay góc ngắm FPS", True, GRAY), (30, HEIGHT - 105))
        
        # Nút thay đạn nhanh
        re_btn = pygame.Rect(30, HEIGHT - 200, 110, 40)
        pygame.draw.rect(game_surf, UI_BG, re_btn, border_radius=4)
        game_surf.blit(font_md.render("RELOAD", True, WHITE), (50, HEIGHT - 190))
        if click and re_btn.collidepoint(mx, my): bullets = stats["cap"]

    # KHÔNG GIAN DI CHUYỂN TOÀN NHÀ (NAV BAR DƯỚI)
    
    nav_y = HEIGHT - 65
    pygame.draw.rect(game_surf, (35, 40, 45), (0, nav_y, WIDTH, 65))
    
    rooms = [("BASEMENT", "🔧 TẦNG HẦM (RÁP)"), ("HOUSE", "🏛️ TRÊN NHÀ (ĐƠN)"), ("BACKYARD", "🎯 SÂN SAU (FPS)")]
    bw = WIDTH // 3
    for i, (room_id, name) in enumerate(rooms):
        r_rect = pygame.Rect(i*bw, nav_y, bw, 65)
        if click and r_rect.collidepoint(mx, my):
            current_room = room_id
            if room_id == "BACKYARD": bullets = stats["cap"]
            
        is_cur = (current_room == room_id)
        tc = ACCENT["GOLD"] if is_cur else WHITE
        game_surf.blit(font_md.render(name, True, tc), (i*bw + bw//2 - 90, nav_y + 22))
        if i > 0: pygame.draw.line(game_surf, BLACK, (i*bw, nav_y), (i*bw, HEIGHT), 2)

    screen.blit(game_surf, (0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
