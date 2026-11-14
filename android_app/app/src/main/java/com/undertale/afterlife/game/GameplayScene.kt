package com.undertale.afterlife.game

import android.content.res.AssetManager
import android.graphics.RectF
import com.undertale.afterlife.input.InputManager
import com.undertale.afterlife.menu.GameColors
import com.undertale.afterlife.menu.TextRenderer
import com.undertale.afterlife.render.SpriteBatch
import com.undertale.afterlife.render.Texture
import com.undertale.afterlife.save.SaveData
import com.undertale.afterlife.save.SaveSystem

class GameplayScene(
    private val assetManager: AssetManager,
    private val inputManager: InputManager,
    private val textRenderer: TextRenderer,
    private val saveSystem: SaveSystem
) {
    companion object {
        private const val EXIT_ZONE_X = 1900f
        private const val EXIT_ZONE_Y_MIN = 676f
        private const val EXIT_ZONE_Y_MAX = 839f
        private const val SCREEN_W = 1920f
        private const val SCREEN_H = 1080f
    }

    val player = Player(assetManager)
    var paused: Boolean = false
        private set
    var touchUiVisible: Boolean = true

    private var pauseSelectedIndex: Int = -1
    private val pauseOptions = listOf("继续", "保存游戏", "保存并返回主菜单")

    private var accumulatedPlayTime: Double = 0.0
    private var lastFrameTime: Long = 0L
    private var heartTime: Long = 0L

    private val backgroundTexture: Texture by lazy {
        val tex = Texture()
        tex.load(assetManager, "images/spawn.png")
        tex
    }

    private val pauseOverlay: Texture by lazy {
        Texture.createSolidColor(0, 0, 0, 160)
    }

    private val exitZoneRect = RectF(EXIT_ZONE_X, EXIT_ZONE_Y_MIN, SCREEN_W, EXIT_ZONE_Y_MAX)

    fun loadFromSave(save: SaveData) {
        player.loadFromSave(save.position.x, save.position.y, save.position.direction)
        player.level = save.player.level
        player.health = save.player.health
        player.maxHealth = save.player.maxHealth
        player.attack = save.player.attack
        player.defense = save.player.defense
        player.gold = save.player.gold
        player.items.clear()
        player.items.addAll(save.player.items)
        player.equipment.clear()
        player.equipment.putAll(save.player.equipment)
        accumulatedPlayTime = save.metadata.playTime
    }

    fun update(deltaTime: Float, backPressed: Boolean): String? {
        val now = System.nanoTime() / 1_000_000L
        if (lastFrameTime == 0L) lastFrameTime = now
        accumulatedPlayTime += (now - lastFrameTime) / 1000.0
        lastFrameTime = now

        if (backPressed && !paused) {
            paused = true
            pauseSelectedIndex = -1
            return null
        }

        if (paused) {
            return handlePauseMenu()
        }

        inputManager.resetFrameStates()
        inputManager.updateHold()

        val dirX = inputManager.getDirectionX()
        val dirY = inputManager.getDirectionY()

        player.update(dirX, dirY, now)

        if (player.rect.left >= EXIT_ZONE_X &&
            player.rect.centerY() in EXIT_ZONE_Y_MIN..EXIT_ZONE_Y_MAX) {
            return "exit"
        }

        return null
    }

    private fun handlePauseMenu(): String? {
        val n = pauseOptions.size

        if (inputManager.keysPressed.contains(android.view.KeyEvent.KEYCODE_DPAD_UP) ||
            inputManager.keysPressed.contains(android.view.KeyEvent.KEYCODE_W)) {
            pauseSelectedIndex = if (pauseSelectedIndex == -1) n - 1
            else (pauseSelectedIndex - 1 + n) % n
        }

        val result = when (pauseSelectedIndex) {
            0 -> { paused = false; null }
            1 -> {
                saveGame()
                null
            }
            2 -> {
                saveGame()
                "back_to_menu"
            }
            else -> null
        }

        return result
    }

    private fun saveGame() {
        saveSystem.saveGame(
            mapOf(
                "playTime" to accumulatedPlayTime,
                "playerPosition" to mapOf(
                    "x" to player.rect.left,
                    "y" to player.rect.top,
                    "direction" to player.direction
                ),
                "playerStats" to mapOf(
                    "level" to player.level,
                    "health" to player.health,
                    "maxHealth" to player.maxHealth,
                    "attack" to player.attack,
                    "defense" to player.defense,
                    "gold" to player.gold,
                    "items" to player.items,
                    "equipment" to player.equipment
                )
            )
        )
        accumulatedPlayTime = 0.0
    }

    fun draw(batch: SpriteBatch) {
        heartTime += 16L
        batch.draw(backgroundTexture, 0f, 0f)

        player.draw(batch)

        if (paused) {
            drawPauseMenu(batch)
        }
    }

    private fun drawPauseMenu(batch: SpriteBatch) {
        batch.draw(pauseOverlay, 0f, 0f, SCREEN_W, SCREEN_H)

        val titleTex = textRenderer.getTextTexture("暂停", 72f, GameColors.WHITE)
        val (tw, th) = textRenderer.getTextDimensions("暂停", 72f)
        batch.draw(titleTex, (SCREEN_W - tw) / 2f, SCREEN_H / 4f - th / 2f)

        for (i in pauseOptions.indices) {
            val color = if (i == pauseSelectedIndex) GameColors.YELLOW else GameColors.WHITE
            val tex = textRenderer.getTextTexture(pauseOptions[i], 48f, color)
            val (iw, ih) = textRenderer.getTextDimensions(pauseOptions[i], 48f)
            val ix = (SCREEN_W - iw) / 2f
            val iy = SCREEN_H / 2f + i * 80f
            batch.draw(tex, ix, iy)
        }
    }

    fun dispose() {
        player.dispose()
    }
}
