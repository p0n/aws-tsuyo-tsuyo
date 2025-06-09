import pygame
import sys
import random
import os
import time

# ゲーム設定
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
GRID_WIDTH = 6
GRID_HEIGHT = 12
CELL_SIZE = 50
FPS = 60

# ゲームタイトル
GAME_TITLE_JP = "AWSツヨツヨ"
GAME_TITLE_EN = "AWS Tsuyo-Tsuyo"

# 難易度レベル設定
DIFFICULTY_LEVELS = {
    "初心者": 4,
    "中級者": 6,
    "上級者": 20
}

# 色の定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

# アニメーション設定
CHAIN_DELAY = 0.5  # 連鎖間の遅延（秒）
VANISH_DURATION = 0.3  # 消える時のアニメーション時間（秒）

# フォントの設定
def get_font(size):
    try:
        # macOSの日本語フォント
        return pygame.font.Font("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", size)
    except:
        try:
            # Windowsの日本語フォント
            return pygame.font.Font("C:\\Windows\\Fonts\\msgothic.ttc", size)
        except:
            # それでもダメならデフォルトフォント
            return pygame.font.SysFont(None, size)

class DifficultySelector:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = get_font(48)
        self.font = get_font(36)
        self.selected = 0
        self.difficulties = list(DIFFICULTY_LEVELS.keys())
        
        # 背景画像の読み込み
        try:
            self.bg_image = pygame.image.load('assets/bg.jpg')
            self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            # 背景画像が読み込めない場合は白色の背景を使用
            self.bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg_image.fill(WHITE)
    
    def draw(self):
        # 背景画像を描画
        self.screen.blit(self.bg_image, (0, 0))
        
        # タイトル
        title = self.font_large.render(GAME_TITLE_JP, True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # 難易度選択
        subtitle = self.font.render("難易度を選択してください", True, BLACK)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 200))
        
        # 難易度オプション
        for i, diff in enumerate(self.difficulties):
            color = (255, 0, 0) if i == self.selected else BLACK
            text = self.font.render(f"{i+1}. {diff}", True, color)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 300 + i * 50))
        
        # 操作説明
        instruction = self.font.render("上下キーで選択、Enterで決定", True, BLACK)
        self.screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, 500))
        
        pygame.display.flip()
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.difficulties)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.difficulties)
            elif event.key == pygame.K_RETURN:
                return self.difficulties[self.selected]
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                idx = event.key - pygame.K_1
                if 0 <= idx < len(self.difficulties):
                    return self.difficulties[idx]
        return None
    
    def run(self):
        clock = pygame.time.Clock()
        selected_difficulty = None
        
        while selected_difficulty is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                selected_difficulty = self.handle_event(event)
            
            self.draw()
            clock.tick(FPS)
        
        return selected_difficulty

# アイコンの読み込み関数
def load_aws_icons(count=20):
    """
    assetsフォルダからAWSアイコンを読み込む
    """
    icon_paths = []
    for i in range(count):
        icon_path = f'assets/icon_{i}.png'
        if os.path.exists(icon_path):
            icon_paths.append(icon_path)
    
    # 十分なアイコンがない場合はエラーメッセージを表示
    if len(icon_paths) < count:
        print(f"Warning: Requested {count} icons but only found {len(icon_paths)}")
    
    return icon_paths

