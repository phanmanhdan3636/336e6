import pygame
import math
import random
import time
import sys

# ==========================================
# KHỞI TẠO VÀ ĐỊNH NGHĨA KÍCH THƯỚC MÀN HÌNH MẢO
# ==========================================
pygame.init()

# Kích thước ảo (Virtual Resolution) để render mượt mà trên di động
V_WIDTH, V_HEIGHT = 854, 480 

# Lấy thông số màn hình thực tế của thiết bị
info = pygame.display.Info()
REAL_WIDTH = info.current_w if info.current_w > 0 else 854
REAL_HEIGHT = info.current_h if info.current_h > 0 else 480

# Chạy Fullscreen trên Android, chạy cửa sổ trên PC để dễ debug
is_android = "android" in sys.platform or hasattr(sys, "getandroidsdk")
if is_android:
    screen = pygame.display.set_mode((REAL_WIDTH, REAL_HEIGHT), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode((REAL_WIDTH, REAL_HEIGHT)) # test trên PC

pygame.display.set_caption("Gunsmith FPS Android - Highly Optimized")
clock = pygame.time.Clock()

# Bề mặt trung gian để vẽ game (Virtual Screen)
virtual_screen = pygame.Surface((V_WIDTH, V_HEIGHT)).convert()

# ==========================================
# BẢNG MÀU SẮC CHUẨN PIXEL
# ==========================================
WHITE = (255, 255, 255)
BLACK = (10, 10, 15)
RED = (220, 50, 50)
GREEN = (50, 220, 50)
BLUE = (50, 150, 250)
YELLOW = (255, 215, 0)
GRAY = (120, 120, 130)
DARK_GRAY = (40, 40, 45)
BROWN = (139, 90, 43)
GOLD = (255, 193, 7)
SKY_BLUE = (100, 160, 220)
GROUND_COLOR = (70, 95, 50)

# Trạng thái game
STATE_MENU = 0
STATE_ASSEMBLY = 1
STATE_PLAYING = 2
STATE_GAMEOVER = 3

# ==========================================
# CƠ SỞ DỮ LIỆU LINH KIỆN SÚNG (PARTS DATABASE)
# ==========================================
PARTS_DB = {
    "receiver": [
        {"id": "rec_pistol", "name": "Thân Pistol", "dmg": 18, "fire_rate": 0.4, "reload": 1.2, "acc": 0.8, "mag": 0, "color": GRAY},
        {"id": "rec_smg", "name": "Thân SMG", "dmg": 14, "fire_rate": 0.08, "reload": 1.8, "acc": 0.62, "mag": 0, "color": DARK_GRAY},
        {"id": "rec_sniper", "name": "Thân Sniper", "dmg": 75, "fire_rate": 1.6, "reload": 2.8, "acc": 0.96, "mag": 0, "color": BROWN}
    ],
    "barrel": [
        {"id": "br_short", "name": "Nòng Ngắn", "dmg": -2, "fire_rate": -0.04, "reload": -0.15, "acc": -0.08, "mag": 0, "color": GRAY},
        {"id": "br_long", "name": "Nòng Dài", "dmg": 6, "fire_rate": 0.08, "reload": 0.15, "acc": 0.18, "mag": 0, "color": BLACK},
        {"id": "br_silencer", "name": "Giảm Thanh", "dmg": -4, "fire_rate": 0, "reload": 0, "acc": 0.08, "mag": 0, "color": DARK_GRAY}
    ],
    "stock": [
        {"id": "st_none", "name": "Không Báng", "dmg": 0, "fire_rate": 0, "reload": -0.2, "acc": -0.18, "mag": 0, "color": BLACK},
        {"id": "st_wood", "name": "Báng Gỗ Cổ Điển", "dmg": 0, "fire_rate": 0, "reload": 0.2, "acc": 0.14, "mag": 0, "color": BROWN},
        {"id": "st_tactical", "name": "Báng Gấp", "dmg": 0, "fire_rate": -0.03, "reload": 0.08, "acc": 0.22, "mag": 0, "color": DARK_GRAY}
    ],
    "grip": [
        {"id": "gr_standard", "name": "Tay Cầm Thường", "dmg": 0, "fire_rate": 0, "reload": 0, "acc": 0.05, "mag": 0, "color": BLACK},
        {"id": "gr_vertical", "name": "Tay Cầm Dọc", "dmg": 0, "fire_rate": -0.04, "reload": 0.08, "acc": 0.16, "mag": 0, "color": GRAY}
    ],
    "mag": [
        {"id": "mg_small", "name": "Băng Đạn Nhỏ", "dmg": 0, "fire_rate": 0, "reload": -0.4, "acc": 0, "mag": 10, "color": GRAY},
        {"id": "mg_extended", "name": "Băng Mở Rộng", "dmg": 0, "fire_rate": 0, "reload": 0.4, "acc": -0.02, "mag": 30, "color": BLACK},
        {"id": "mg_drum", "name": "Băng Trống Sấy", "dmg": 0, "fire_rate": 0.05, "reload": 1.2, "acc": -0.06, "mag": 55, "color": DARK_GRAY}
    ],
    "scope": [
        {"id": "sc_iron", "name": "Đầu Ruồi", "dmg": 0, "fire_rate": 0, "reload": 0, "acc": 0.05, "mag": 0, "color": BLACK},
        {"id": "sc_reddot", "name": "Kính Ngắm Red-Dot", "dmg": 0, "fire_rate": -0.03, "reload": 0, "acc": 0.15, "mag": 0, "color": RED},
        {"id": "sc_x8", "name": "Ống Ngắm X8", "dmg": 0, "fire_rate": 0.15, "reload": 0.15, "acc": 0.38, "mag": 0, "color": BLACK}
    ]
}

def generate_random_part(type_filter=None):
    ptype = type_filter if type_filter else random.choice(list(PARTS_DB.keys()))
    part_data = random.choice(PARTS_DB[ptype])
    return {"type": ptype, **part_data}

def get_loot_color(part_type):
    colors = {"receiver": GOLD, "barrel": GRAY, "stock": BROWN, "grip": DARK_GRAY, "mag": BLUE, "scope": RED}
    return colors.get(part_type, WHITE)

# ==========================================
# LỚP TOUCH HỖ TRỢ ĐA ĐIỂM (MULTI-TOUCH EVENT)
# ==========================================
class TouchInput:
    def __init__(self, finger_id, vx, vy):
        self.id = finger_id
        self.start_vx = vx # Điểm chạm ban đầu
        self.start_vy = vy
        self.vx = vx       # Tọa độ hiện tại
        self.vy = vy
        self.dx = 0.0      # Lượng dịch chuyển frame này
        self.dy = 0.0

# ==========================================
# ĐỐI TƯỢNG HỆ THỐNG SÚNG & NHÂN VẬT
# ==========================================
class Gun:
    def __init__(self):
        self.parts = {
            "receiver": PARTS_DB["receiver"][0],
            "barrel": PARTS_DB["barrel"][0],
            "stock": PARTS_DB["stock"][0],
            "grip": PARTS_DB["grip"][0],
            "mag": PARTS_DB["mag"][0],
            "scope": PARTS_DB["scope"][0]
        }
        self.surf = pygame.Surface((220, 150), pygame.SRCALPHA).convert_alpha()
        self.update_stats()
        self.current_ammo = self.mag
        self.last_shot_time = 0
        self.is_reloading = False
        self.reload_start_time = 0
        self.recoil_offset = 0

    def update_stats(self):
        # Tính toán lại chỉ số dựa trên 6 loại linh kiện
        self.dmg = 0
        self.fire_rate = 0
        self.reload = 0
        self.acc = 0
        self.mag = 0
        for p in self.parts.values():
            if p:
                self.dmg += p["dmg"]
                self.fire_rate += p["fire_rate"]
                self.reload += p["reload"]
                self.acc += p["acc"]
                self.mag += p["mag"]
        
        # Giới hạn an toàn tránh lỗi chia 0
        self.dmg = max(1, self.dmg)
        self.fire_rate = max(0.05, self.fire_rate)
        self.reload = max(0.4, self.reload)
        self.acc = max(0.1, min(1.0, self.acc))
        self.mag = max(1, self.mag)
        
        # RENDERING CACHE: Vẽ sẵn súng vào Surface tĩnh để tăng hiệu năng tối đa
        self.surf.fill((0, 0, 0, 0)) # Clear trong suốt
        x, y = 30, 40
        
        # Vẽ các thành phần của súng lên cache surface
        if self.parts["stock"] and "none" not in self.parts["stock"]["id"]:
            pygame.draw.rect(self.surf, self.parts["stock"]["color"], (x + 95, y + 5, 50, 25), border_radius=3)
        pygame.draw.rect(self.surf, self.parts["receiver"]["color"], (x, y, 100, 35), border_radius=2)
        if self.parts["barrel"]:
            bw = 50 if "long" in self.parts["barrel"]["id"] else 25
            pygame.draw.rect(self.surf, self.parts["barrel"]["color"], (x - bw, y + 5, bw, 15), border_radius=1)
        if self.parts["grip"]:
            pygame.draw.rect(self.surf, self.parts["grip"]["color"], (x + 20, y + 35, 18, 35), border_radius=2)
        if self.parts["mag"]:
            mh = 45 if "extended" in self.parts["mag"]["id"] else 25
            pygame.draw.rect(self.surf, self.parts["mag"]["color"], (x + 55, y + 35, 22, mh), border_radius=2)
        if self.parts["scope"]:
            pygame.draw.rect(self.surf, self.parts["scope"]["color"], (x + 30, y - 15, 35, 15), border_radius=2)

    def shoot(self, current_time):
        if self.is_reloading: return False
        if self.current_ammo <= 0:
            self.start_reload(current_time)
            return False
        if current_time - self.last_shot_time >= self.fire_rate:
            self.current_ammo -= 1
            self.last_shot_time = current_time
            self.recoil_offset = 30 # Tạo độ giật (Recoil animation)
            return True
        return False

    def start_reload(self, current_time):
        if not self.is_reloading and self.current_ammo < self.mag:
            self.is_reloading = True
            self.reload_start_time = current_time

    def update(self, current_time, dt):
        if self.is_reloading:
            if current_time - self.reload_start_time >= self.reload:
                self.current_ammo = self.mag
                self.is_reloading = False
        if self.recoil_offset > 0:
            self.recoil_offset -= 180 * dt
            if self.recoil_offset < 0: self.recoil_offset = 0

class Player:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0 # Chiều cao mắt camera (để làm hiệu ứng nhún chân dập dềnh)
        self.z = 0.0
        self.yaw = 0.0   # Góc quay Trái / Phải
        self.pitch = 0.0 # Góc quay Lên / Xuống
        self.health = 100
        self.max_health = 100
        self.speed = 4.5
        self.gun = Gun()
        # Khởi đầu game tặng 5 món đồ trong hòm đồ
        self.inventory = [generate_random_part() for _ in range(5)]

# ==========================================
# THIẾT KẾ ĐỒ HỌA GIẢ LẬP 3D SPRITE SCALING (NO RAYCASTING)
# ==========================================
FOV = V_WIDTH / 1.4

def project_3d_to_2d(x, y, z, px, py, pz, yaw, pitch):
    # Di chuyển hệ trục về tâm Camera
    dx = x - px
    dy = y - py
    dz = z - pz

    # Xoay theo trục Yaw
    cos_yaw = math.cos(-yaw)
    sin_yaw = math.sin(-yaw)
    rx = dx * cos_yaw - dz * sin_yaw
    rz = dx * sin_yaw + dz * cos_yaw

    if rz <= 0.2: # Vật thể nằm phía sau Camera -> Không render
        return None

    # Phép chiếu phối cảnh Perspective Projection
    scale = FOV / rz
    screen_x = V_WIDTH / 2 + rx * scale
    screen_y = V_HEIGHT / 2 - dy * scale + (pitch * 240) # Ảnh hưởng bởi Pitch lên xuống

    return screen_x, screen_y, scale, rz

class Sprite3D:
    def __init__(self, x, y, z, size, type_id):
        self.x = x
        self.y = y
        self.z = z
        self.size = size
        self.type_id = type_id
        self.dist_to_player = 0.0
        self.active = True

class Enemy(Sprite3D):
    def __init__(self, x, z):
        super().__init__(x, 0.4, z, 1.4, "enemy")
        self.hp = 45
        self.max_hp = 45
        self.speed = 1.6
        self.attack_cooldown = 1.2
        self.last_attack_time = 0.0
        self.color = random.choice([(220, 50, 50), (240, 100, 50), (200, 40, 90)])
        self.bob_timer = random.uniform(0, 5.0)

    def update(self, px, pz, dt, player, current_time):
        if self.hp <= 0: return

        # AI tìm đường đến Player
        dx = px - self.x
        dz = pz - self.z
        dist = math.hypot(dx, dz)
        
        # Hiệu ứng nhấp nhô của quái khi chạy (Animation)
        self.bob_timer += dt * 6
        self.y = 0.4 + math.sin(self.bob_timer) * 0.08

        if dist > 1.2:
            self.x += (dx / dist) * self.speed * dt
            self.z += (dz / dist) * self.speed * dt
        else:
            # Gây sát thương khi áp sát Player
            if current_time - self.last_attack_time >= self.attack_cooldown:
                player.health -= 8
                self.last_attack_time = current_time

class Loot(Sprite3D):
    def __init__(self, x, z, part_data):
        super().__init__(x, -0.2, z, 0.45, "loot")
        self.part_data = part_data
        self.bob_timer = 0.0

    def update(self, dt):
        self.bob_timer += dt * 4.0
        self.y = -0.25 + math.sin(self.bob_timer) * 0.08

class Particle3D(Sprite3D):
    def __init__(self, x, y, z, vx, vy, vz, color, life):
        super().__init__(x, y, z, 0.15, "particle")
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.color = color
        self.life = life
        self.max_life = life

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        self.vy -= 4.5 * dt # Lực hấp dẫn kéo hạt rơi xuống đất
        self.life -= dt
        if self.life <= 0:
            self.active = False

# ==========================================
# LỚP ĐIỀU KHIỂN CHÍNH (GAME CONTROLLER)
# ==========================================
class Game:
    def __init__(self):
        self.state = STATE_MENU
        
        # Nạp font an toàn (None đảm bảo chạy trên mọi máy tính và điện thoại không bị lỗi thiếu file font)
        self.font_large = pygame.font.Font(None, 60)
        self.font_mid = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 20)
        self.font_tiny = pygame.font.Font(None, 16)

        self.player = Player()
        self.entities = []
        self.particles = []
        
        self.score = 0
        self.screen_shake = 0.0

        # Lưu trữ trạng thái ngón tay chạm màn hình (Multi-touch)
        self.active_touches = {}
        
        # Trạng thái điều khiển tay
        self.joystick_touch_id = None
        self.look_touch_id = None
        
        # Tọa độ vật lý Joystick ảo
        self.joy_x, self.joy_y = 120, V_HEIGHT - 120
        self.joy_radius = 55
        self.joy_knob_x, self.joy_knob_y = self.joy_x, self.joy_y
        self.joy_dir_x, self.joy_dir_y = 0.0, 0.0

        # Bố cục nút bấm trên Mobile (Tọa độ ảo 854x480)
        self.btn_shoot = pygame.Rect(V_WIDTH - 140, V_HEIGHT - 140, 90, 90)
        self.btn_reload = pygame.Rect(V_WIDTH - 125, V_HEIGHT - 240, 60, 60)
        self.btn_bag = pygame.Rect(V_WIDTH - 90, 20, 70, 45)

        # Trạng thái tự động xả đạn khi giữ đè nút bắn
        self.is_holding_shoot = False

        # Khởi tạo quái ban đầu
        for _ in range(6):
            self.spawn_enemy()

        # PRE-RENDER CACHE: Tăng hiệu năng vẽ Enemy, tối ưu hóa FPS cho điện thoại
        self.enemy_cache_surf = pygame.Surface((64, 64), pygame.SRCALPHA).convert_alpha()
        self._build_enemy_texture(self.enemy_cache_surf, RED)

    def _build_enemy_texture(self, surf, color):
        w, h = surf.get_size()
        # Thân chính của quái pixel
        pygame.draw.rect(surf, color, (w//4, h//4, w//2, h//2), border_radius=4)
        # Viền đen sắc nét
        pygame.draw.rect(surf, BLACK, (w//4, h//4, w//2, h//2), 3, border_radius=4)
        # Mắt trái mắt phải
        pygame.draw.rect(surf, WHITE, (w//4 + w//16, h//4 + h//8, w//8, h//8))
        pygame.draw.rect(surf, WHITE, (w//4 + w*5//16, h//4 + h//8, w//8, h//8))
        pygame.draw.rect(surf, RED, (w//4 + w//16 + 2, h//4 + h//8 + 2, 4, 4))
        pygame.draw.rect(surf, RED, (w//4 + w*5//16 + 2, h//4 + h//8 + 2, 4, 4))
        # Chân nhún
        pygame.draw.rect(surf, DARK_GRAY, (w//4 + 4, h*3//4 - 4, w//6, h//5), border_radius=2)
        pygame.draw.rect(surf, DARK_GRAY, (w*2//3 - 8, h*3//4 - 4, w//6, h//5), border_radius=2)

    def spawn_enemy(self):
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(12.0, 28.0)
        ex = self.player.x + math.cos(angle) * dist
        ez = self.player.z + math.sin(angle) * dist
        self.entities.append(Enemy(ex, ez))

    # ==========================================
    # HỆ THỐNG PHÂN PHỐI SỰ KIỆN TOUCH VÀ MOUSE DUAL-INPUT
    # ==========================================
    def process_inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # 1. HỆ THỐNG XỬ LÝ SỰ KIỆN ĐA ĐIỂM TRÊN ANDROID (TOUCH API)
            if event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
                # Chuyển đổi tọa độ Touch chuẩn hóa (0.0 -> 1.0) sang hệ tọa độ màn hình ảo V_WIDTH/V_HEIGHT
                vx = event.x * V_WIDTH
                vy = event.y * V_HEIGHT
                v_dx = event.dx * V_WIDTH
                v_dy = event.dy * V_HEIGHT

                if event.type == pygame.FINGERDOWN:
                    self.handle_touch_down(event.finger_id, vx, vy)
                elif event.type == pygame.FINGERMOTION:
                    self.handle_touch_move(event.finger_id, vx, vy, v_dx, v_dy)
                elif event.type == pygame.FINGERUP:
                    self.handle_touch_up(event.finger_id, vx, vy)

            # 2. HỆ THỐNG GIẢ LẬP ĐỂ TEST TRÊN PC BẰNG CHUỘT
            elif not is_android:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Chuột trái
                        vx = (event.pos[0] / REAL_WIDTH) * V_WIDTH
                        vy = (event.pos[1] / REAL_HEIGHT) * V_HEIGHT
                        self.handle_touch_down(-1, vx, vy)
                
                elif event.type == pygame.MOUSEMOTION:
                    if event.buttons[0]: # Đang rê chuột trái
                        vx = (event.pos[0] / REAL_WIDTH) * V_WIDTH
                        vy = (event.pos[1] / REAL_HEIGHT) * V_HEIGHT
                        v_dx = (event.rel[0] / REAL_WIDTH) * V_WIDTH
                        v_dy = (event.rel[1] / REAL_HEIGHT) * V_HEIGHT
                        self.handle_touch_move(-1, vx, vy, v_dx, v_dy)
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        vx = (event.pos[0] / REAL_WIDTH) * V_WIDTH
                        vy = (event.pos[1] / REAL_HEIGHT) * V_HEIGHT
                        self.handle_touch_up(-1, vx, vy)

    def handle_touch_down(self, fid, vx, vy):
        # Lưu chạm vào danh sách đang hoạt động
        self.active_touches[fid] = TouchInput(fid, vx, vy)

        if self.state == STATE_MENU:
            self.state = STATE_ASSEMBLY
            return

        if self.state == STATE_GAMEOVER:
            self.__init__() # Restart game
            return

        if self.state == STATE_ASSEMBLY:
            # Click trong màn hình Assembly
            # Nút VÀO MAP
            btn_play = pygame.Rect(V_WIDTH - 150, V_HEIGHT - 65, 130, 45)
            if btn_play.collidepoint(vx, vy):
                self.state = STATE_PLAYING
                self.reset_controls()
                return

            # Kiểm tra chạm trang bị linh kiện trong Kho đồ
            inv_x, inv_y = 40, 90
            for i, item in enumerate(self.player.inventory):
                row = i // 5
                col = i % 5
                bx = inv_x + col * 85
                by = inv_y + row * 85
                if bx <= vx <= bx + 75 and by <= vy <= by + 75:
                    # Hoán đổi linh kiện đang đeo với linh kiện trong kho
                    ptype = item["type"]
                    equipped = self.player.gun.parts[ptype]
                    self.player.gun.parts[ptype] = item
                    self.player.inventory.remove(item)
                    if equipped:
                        self.player.inventory.append(equipped)
                    self.player.gun.update_stats()
                    break
            return

        if self.state == STATE_PLAYING:
            # Kiểm tra chạm vào các nút điều khiển
            if self.btn_shoot.collidepoint(vx, vy):
                self.is_holding_shoot = True
                self.try_shoot()
                return

            if self.btn_reload.collidepoint(vx, vy):
                self.player.gun.start_reload(time.time())
                return

            if self.btn_bag.collidepoint(vx, vy):
                self.state = STATE_ASSEMBLY
                return

            # Nếu chạm vào vùng bên trái -> Kích hoạt Joystick di chuyển
            if vx < V_WIDTH / 2:
                if self.joystick_touch_id is None:
                    dist = math.hypot(vx - self.joy_x, vy - self.joy_y)
                    if dist < self.joy_radius + 40: # Cho phép nhấp lệch một xíu vẫn kích hoạt
                        self.joystick_touch_id = fid
                        self.update_joystick_pos(vx, vy)
            # Nếu chạm vào vùng bên phải -> Quay Camera góc nhìn
            else:
                if self.look_touch_id is None:
                    self.look_touch_id = fid

    def handle_touch_move(self, fid, vx, vy, dx, dy):
        if fid not in self.active_touches: return
        touch = self.active_touches[fid]
        touch.vx, touch.vy = vx, vy
        touch.dx, touch.dy = dx, dy

        if self.state == STATE_PLAYING:
            # Cập nhật kéo dãn ngón tay của Joystick
            if fid == self.joystick_touch_id:
                self.update_joystick_pos(vx, vy)
            
            # Xoay Camera nhạy bén mượt mà không giật lắc
            elif fid == self.look_touch_id:
                # 0.004 là hệ số nhạy cảm ứng phù hợp cho vuốt màn hình
                self.player.yaw += dx * 0.005
                self.player.pitch -= dy * 0.005
                # Giới hạn góc nhìn lên xuống không vượt quá đỉnh/đất
                self.player.pitch = max(-1.2, min(1.2, self.player.pitch))

    def handle_touch_up(self, fid, vx, vy):
        if fid in self.active_touches:
            del self.active_touches[fid]

        if fid == self.joystick_touch_id:
            self.joystick_touch_id = None
            self.joy_knob_x, self.joy_knob_y = self.joy_x, self.joy_y
            self.joy_dir_x, self.joy_dir_y = 0.0, 0.0

        if fid == self.look_touch_id:
            self.look_touch_id = None

        # Thả ngón tay khỏi nút bắn -> dừng bắn tự động
        if self.is_holding_shoot:
            # Kiểm tra xem có còn ngón tay nào đè nút bắn không
            still_holding = False
            for t_id, touch in self.active_touches.items():
                if self.btn_shoot.collidepoint(touch.vx, touch.vy):
                    still_holding = True
                    break
            if not still_holding:
                self.is_holding_shoot = False

    def reset_controls(self):
        self.active_touches.clear()
        self.joystick_touch_id = None
        self.look_touch_id = None
        self.joy_knob_x, self.joy_knob_y = self.joy_x, self.joy_y
        self.joy_dir_x, self.joy_dir_y = 0.0, 0.0
        self.is_holding_shoot = False

    def update_joystick_pos(self, vx, vy):
        dx = vx - self.joy_x
        dy = vy - self.joy_y
        dist = math.hypot(dx, dy)
        if dist <= self.joy_radius:
            self.joy_knob_x = vx
            self.joy_knob_y = vy
        else:
            angle = math.atan2(dy, dx)
            self.joy_knob_x = self.joy_x + math.cos(angle) * self.joy_radius
            self.joy_knob_y = self.joy_y + math.sin(angle) * self.joy_radius

        self.joy_dir_x = (self.joy_knob_x - self.joy_x) / self.joy_radius
        self.joy_dir_y = (self.joy_knob_y - self.joy_y) / self.joy_radius

    # ==========================================
    # LOGIC CỦA GAME (GAMEPLAY & PHYSICS LOOPS)
    # ==========================================
    def try_shoot(self):
        t = time.time()
        if self.player.gun.shoot(t):
            self.screen_shake = 5.0 # Tạo độ rung màn hình dữ dội cho chân thực
            
            # Tính độ lệch đường đạn (Spread) theo thông số độ chính xác súng (Gun Accuracy)
            spread = (1.0 - self.player.gun.acc) * 75
            hit_x = V_WIDTH/2 + random.uniform(-spread, spread)
            hit_y = V_HEIGHT/2 + random.uniform(-spread, spread)

            # Tìm quái vật trúng đạn gần nhất hướng ngắm
            hit_enemy = None
            closest_dist = 9999.0
            
            for ent in self.entities:
                if isinstance(ent, Enemy) and ent.hp > 0:
                    proj = project_3d_to_2d(ent.x, ent.y, ent.z, self.player.x, self.player.y, self.player.z, self.player.yaw, self.player.pitch)
                    if proj:
                        sx, sy, scale, rz = proj
                        size_on_screen = ent.size * scale
                        # Kiểm tra xem đạn bắn có găm trúng hitbox hình chữ nhật của quái
                        if (sx - size_on_screen/2 <= hit_x <= sx + size_on_screen/2 and
                            sy - size_on_screen <= hit_y <= sy):
                            if rz < closest_dist:
                                closest_dist = rz
                                hit_enemy = ent

            if hit_enemy:
                hit_enemy.hp -= self.player.gun.dmg
                # Tạo hạt máu văng tung tóe (giới hạn tối đa 12 hạt để không tụt FPS)
                for _ in range(min(8, int(self.player.gun.dmg/3))):
                    self.particles.append(Particle3D(
                        hit_enemy.x, hit_enemy.y + 0.3, hit_enemy.z,
                        random.uniform(-1.5, 1.5), random.uniform(1.0, 3.5), random.uniform(-1.5, 1.5),
                        RED, 0.45
                    ))
                if hit_enemy.hp <= 0:
                    self.score += 15
                    # Tỷ lệ rớt đồ linh kiện ngẫu nhiên khi diệt địch
                    if random.random() < 0.5:
                        self.entities.append(Loot(hit_enemy.x, hit_enemy.z, generate_random_part()))
                    self.spawn_enemy()
            else:
                # Bắn trượt -> Sinh hạt bụi xám nhỏ nơi đất
                pass

    def update(self, dt):
        if self.state != STATE_PLAYING: return

        # Xả đạn liên tục nếu súng là dòng tự động (SMG,...)
        if self.is_holding_shoot:
            self.try_shoot()

        # Giảm dần độ rung màn hình
        if self.screen_shake > 0:
            self.screen_shake -= 25.0 * dt
            if self.screen_shake < 0: self.screen_shake = 0

        self.player.gun.update(time.time(), dt)

        # Di chuyển người chơi dựa trên kéo Joypad
        if self.joy_dir_x != 0 or self.joy_dir_y != 0:
            speed = self.player.speed * dt
            # Joystick Y điều khiển Tiến/Lùi; Joystick X điều khiển di chuyển sang ngang (Strafe)
            move_x = self.joy_dir_y * math.cos(self.player.yaw) + self.joy_dir_x * math.cos(self.player.yaw + math.pi/2)
            move_z = self.joy_dir_y * math.sin(self.player.yaw) + self.joy_dir_x * math.sin(self.player.yaw + math.pi/2)
            
            self.player.x += move_x * speed
            self.player.z += move_z * speed
            # Animation bước đi: camera hơi dập dềnh tạo độ chân thực
            self.player.y = math.sin(time.time() * 9.0) * 0.08
        else:
            self.player.y = 0.0

        # Cập nhật AI và Loot
        current_time = time.time()
        for ent in self.entities:
            if isinstance(ent, Enemy):
                ent.update(self.player.x, self.player.z, dt, self.player, current_time)
            elif isinstance(ent, Loot):
                ent.update(dt)
                # Tự động hút đồ khi người chơi áp sát lại gần dưới 1.0 mét
                dist = math.hypot(ent.x - self.player.x, ent.z - self.player.z)
                if dist < 0.9:
                    if len(self.player.inventory) < 20: # Hạn chế túi tối đa 20 slots
                        self.player.inventory.append(ent.part_data)
                        ent.active = False
        
        # Cập nhật các hạt hiệu ứng (Blood, Muzzle Flash)
        for p in self.particles:
            p.update(dt)

        # Dọn dẹp RAM xóa các entity hết hoạt động để tối ưu bộ nhớ Android
        self.entities = [e for e in self.entities if e.active]
        self.particles = [p for p in self.particles if p.active]
        if len(self.particles) > 30: # Cắt bớt hạt thừa nếu quá nhiều gây lag
            self.particles = self.particles[-30:]

        # Kiểm tra điều kiện thua cuộc
        if self.player.health <= 0:
            self.state = STATE_GAMEOVER

    # ==========================================
    # CÁC GIAO DIỆN VẼ GRAPHICS (RENDER STATES)
    # ==========================================
    def draw_menu(self):
        virtual_screen.fill(DARK_GRAY)
        title = self.font_large.render("GUNSMITH SURVIVAL FPS", True, GOLD)
        instruct = self.font_mid.render("TAP TO START GAME", True, WHITE)
        desc = self.font_small.render("FPS Assembly & Survival Game optimized for Android", True, GRAY)
        
        virtual_screen.blit(title, (V_WIDTH//2 - title.get_width()//2, V_HEIGHT//3))
        virtual_screen.blit(instruct, (V_WIDTH//2 - instruct.get_width()//2, V_HEIGHT//2 + 20))
        virtual_screen.blit(desc, (V_WIDTH//2 - desc.get_width()//2, V_HEIGHT - 60))

    def draw_assembly(self):
        virtual_screen.fill((25, 25, 32))
        
        title = self.font_mid.render("TÚI ĐỒ & CHẾ TẠO SÚNG", True, WHITE)
        virtual_screen.blit(title, (40, 25))

        # Hiển thị súng lắp ghép hiện tại (Hộp phải)
        panel_rect = pygame.Rect(V_WIDTH - 360, 80, 320, 310)
        pygame.draw.rect(virtual_screen, (40, 40, 50), panel_rect, border_radius=10)
        pygame.draw.rect(virtual_screen, GRAY, panel_rect, 2, border_radius=10)
        
        y_offset = 95
        for ptype, part in self.player.gun.parts.items():
            name = part["name"] if part else "RỖNG"
            color = part["color"] if part else RED
            # Nhãn loại linh kiện
            lbl = self.font_small.render(f"{ptype.upper()}:", True, GRAY)
            val = self.font_small.render(name, True, color)
            virtual_screen.blit(lbl, (V_WIDTH - 340, y_offset))
            virtual_screen.blit(val, (V_WIDTH - 230, y_offset))
            y_offset += 28

        # In thông số súng sau lắp ráp
        gun = self.player.gun
        stats_text = [
            f"ST: {gun.dmg}",
            f"T.Bắn: {gun.fire_rate:.2f}s",
            f"Thay Đạn: {gun.reload:.1f}s",
            f"Chính Xác: {int(gun.acc*100)}%",
            f"Băng Đạn: {gun.mag} viên"
        ]
        
        stats_y = y_offset + 10
        for stat in stats_text:
            st_r = self.font_tiny.render(stat, True, GOLD)
            virtual_screen.blit(st_r, (V_WIDTH - 340, stats_y))
            stats_y += 18

        # Nút nhấn Play (Vào Map đấu)
        btn_play = pygame.Rect(V_WIDTH - 150, V_HEIGHT - 65, 130, 45)
        pygame.draw.rect(virtual_screen, GREEN, btn_play, border_radius=8)
        p_text = self.font_mid.render("VÀO MAP", True, WHITE)
        virtual_screen.blit(p_text, (btn_play.x + (btn_play.width//2 - p_text.get_width()//2), btn_play.y + 10))

        # Khối lưới kho đồ chứa linh kiện dự trữ (Bên trái)
        inv_title = self.font_small.render("Linh kiện sở hữu (Chạm để trang bị):", True, GOLD)
        virtual_screen.blit(inv_title, (40, 65))
        
        inv_x, inv_y = 40, 90
        for i, item in enumerate(self.player.inventory):
            row = i // 5
            col = i % 5
            bx = inv_x + col * 85
            by = inv_y + row * 85
            
            # Khung ô chứa đồ
            pygame.draw.rect(virtual_screen, item["color"], (bx, by, 75, 75), border_radius=8)
            pygame.draw.rect(virtual_screen, WHITE, (bx, by, 75, 75), 2, border_radius=8)
            
            # Tên linh kiện viết tắt hiển thị gọn gàng
            abbr = item["name"].replace("Kính Ngắm ", "").replace("Báng ", "").replace("Băng Đạn ", "")
            if len(abbr) > 10: abbr = abbr[:9] + "."
            
            txt = self.font_tiny.render(abbr, True, WHITE)
            type_txt = self.font_tiny.render(item["type"][:4].upper(), True, YELLOW)
            
            virtual_screen.blit(txt, (bx + 6, by + 18))
            virtual_screen.blit(type_txt, (bx + 6, by + 45))

    def draw_playing(self):
        # 1. Vẽ bầu trời và mặt đất (Sky & Floor)
        horizon = V_HEIGHT // 2 + int(self.player.pitch * 240)
        pygame.draw.rect(virtual_screen, SKY_BLUE, (0, 0, V_WIDTH, horizon))
        pygame.draw.rect(virtual_screen, GROUND_COLOR, (0, horizon, V_WIDTH, V_HEIGHT - horizon))

        # 2. Xử lý phép chiếu chiều sâu & Sắp xếp thứ tự xa-gần (Z-Sorting)
        render_list = []
        for ent in self.entities + self.particles:
            proj = project_3d_to_2d(ent.x, ent.y, ent.z, self.player.x, self.player.y, self.player.z, self.player.yaw, self.player.pitch)
            if proj:
                sx, sy, scale, rz = proj
                ent.dist_to_player = rz
                render_list.append((ent, sx, sy, scale))

        # Sắp xếp vẽ xa trước, gần vẽ đè sau (Tránh lỗi đè hình)
        render_list.sort(key=lambda item: item[0].dist_to_player, reverse=True)

        # 3. Thực hiện vẽ các Billboard lên màn hình ảo
        for ent, sx, sy, scale in render_list:
            size_on_screen = int(ent.size * scale)
            if size_on_screen <= 0 or size_on_screen > 1200: continue

            if isinstance(ent, Enemy):
                # Scale trực tiếp từ Texture Cache đã dựng sẵn (Tối ưu cực lớn so với vẽ lại)
                scaled_enemy = pygame.transform.scale(self.enemy_cache_surf, (size_on_screen, size_on_screen))
                virtual_screen.blit(scaled_enemy, (sx - size_on_screen//2, sy - size_on_screen))
                
                # Vẽ thanh HP quái vật mini trên đầu
                hp_w = size_on_screen
                hp_h = max(2, size_on_screen // 12)
                pygame.draw.rect(virtual_screen, RED, (sx - hp_w//2, sy - size_on_screen - hp_h - 4, hp_w, hp_h))
                pygame.draw.rect(virtual_screen, GREEN, (sx - hp_w//2, sy - size_on_screen - hp_h - 4, hp_w * (ent.hp / ent.max_hp), hp_h))

            elif isinstance(ent, Loot):
                # Vẽ hộp linh kiện phát sáng nổi trên mặt đất
                color = get_loot_color(ent.part_data["type"])
                l_rect = pygame.Rect(sx - size_on_screen//2, sy - size_on_screen//2, size_on_screen, size_on_screen)
                pygame.draw.rect(virtual_screen, color, l_rect, border_radius=2)
                pygame.draw.rect(virtual_screen, WHITE, l_rect, max(1, size_on_screen//8), border_radius=2)

            elif isinstance(ent, Particle3D):
                # Vẽ các hạt bụi máu, tia lửa
                p_size = max(1, int(ent.size * scale))
                pygame.draw.rect(virtual_screen, ent.color, (sx, sy, p_size, p_size))

        # 4. Vẽ HUD ngắm bắn và súng
        # Tâm ngắm thông minh (Dựa trên độ chính xác súng)
        spread = (1.0 - self.player.gun.acc) * 75
        cx, cy = V_WIDTH // 2, V_HEIGHT // 2
        pygame.draw.circle(virtual_screen, WHITE, (cx, cy), max(3, int(spread)), 1)
        pygame.draw.line(virtual_screen, WHITE, (cx - 12, cy), (cx + 12, cy), 1)
        pygame.draw.line(virtual_screen, WHITE, (cx, cy - 12), (cx, cy + 12), 1)

        # Vẽ súng ở góc phải bên dưới màn hình, cộng hưởng với Recoil và nhún di chuyển
        gun_x = V_WIDTH - 240 + int(self.player.gun.recoil_offset)
        gun_y = V_HEIGHT - 170 + int(self.player.gun.recoil_offset) + int(self.player.y * 120)
        
        if self.player.gun.is_reloading:
            gun_y += int(math.sin(time.time() * 11) * 35) # Anim súng thò lên thụt xuống khi reload
            
        virtual_screen.blit(self.player.gun.surf, (gun_x, gun_y))

        # Muzzle Flash (Tia lửa bùng lên đầu nòng khi nổ súng)
        if time.time() - self.player.gun.last_shot_time < 0.05:
            # Ước lượng vị trí đầu nòng
            bw = 50 if "long" in self.player.gun.parts["barrel"]["id"] else 25
            flash_x = gun_x + 30 - bw
            flash_y = gun_y + 47
            pygame.draw.circle(virtual_screen, YELLOW, (flash_x, flash_y), random.randint(15, 25))
            pygame.draw.circle(virtual_screen, WHITE, (flash_x, flash_y), random.randint(8, 12))

        # Vẽ các nút cảm ứng cho điện thoại (Alpha mờ đẹp mắt)
        # 4.1 Joypad di chuyển bên trái
        self.draw_alpha_circle(virtual_screen, (150, 150, 150, 80), (self.joy_x, self.joy_y), self.joy_radius)
        self.draw_alpha_circle(virtual_screen, (220, 220, 220, 180), (int(self.joy_knob_x), int(self.joy_knob_y)), 25)

        # 4.2 Nút SHOOT khổng lồ
        sh_color = (220, 60, 60, 160) if not self.is_holding_shoot else (255, 100, 100, 220)
        self.draw_alpha_circle(virtual_screen, sh_color, self.btn_shoot.center, self.btn_shoot.width//2)
        sh_txt = self.font_mid.render("FIRE", True, WHITE)
        virtual_screen.blit(sh_txt, (self.btn_shoot.centerx - sh_txt.get_width()//2, self.btn_shoot.centery - sh_txt.get_height()//2))

        # 4.3 Nút RELOAD
        rl_color = (50, 120, 220, 160) if not self.player.gun.is_reloading else (100, 200, 100, 180)
        self.draw_alpha_circle(virtual_screen, rl_color, self.btn_reload.center, self.btn_reload.width//2)
        rl_txt = self.font_tiny.render("RELOAD", True, WHITE)
        virtual_screen.blit(rl_txt, (self.btn_reload.centerx - rl_txt.get_width()//2, self.btn_reload.centery - rl_txt.get_height()//2))

        # 4.4 Nút BAG (Mở rương ráp súng)
        pygame.draw.rect(virtual_screen, BROWN, self.btn_bag, border_radius=6)
        bag_txt = self.font_small.render("TÚI ĐỒ", True, WHITE)
        virtual_screen.blit(bag_txt, (self.btn_bag.x + (self.btn_bag.width//2 - bag_txt.get_width()//2), self.btn_bag.y + 14))

        # 4.5 Chỉ số máu và đạn lên HUD
        hp_text = self.font_large.render(f"HP: {self.player.health}", True, RED)
        virtual_screen.blit(hp_text, (25, 20))
        
        ammo_str = "NẠP ĐẠN..." if self.player.gun.is_reloading else f"ĐẠN: {self.player.gun.current_ammo}/{self.player.gun.mag}"
        ammo_text = self.font_mid.render(ammo_str, True, WHITE if self.player.gun.current_ammo > 0 else RED)
        virtual_screen.blit(ammo_text, (25, 65))

        score_text = self.font_mid.render(f"ĐIỂM: {self.score}", True, GOLD)
        virtual_screen.blit(score_text, (25, 100))

    def draw_alpha_circle(self, surface, color, center, radius):
        # Hàm bổ trợ vẽ vòng tròn có độ trong suốt (Alpha channel)
        target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
        shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA).convert_alpha()
        pygame.draw.circle(shape_surf, color, (radius, radius), radius)
        surface.blit(shape_surf, target_rect)

    def draw_gameover(self):
        virtual_screen.fill(BLACK)
        txt_dead = self.font_large.render("BẠN ĐÃ HY SINH!", True, RED)
        txt_score = self.font_mid.render(f"Tổng Điểm Đạt Được: {self.score}", True, WHITE)
        txt_restart = self.font_small.render("CHẠM MÀN HÌNH ĐỂ KHỞI ĐỘNG LẠI", True, GRAY)
        
        virtual_screen.blit(txt_dead, (V_WIDTH//2 - txt_dead.get_width()//2, V_HEIGHT//3))
        virtual_screen.blit(txt_score, (V_WIDTH//2 - txt_score.get_width()//2, V_HEIGHT//2))
        virtual_screen.blit(txt_restart, (V_WIDTH//2 - txt_restart.get_width()//2, V_HEIGHT - 80))

    # ==========================================
    # VÒNG LẶP CHẠY GAME CHÍNH (MAIN LOOP)
    # ==========================================
    def run(self):
        last_time = time.time()
        while True:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            # Giới hạn dt phòng hờ game lag gây lỗi giật lùi xuyên tường vật thể
            dt = min(0.08, dt)

            self.process_inputs()
            self.update(dt)

            # Phân bổ các bản vẽ màn hình lên virtual_screen
            if self.state == STATE_MENU:
                self.draw_menu()
            elif self.state == STATE_ASSEMBLY:
                self.draw_assembly()
            elif self.state == STATE_PLAYING:
                self.draw_playing()
            elif self.state == STATE_GAMEOVER:
                self.draw_gameover()

            # Rung màn hình khi súng bắn
            shake_x, shake_y = 0, 0
            if self.screen_shake > 0 and self.state == STATE_PLAYING:
                shake_x = random.randint(-int(self.screen_shake), int(self.screen_shake))
                shake_y = random.randint(-int(self.screen_shake), int(self.screen_shake))

            # Render kéo dãn Surface ảo 854x480 vừa khít với màn hình thật của điện thoại
            # Sử dụng thuật toán scale nhanh của Pygame để tối ưu phần cứng điện thoại
            pygame.transform.scale(virtual_screen, (REAL_WIDTH, REAL_HEIGHT), screen)
            
            # Nếu có độ rung màn hình, dời lệch nhẹ góc vẽ display
            if shake_x != 0 or shake_y != 0:
                screen.blit(screen, (shake_x, shake_y))

            pygame.display.flip()
            clock.tick(60) # Cố định tốc độ game 60 FPS tiết kiệm pin Android

if __name__ == "__main__":
    game = Game()
    game.run()
