import pyxel
import math
import random  # ランダム生成のために追加

# 定数の定義
SCREEN_WIDTH = 160  # 画面の幅
SCREEN_HEIGHT = 120  # 画面の高さ
PLAY_AREA_TOP = 10  # プレイエリアの上端
PLAY_AREA_BOTTOM = SCREEN_HEIGHT - 10  # プレイエリアの下端
PLAYER_RADIUS = 5  # プレイヤーの初期半径
PLAYER_MIN_RADIUS = 2  # プレイヤーの最小半径
PLAYER_INITIAL_SPEED = 2  # プレイヤーの初期速度
PLAYER_MAX_SPEED = 10  # プレイヤーの最大速度
POWER_UP_DURATION = 30  # パワーアップの持続時間 (1秒間: 30FPS * 1)
CIRCLE_COUNT = 5  # 画面上に表示される円の数
CIRCLE_RADIUS = 1  # 円の半径
SCORE_INCREMENT = 1000  # 衝突時のスコア増加量

# テキストの色と位置
TEXT_COLOR_READY = 10  # 使用可能な状態のテキスト色 (緑)
TEXT_COLOR_USED = 8  # 使用済み状態のテキスト色 (赤)
TEXT_COLOR_SCORE = 7  # スコア表示のテキスト色 (白)
TEXT_POSITION_SCORE = (5, 110)  # スコア表示の位置
TEXT_POSITION_POWER_UP = (60, 110)  # パワーアップ状態の表示位置
TEXT_POSITION_BRAKE = (60, 100)  # ブレーキ状態の表示位置

# タイトル画面のテキスト
TITLE_TEXT = "SPACE SPEEDER"  # ゲームタイトル
START_TEXT = "PRESS SPACE OR A TO START"  # ゲーム開始の説明
QUIT_TEXT = "PRESS Q OR B TO QUIT"  # ゲーム終了の説明
TITLE_TEXT_COLOR = 7  # タイトルテキストの色 (白)
START_TEXT_COLOR = TEXT_COLOR_READY  # スタートテキストの色 (緑)
QUIT_TEXT_COLOR = TEXT_COLOR_USED  # 終了テキストの色 (赤)
TITLE_TEXT_POSITION = (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 - 20)  # タイトルテキストの位置
START_TEXT_POSITION = (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 20)  # スタートテキストの位置
QUIT_TEXT_POSITION = (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 30)  # 終了テキストの位置