class PuyoGame:
    def __init__(self, difficulty="初心者", screen=None):
        if screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption(GAME_TITLE_EN)
        else:
            self.screen = screen
            
        self.clock = pygame.time.Clock()
        self.font = get_font(36)
        
        # 背景画像の読み込み
        try:
            self.bg_image = pygame.image.load('assets/bg.jpg')
            self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            # 背景画像が読み込めない場合は白色の背景を使用
            self.bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg_image.fill(WHITE)
        
        # 難易度に基づいてアイコン数を設定
        self.difficulty = difficulty
        self.icon_count = DIFFICULTY_LEVELS[difficulty]
        
        # アイコンをダウンロード
        self.icons = []
        self.load_icons()
        
        # ゲームボード初期化
        self.board = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # 現在のぷよ
        self.current_puyo = self.create_new_puyo()
        self.next_puyo = self.create_new_puyo()
        
        # ゲーム状態
        self.game_over = False
        self.score = 0
        self.fall_time = 0
        self.fall_speed = 0.5  # 秒単位
        self.return_to_menu = False
        self.paused = False
        
        # アニメーション状態
        self.animation_state = None  # None, "vanishing", "falling"
        self.animation_time = 0
        self.vanishing_puyos = []
        self.chain_count = 0
        
    def load_icons(self):
        """アイコンを読み込む"""
        icon_paths = load_aws_icons(self.icon_count)
        for path in icon_paths:
            icon = pygame.image.load(path)
            self.icons.append(icon)
    
    def create_new_puyo(self):
        """新しいぷよを作成"""
        if len(self.icons) < 2:
            return None
        
        # ランダムに2つのアイコンを選択
        icon1 = random.randint(0, len(self.icons) - 1)
        icon2 = random.randint(0, len(self.icons) - 1)
        
        # 初期位置
        x = GRID_WIDTH // 2 - 1
        y = 0
        
        return {
            'position': [(x, y), (x, y + 1)],
            'icons': [icon1, icon2],
            'rotation': 0
        }
    
    def draw_board(self):
        """ゲームボードを描画"""
        # 背景画像を描画
        self.screen.blit(self.bg_image, (0, 0))
        
        # ゲームエリアの半透明オーバーレイ
        game_area = pygame.Surface((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE), pygame.SRCALPHA)
        game_area.fill((255, 255, 255, 128))  # 白色の半透明
        self.screen.blit(game_area, (0, 0))
        
        # グリッド線
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(
                self.screen, 
                GRAY, 
                (x * CELL_SIZE, 0), 
                (x * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)
            )
        
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(
                self.screen, 
                GRAY, 
                (0, y * CELL_SIZE), 
                (GRID_WIDTH * CELL_SIZE, y * CELL_SIZE)
            )
        
        # ボード上のぷよを描画
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.board[y][x] is not None:
                    # 消えるアニメーション中のぷよは半透明に
                    if self.animation_state == "vanishing" and (x, y) in self.vanishing_puyos:
                        progress = self.animation_time / VANISH_DURATION
                        alpha = int(255 * (1 - progress))
                        
                        # 元のアイコンを取得
                        icon = self.icons[self.board[y][x]]
                        
                        # 半透明のコピーを作成
                        icon_copy = icon.copy()
                        icon_copy.set_alpha(alpha)
                        
                        self.screen.blit(
                            icon_copy, 
                            (x * CELL_SIZE, y * CELL_SIZE)
                        )
                    else:
                        self.screen.blit(
                            self.icons[self.board[y][x]], 
                            (x * CELL_SIZE, y * CELL_SIZE)
                        )
        
        # 現在のぷよを描画
        if self.current_puyo and not self.animation_state:
            for i, (x, y) in enumerate(self.current_puyo['position']):
                if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                    self.screen.blit(
                        self.icons[self.current_puyo['icons'][i]], 
                        (x * CELL_SIZE, y * CELL_SIZE)
                    )
        
        # 次のぷよを表示
        if self.next_puyo:
            text = self.font.render("Next:", True, BLACK)
            self.screen.blit(text, (GRID_WIDTH * CELL_SIZE + 20, 20))
            
            for i, icon_idx in enumerate(self.next_puyo['icons']):
                self.screen.blit(
                    self.icons[icon_idx], 
                    (GRID_WIDTH * CELL_SIZE + 20, 60 + i * CELL_SIZE)
                )
        
        # スコア表示
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (GRID_WIDTH * CELL_SIZE + 20, 180))
        
        # 難易度表示
        diff_text = self.font.render(f"難易度: {self.difficulty}", True, BLACK)
        self.screen.blit(diff_text, (GRID_WIDTH * CELL_SIZE + 20, 220))
        
        # 連鎖数表示
        if self.chain_count > 0:
            chain_text = self.font.render(f"{self.chain_count}連鎖!", True, (255, 0, 0))
            self.screen.blit(chain_text, (GRID_WIDTH * CELL_SIZE + 20, 260))
        
        # ポーズ表示
        if self.paused:
            # 半透明のオーバーレイ
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # 黒色の半透明
            self.screen.blit(overlay, (0, 0))
            
            # ポーズテキスト
            pause_text = self.font.render("PAUSE", True, WHITE)
            self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            
            # 操作説明
            resume_text = self.font.render("Pキーで再開", True, WHITE)
            self.screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        
        # ゲームオーバー表示
        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
            self.screen.blit(game_over_text, (GRID_WIDTH * CELL_SIZE // 2 - 80, GRID_HEIGHT * CELL_SIZE // 2))
            
            restart_text = self.font.render("Rキーでリスタート", True, BLACK)
            self.screen.blit(restart_text, (GRID_WIDTH * CELL_SIZE // 2 - 100, GRID_HEIGHT * CELL_SIZE // 2 + 40))
            
            menu_text = self.font.render("Mキーで難易度選択", True, BLACK)
            self.screen.blit(menu_text, (GRID_WIDTH * CELL_SIZE // 2 - 100, GRID_HEIGHT * CELL_SIZE // 2 + 80))
    
    def move_puyo(self, dx=0, dy=0):
        """ぷよを移動"""
        if self.game_over or not self.current_puyo or self.paused or self.animation_state:
            return False
        
        # 移動後の位置を計算
        new_positions = [(x + dx, y + dy) for x, y in self.current_puyo['position']]
        
        # 移動が有効かチェック
        if self.is_valid_position(new_positions):
            self.current_puyo['position'] = new_positions
            return True
        return False
    
    def rotate_puyo(self):
        """ぷよを回転"""
        if self.game_over or not self.current_puyo or self.paused or self.animation_state:
            return False
        
        # 回転の中心を取得
        center_x, center_y = self.current_puyo['position'][0]
        
        # 2つ目のぷよの相対位置を計算
        x2, y2 = self.current_puyo['position'][1]
        rel_x, rel_y = x2 - center_x, y2 - center_y
        
        # 時計回りに90度回転
        new_rel_x, new_rel_y = -rel_y, rel_x
        
        # 新しい位置を計算
        new_positions = [(center_x, center_y), (center_x + new_rel_x, center_y + new_rel_y)]
        
        # 回転が有効かチェック
        if self.is_valid_position(new_positions):
            self.current_puyo['position'] = new_positions
            self.current_puyo['rotation'] = (self.current_puyo['rotation'] + 1) % 4
            return True
        
        # 壁キック処理（壁際で回転できない場合、少し横にずらす）
        kick_offsets = [(-1, 0), (1, 0), (0, -1)]
        for offset_x, offset_y in kick_offsets:
            kicked_positions = [(pos[0] + offset_x, pos[1] + offset_y) for pos in new_positions]
            if self.is_valid_position(kicked_positions):
                self.current_puyo['position'] = kicked_positions
                self.current_puyo['rotation'] = (self.current_puyo['rotation'] + 1) % 4
                return True
        
        return False
    
    def is_valid_position(self, positions):
        """指定された位置が有効かどうかをチェック"""
        for x, y in positions:
            # 画面外チェック
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                return False
            
            # 他のぷよとの衝突チェック
            if y >= 0 and self.board[y][x] is not None:
                return False
        
        return True
    
    def lock_puyo(self):
        """現在のぷよをボードに固定"""
        for i, (x, y) in enumerate(self.current_puyo['position']):
            if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                self.board[y][x] = self.current_puyo['icons'][i]
        
        # 浮いているぷよをチェック
        self.check_floating_puyos()
        
        # 連鎖チェック
        self.chain_count = 0
        self.start_chain_check()
        
        # 次のぷよを取得
        self.current_puyo = self.next_puyo
        self.next_puyo = self.create_new_puyo()
        
        # ゲームオーバーチェック
        for x, y in self.current_puyo['position']:
            if y >= 0 and self.board[y][x] is not None:
                self.game_over = True
                break
    
    def check_floating_puyos(self):
        """浮いているぷよをチェックして落とす"""
        # 各列ごとに下から上に向かってチェック
        for x in range(GRID_WIDTH):
            # 各列の最下部から上に向かって空白を探す
            for y in range(GRID_HEIGHT - 1, 0, -1):
                if self.board[y][x] is None:
                    # 空白の上にあるぷよを見つけて落とす
                    for above_y in range(y - 1, -1, -1):
                        if self.board[above_y][x] is not None:
                            self.board[y][x] = self.board[above_y][x]
                            self.board[above_y][x] = None
                            break
    
    def apply_gravity(self):
        """重力を適用（ぷよを下に落とす）"""
        moved = False
        
        # 各列ごとに独立して重力を適用
        for x in range(GRID_WIDTH):
            # 下から上に向かってチェック
            for y in range(GRID_HEIGHT - 2, -1, -1):
                if self.board[y][x] is not None and self.board[y + 1][x] is None:
                    # 下が空いていれば落とす
                    self.board[y + 1][x] = self.board[y][x]
                    self.board[y][x] = None
                    moved = True
        
        return moved
    
    def start_chain_check(self):
        """連鎖チェックを開始"""
        self.animation_state = "checking"
        self.check_chains()
    
    def check_chains(self):
        """連鎖をチェックして消去"""
        # 連結成分を見つける
        visited = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        chains_found = False
        self.vanishing_puyos = []
        
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.board[y][x] is not None and not visited[y][x]:
                    chain = []
                    self.find_chain(x, y, self.board[y][x], visited, chain)
                    
                    # 4つ以上連結していれば消去対象に追加
                    if len(chain) >= 4:
                        chains_found = True
                        self.vanishing_puyos.extend(chain)
                        
                        # スコア加算
                        self.score += len(chain) * 10
        
        if chains_found:
            # 連鎖カウント増加
            self.chain_count += 1
            
            # 消えるアニメーション開始
            self.animation_state = "vanishing"
            self.animation_time = 0
        else:
            # 連鎖がなければアニメーション終了
            self.animation_state = None
    
    def find_chain(self, x, y, icon_type, visited, chain):
        """同じ種類のぷよの連結を探索（深さ優先探索）"""
        # 範囲外チェック
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return
        
        # 既に訪問済みか、異なるタイプのぷよかチェック
        if visited[y][x] or self.board[y][x] != icon_type:
            return
        
        # このぷよを連結に追加
        visited[y][x] = True
        chain.append((x, y))
        
        # 4方向を探索
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        for dx, dy in directions:
            self.find_chain(x + dx, y + dy, icon_type, visited, chain)
    
    def update_animation(self, dt):
        """アニメーション状態を更新"""
        if self.animation_state == "vanishing":
            self.animation_time += dt
            
            # 消えるアニメーション終了
            if self.animation_time >= VANISH_DURATION:
                # ぷよを実際に消す
                for x, y in self.vanishing_puyos:
                    if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                        self.board[y][x] = None
                
                # 落下アニメーション開始
                self.animation_state = "falling"
                self.animation_time = 0
                
                # 重力を適用
                while self.apply_gravity():
                    pass
                
                # 浮いているぷよをチェック
                self.check_floating_puyos()
                
                # 次の連鎖チェックを遅延実行
                self.animation_state = "delay"
                self.animation_time = 0
        
        elif self.animation_state == "delay":
            self.animation_time += dt
            
            # 遅延終了後、次の連鎖チェック
            if self.animation_time >= CHAIN_DELAY:
                self.check_chains()
    
    def update(self, dt):
        """ゲーム状態を更新"""
        if self.game_over or self.paused:
            return
        
        # アニメーション更新
        if self.animation_state:
            self.update_animation(dt)
            return
        
        # 自動落下
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if not self.move_puyo(0, 1):
                self.lock_puyo()
    
    def restart(self):
        """ゲームをリスタート"""
        self.__init__(self.difficulty, self.screen)
    
    def change_difficulty(self, difficulty):
        """難易度を変更"""
        if difficulty in DIFFICULTY_LEVELS:
            self.__init__(difficulty, self.screen)
    
    def toggle_pause(self):
        """ポーズ状態を切り替え"""
        if not self.game_over:
            self.paused = not self.paused
    
    def run(self):
        """ゲームループ"""
        running = True
        last_time = pygame.time.get_ticks() / 1000.0
        
        while running:
            # デルタタイム計算
            current_time = pygame.time.get_ticks() / 1000.0
            dt = current_time - last_time
            last_time = current_time
            
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.toggle_pause()
                    elif not self.paused:  # ポーズ中は他のキー入力を無視
                        if event.key == pygame.K_LEFT:
                            self.move_puyo(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move_puyo(1, 0)
                        elif event.key == pygame.K_DOWN:
                            self.move_puyo(0, 1)
                        elif event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                            self.rotate_puyo()
                        elif event.key == pygame.K_r:
                            self.restart()
                        elif event.key == pygame.K_m and self.game_over:
                            self.return_to_menu = True
                            running = False
                        elif event.key == pygame.K_1:
                            self.change_difficulty("初心者")
                        elif event.key == pygame.K_2:
                            self.change_difficulty("中級者")
                        elif event.key == pygame.K_3:
                            self.change_difficulty("上級者")
            
            # ゲーム状態更新
            self.update(dt)
            
            # 描画
            self.draw_board()
            pygame.display.flip()
            
            # フレームレート制御
            self.clock.tick(FPS)
        
        return self.return_to_menu

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(GAME_TITLE_EN)
    
    while True:
        # 難易度選択画面
        selector = DifficultySelector(screen)
        difficulty = selector.run()
        
        # 選択された難易度でゲーム開始
        game = PuyoGame(difficulty, screen)
        return_to_menu = game.run()
        
        # ゲームが終了してメニューに戻る指示がなければ終了
        if not return_to_menu:
            break
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()