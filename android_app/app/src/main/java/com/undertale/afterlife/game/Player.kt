package com.undertale.afterlife.game

import android.content.res.AssetManager
import android.graphics.RectF
import com.undertale.afterlife.render.SpriteBatch
import com.undertale.afterlife.render.Texture
import kotlin.math.abs

class Player(private val assetManager: AssetManager) {

    companion object {
        const val PLAYER_WIDTH = 40f
        const val PLAYER_HEIGHT = 60f
        const val INITIAL_X = 862f
        const val INITIAL_Y = 561f
        const val SPEED = 25f
        const val FRAME_DURATION = 80L
    }

    val rect = RectF(INITIAL_X, INITIAL_Y, INITIAL_X + PLAYER_WIDTH, INITIAL_Y + PLAYER_HEIGHT)
    var direction: String = "down"
        private set

    var level: Int = 1
    var health: Int = 20
    var maxHealth: Int = 20
    var attack: Int = 10
    var defense: Int = 10
    var gold: Int = 0
    val items: MutableList<String> = mutableListOf()
    val equipment: MutableMap<String, String> = mutableMapOf()

    private var animationTime: Long = 0L
    private var animationIndex: Int = 0

    private val sequences: Map<String, List<String>> = mapOf(
        "down" to listOf("stand_down", "walk_down_r", "stand_down", "walk_down_l"),
        "up" to listOf("stand_up", "walk_up_r", "stand_up", "walk_up_l"),
        "left" to listOf("stand_left", "walk_left", "stand_left", "walk_left"),
        "right" to listOf("stand_right", "walk_right", "stand_right", "walk_right")
    )

    private val assetPaths: Map<String, String> = mapOf(
        "stand_down" to "images/frisk_stand.png",
        "walk_down_r" to "images/frisk_foot_right_up.png",
        "walk_down_l" to "images/frisk_foot_left_up.png",
        "stand_up" to "images/frisk_back_stand.png",
        "walk_up_r" to "images/frisk_back_foot_right_up.png",
        "walk_up_l" to "images/frisk_back_foot_left_up.png",
        "stand_left" to "images/frisk_stand_left.png",
        "walk_left" to "images/frisk_walk_left.png",
        "stand_right" to "images/frisk_stand_right.png",
        "walk_right" to "images/frisk_walk_right.png"
    )

    private val textureCache: MutableMap<String, Texture> = mutableMapOf()

    private fun getFrameTexture(frameKey: String): Texture {
        textureCache[frameKey]?.let { return it }
        val path = assetPaths[frameKey] ?: throw RuntimeException("Unknown frame: $frameKey")
        val tex = Texture()
        tex.load(assetManager, path)
        textureCache[frameKey] = tex
        return tex
    }

    fun update(dx: Float, dy: Float, currentTimeMs: Long) {
        val isMoving = abs(dx) > 0.1f || abs(dy) > 0.1f

        if (isMoving) {
            if (abs(dx) > abs(dy)) {
                direction = if (dx > 0) "right" else "left"
            } else {
                direction = if (dy > 0) "down" else "up"
            }

            val cx = rect.centerX()
            val cy = rect.centerY()
            val newX = rect.left + dx * SPEED
            val newY = rect.top + dy * SPEED
            val newCx = newX + PLAYER_WIDTH / 2f
            val newCy = newY + PLAYER_HEIGHT / 2f

            if (MapBoundary.isPointInside(newCx, cy)) {
                rect.offsetTo(newX, rect.top)
            }
            if (MapBoundary.isPointInside(cx, newCy)) {
                rect.offsetTo(rect.left, newY)
            }

            if (currentTimeMs - animationTime > FRAME_DURATION) {
                animationTime = currentTimeMs
                val seqLen = (sequences[direction]?.size ?: 4)
                animationIndex = (animationIndex + 1) % seqLen
            }
        } else {
            animationIndex = 0
        }
    }

    fun draw(batch: SpriteBatch) {
        val seq = sequences[direction] ?: return
        val frameKey = seq[animationIndex]
        val tex = getFrameTexture(frameKey)

        val drawX = rect.left
        val drawY = rect.bottom - tex.height
        batch.draw(tex, drawX, drawY)
    }

    fun loadFromSave(posX: Float, posY: Float, dir: String) {
        rect.offsetTo(posX, posY)
        direction = dir
    }

    fun dispose() {
        textureCache.values.forEach { it.dispose() }
        textureCache.clear()
    }
}