class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Space Speeder", fps=30)

        # リソースの読み込み
        pyxel.load("my_resource.pyxres")

        # サウンドの設定
        pyxel.sound(0).set("c3e3g3c4", "p", "7", "n", 10)  # 通常衝突音
        pyxel.sound(1).set("f3a3d4f4", "p", "7", "n", 10)  # ボーナス衝突音
        pyxel.sound(2).set("g2c3e3g3c4e4g4", "t", "6", "n", 30)  # タイトル画面BGM
        pyxel.sound(3).set("c2e2g2c3e3g3", "p", "7", "n", 20)  # ゲーム画面BGM
        pyxel.sound(4).set("e3g3b3e4g4b4", "p", "6", "n", 15)  # スコア画面BGM
        self.selected_timer = 10  # デフォルトのタイマー秒数を初期化
        self.reset_game()  # 初期化処理

        pyxel.run(self.update, self.draw)

    def reset_game(self):
        """ゲームのパラメータを初期値にリセット"""
        self.state = "TITLE"  # ゲームの状態をタイトルに戻す
        self.x = SCREEN_WIDTH // 2  # プレイヤーの初期X座標
        self.y = SCREEN_HEIGHT // 2  # プレイヤーの初期Y座標
        self.r = PLAYER_RADIUS  # プレイヤーの初期半径
        self.score = 0  # スコアの初期化
        self.speed = PLAYER_INITIAL_SPEED  # プレイヤーの初期速度
        self.deadzone = 2000  # 入力デッドゾーン
        self.circles = [(random.randint(0, SCREEN_WIDTH - 1), random.randint(PLAY_AREA_TOP, PLAY_AREA_BOTTOM - 1), CIRCLE_RADIUS) for _ in range(CIRCLE_COUNT)]  # 円の初期配置
        self.power_up_active = False  # パワーアップの状態
        self.power_up_timer = 0  # パワーアップの残り時間
        self.power_up_used = False  # パワーアップの使用状態
        self.brake_used = False  # ブレーキの使用状態
        self.stage = 1  # ステージ番号
        self.timer = self.selected_timer * 30  # 選択した秒数をタイマーに設定
        self.effects = []  # 衝突エフェクトのリスト
        self.last_collision_time = -10  # 最後の衝突時刻

        # タイトル画面BGMを再生
        pyxel.play(0, 2, loop=True)

    def update(self):
        if self.state == "TITLE":
            self.update_title()
        elif self.state == "GAME":
            self.update_game()
        elif self.state == "SCORE":
            self.update_score()

    def update_title(self):
        # タイトル画面に入ったときにBGMを再生
        if not pyxel.play_pos(0):  # チャンネル0でBGMが再生されていない場合
            pyxel.play(0, 2, loop=True)  # タイトル画面BGMをループ再生

        # スタートボタン (スペースキーまたはAボタン)
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            self.timer = self.selected_timer * 30  # 選択した秒数をタイマーに設定
            self.state = "GAME"
            pyxel.stop()  # タイトル画面BGMを停止
            pyxel.play(0, 3, loop=True)  # ゲーム画面BGMを再生

        # 終了ボタン (QキーまたはBボタン)
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            pyxel.quit()

        # 左右キーでタイマー秒数を変更
        if pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            if self.selected_timer > 10:
                self.selected_timer -= 20 if self.selected_timer == 60 else 10
        if pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            if self.selected_timer < 60:
                self.selected_timer += 20 if self.selected_timer == 10 else 10

    def update_game(self):
        # タイマーを減少
        self.timer -= 1
        if self.timer <= 0:
            self.state = "SCORE"  # スコア画面へ遷移
            pyxel.stop()  # ゲーム画面BGMを停止
            pyxel.play(0, 4, loop=True)  # スコア画面BGMを再生
            return

        # 衝突判定と削除
        new_circles = []
        for cx, cy, cr in self.circles:
            if self.check_collision(self.x, self.y, self.r, cx, cy, cr):
                current_time = pyxel.frame_count
                self.score += SCORE_INCREMENT
                self.r -= 1
                if self.r <= PLAYER_MIN_RADIUS:
                    self.r = PLAYER_MIN_RADIUS
                if not self.brake_used:
                    self.speed += 1
                    if self.speed > PLAYER_MAX_SPEED:
                        self.speed = PLAYER_MAX_SPEED

                # ボーナススコアの判定
                if current_time - self.last_collision_time <= 6:  # 0.2秒以内 (30FPSで6フレーム)
                    self.score += 500  # ボーナススコア
                    # ボーナスエフェクトを追加
                    self.effects.append({"x": cx, "y": cy, "timer": 15, "bonus": True})
                    pyxel.play(1, 1)  # ボーナス衝突音をチャンネル1で再生
                else:
                    # 通常の衝突エフェクトを追加
                    self.effects.append({"x": cx, "y": cy, "timer": 15, "bonus": False})
                    pyxel.play(1, 0)  # 通常衝突音をチャンネル1で再生

                self.last_collision_time = current_time  # 衝突時刻を更新
            else:
                new_circles.append((cx, cy, cr))
        self.circles = new_circles

        # エフェクトの更新
        self.effects = [effect for effect in self.effects if effect["timer"] > 0]
        for effect in self.effects:
            effect["timer"] -= 1

        # Aボタンでパワーアップを発動
        if (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)) and not self.power_up_used:
            self.power_up_active = True
            self.power_up_timer = POWER_UP_DURATION
            self.power_up_used = True

        # パワーアップ中の処理
        if self.power_up_active:
            self.r = PLAYER_RADIUS
            self.power_up_timer -= 1
            if self.power_up_timer <= 0:
                self.power_up_active = False
                self.r = PLAYER_MIN_RADIUS

        # Bボタンでブレーキを発動
        if (pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)) and not self.brake_used:
            self.speed = PLAYER_INITIAL_SPEED
            self.brake_used = True

        # キーボード入力
        if pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP) or pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY) < -self.deadzone:
            self.y -= self.speed
        if pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN) or pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY) > self.deadzone:
            self.y += self.speed
        if pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT) or pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX) < -self.deadzone:
            self.x -= self.speed
        if pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT) or pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX) > self.deadzone:
            self.x += self.speed

        # プレイヤーの円が画面外に出ないように制限
        self.x = max(0, min(self.x, SCREEN_WIDTH - 1))
        self.y = max(PLAY_AREA_TOP, min(self.y, PLAY_AREA_BOTTOM - 1))

        # すべての円が削除された場合、新しい円を生成
        if not self.circles:
            self.circles = [(random.randint(0, SCREEN_WIDTH - 1), random.randint(PLAY_AREA_TOP, PLAY_AREA_BOTTOM - 1), CIRCLE_RADIUS) for _ in range(CIRCLE_COUNT)]
            self.stage += 1  # ステージ数を加算
            self.power_up_used = False  # パワーアップを再度使用可能に
            self.brake_used = False  # ブレーキを再度使用可能に

            # パワーアップを終了
            self.power_up_active = False
            self.r = PLAYER_RADIUS  # 半径を元に戻す

    def update_score(self):
        # タイトル画面に戻るボタン (QキーまたはBボタン)
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            self.reset_game()  # パラメータを初期値にリセット
            pyxel.stop()  # スコア画面BGMを停止
            pyxel.play(0, 2, loop=True)  # タイトル画面BGMを再生

    def check_collision(self, x1, y1, r1, x2, y2, r2):
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return distance <= (r1 + r2)

    def draw(self):
        if self.state == "TITLE":
            self.draw_title()
        elif self.state == "GAME":
            self.draw_game()
        elif self.state == "SCORE":
            self.draw_score()

    def draw_title(self):
        pyxel.cls(0)

        # タイトル画像を描画
        pyxel.blt((SCREEN_WIDTH - 80) / 2, 15, 0, 0, 0, 80, 53, 1)
        # スタートと終了ボタンの説明
        pyxel.text(*START_TEXT_POSITION, START_TEXT, START_TEXT_COLOR)
        pyxel.text(*QUIT_TEXT_POSITION, QUIT_TEXT, QUIT_TEXT_COLOR)

        # タイマーと変更方法を下端に1行で表示
        pyxel.text(5, SCREEN_HEIGHT - 8, f"Timer: {self.selected_timer}s | Use LEFT/RIGHT to change", TEXT_COLOR_SCORE)

    def draw_game(self):
        pyxel.cls(0)

        # プレイヤーのデザイン
        pyxel.circ(self.x, self.y, self.r, 3)
        pyxel.circb(self.x, self.y, self.r + 2, 7)
        pyxel.circb(self.x, self.y, self.r + 4, 10)
        pyxel.line(self.x - self.r - 2, self.y, self.x + self.r + 2, self.y, 8)
        pyxel.line(self.x, self.y - self.r - 2, self.x, self.y + self.r + 2, 8)

        # 他の円を描画
        for cx, cy, cr in self.circles:
            pyxel.circ(cx, cy, cr, 1)

        # 衝突エフェクトを描画
        for effect in self.effects:
            if effect.get("bonus"):
                # ボーナスエフェクト (大きな点滅する円)
                pyxel.circb(effect["x"], effect["y"], 10, pyxel.frame_count % 16)
                pyxel.text(effect["x"] - 10, effect["y"] - 10, "BONUS!", 8)
            else:
                # 通常エフェクト
                pyxel.circb(effect["x"], effect["y"], 5, pyxel.frame_count % 16)

        # 上部のテキスト (スコア、ステージ、タイマー)
        pyxel.text(5, 2, f"Score: {self.score}  Stage: {self.stage}  Time: {self.timer // 30}s", TEXT_COLOR_SCORE)

        # 下部のテキスト (パワーアップとブレーキの使用状況)
        power_up_text = "Power-Up: Used" if self.power_up_used else "Power-Up: Ready"
        power_up_color = TEXT_COLOR_USED if self.power_up_used else TEXT_COLOR_READY
        brake_text = "Brake: Used" if self.brake_used else "Brake: Ready"
        brake_color = TEXT_COLOR_USED if self.brake_used else TEXT_COLOR_READY
        pyxel.text(5, SCREEN_HEIGHT - 8, f"{power_up_text}", power_up_color)
        pyxel.text(80, SCREEN_HEIGHT - 8, f"{brake_text}", brake_color)

    def draw_score(self):
        pyxel.cls(0)
        pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 - 20, "GAME OVER", TITLE_TEXT_COLOR)
        pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2, f"Final Score: {self.score}", TEXT_COLOR_SCORE)
        pyxel.text(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 20, "PRESS Q OR B TO RETURN TO TITLE", QUIT_TEXT_COLOR)

App()