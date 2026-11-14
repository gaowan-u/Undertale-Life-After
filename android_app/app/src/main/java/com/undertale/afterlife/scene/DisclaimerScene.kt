package com.undertale.afterlife.scene

import com.undertale.afterlife.menu.GameColors
import com.undertale.afterlife.menu.TextRenderer
import com.undertale.afterlife.render.SpriteBatch
import com.undertale.afterlife.render.Texture
import kotlin.math.sin

class DisclaimerScene(private val textRenderer: TextRenderer) {

    private val phaseTotalTime = 5.0f
    private var elapsed: Float = 0f
    private var done: Boolean = false

    private val lines = listOf(
        "本作品为粉丝创作，非官方授权产品",
        "Undertale™ 是Toby Fox的注册商标",
        "与Undertale开发团队无任何关联",
        "角色版权归原著作权方所有",
        "美术资源遵循CC BY-NC 4.0协议"
    )

    private val bgOverlay: Texture by lazy {
        Texture.createSolidColor(0, 0, 0, 255)
    }

    fun update(deltaTime: Float, skip: Boolean): Boolean {
        if (skip) {
            done = true
            return true
        }
        elapsed += deltaTime
        if (elapsed > phaseTotalTime) {
            done = true
            return true
        }
        return false
    }

    fun draw(batch: SpriteBatch) {
        batch.draw(bgOverlay, 0f, 0f, 1920f, 1080f)

        val progress = (elapsed / phaseTotalTime).coerceIn(0f, 1f)

        var alpha = 1f
        if (progress < 0.2f) {
            alpha = progress / 0.2f
        } else if (progress > 0.8f) {
            alpha = 1f - (progress - 0.8f) / 0.2f
        }

        val bounce = sin(progress * 3.14f * 2f) * 10f

        for ((i, line) in lines.withIndex()) {
            val tex = textRenderer.getTextTexture(line, 36f, GameColors.WHITE)
            val (tw, _) = textRenderer.getTextDimensions(line, 36f)
            val baseY = 1080f / 2f + i * 50f - 60f
            val y = baseY + bounce * (1f - progress) + progress * 100f
            batch.draw(tex, (1920f - tw) / 2f, y, alpha = alpha)
        }
    }

    fun isDone(): Boolean = done

    fun dispose() {}
}
