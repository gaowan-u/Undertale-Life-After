package com.undertale.afterlife.scene

import android.graphics.RectF
import com.undertale.afterlife.menu.GameColors
import com.undertale.afterlife.menu.HeartCursor
import com.undertale.afterlife.menu.TextRenderer
import com.undertale.afterlife.render.SpriteBatch
import com.undertale.afterlife.render.Texture

open class MainMenu(
    protected val textRenderer: TextRenderer,
    protected val menuItems: MutableList<String> = mutableListOf("开始游戏", "加载游戏", "设置", "退出"),
    protected val title: String = "主菜单"
) {
    companion object {
        protected const val SCREEN_W = 1920f
        protected const val SCREEN_H = 1080f
        private const val TITLE_SIZE = 72f
        private const val ITEM_SIZE = 48f
        private const val ITEM_SPACING = 80f
        private const val HEART_OFFSET_X = 60f
    }

    var selectedIndex: Int = -1
        protected set

    protected val overlayTexture: Texture by lazy {
        Texture.createSolidColorARGB(GameColors.OVERLAY)
    }

    val heartCursor = HeartCursor()

    private var itemSurfaces: List<Texture>? = null
    private var itemSelectedSurfaces: List<Texture>? = null
    protected var itemRects: List<RectF> = emptyList()

    private var heartTime: Long = 0L

    protected fun invalidateItemSurfaces() {
        itemSurfaces = null
        itemSelectedSurfaces = null
        itemRects = emptyList()
    }

    private fun ensureItemSurfaces() {
        if (itemSurfaces == null) {
            itemSurfaces = menuItems.map {
                textRenderer.getTextTexture(it, ITEM_SIZE, GameColors.WHITE)
            }
        }
        if (itemSelectedSurfaces == null) {
            itemSelectedSurfaces = menuItems.map {
                textRenderer.getTextTexture(it, ITEM_SIZE, GameColors.YELLOW)
            }
        }
        if (itemRects.isEmpty()) {
            itemRects = menuItems.mapIndexed { index, item ->
                val (w, h) = textRenderer.getTextDimensions(item, ITEM_SIZE)
                RectF(
                    (SCREEN_W - w) / 2f,
                    SCREEN_H / 2f + index * ITEM_SPACING,
                    (SCREEN_W - w) / 2f + w,
                    SCREEN_H / 2f + index * ITEM_SPACING + h
                )
            }
        }
    }

    open fun handleInput(
        deltaTime: Float = 0f,
        navUp: Boolean = false,
        navDown: Boolean = false,
        select: Boolean = false,
        back: Boolean = false,
        mouseX: Float = 0f,
        mouseY: Float = 0f,
        mouseClicked: Boolean = false
    ): String? {
        ensureItemSurfaces()

        val n = menuItems.size
        if (n == 0) return null

        if (navUp) {
            selectedIndex = if (selectedIndex == -1) n - 1
            else (selectedIndex - 1 + n) % n
        } else if (navDown) {
            selectedIndex = if (selectedIndex == -1) 0
            else (selectedIndex + 1) % n
        }

        for ((i, rect) in itemRects.withIndex()) {
            if (rect.contains(mouseX, mouseY)) {
                selectedIndex = i
                break
            }
        }

        if (select && selectedIndex != -1) return handleSelection()
        if (mouseClicked && selectedIndex != -1) return handleSelection()

        return null
    }

    protected open fun handleSelection(): String? = when (selectedIndex) {
        0 -> "start_game"
        1 -> "load_game"
        2 -> "open_settings"
        3 -> "exit"
        else -> null
    }

    open fun draw(batch: SpriteBatch) {
        heartTime += 16L
        ensureItemSurfaces()

        batch.draw(overlayTexture, 0f, 0f, SCREEN_W, SCREEN_H)

        val titleTex = textRenderer.getTextTexture(title, TITLE_SIZE, GameColors.WHITE)
        val (tw, th) = textRenderer.getTextDimensions(title, TITLE_SIZE)
        batch.draw(titleTex, (SCREEN_W - tw) / 2f, SCREEN_H / 4f - th / 2f)

        val surfaces = itemSurfaces!!
        val selSurfaces = itemSelectedSurfaces!!

        for (i in menuItems.indices) {
            val surf = if (i == selectedIndex) selSurfaces[i] else surfaces[i]
            val rect = itemRects[i]
            batch.draw(surf, rect.left, rect.top)

            if (i == selectedIndex) {
                val breathingOffset = HeartCursor.breathingOffset(heartTime)
                val heartX = rect.left - HEART_OFFSET_X + breathingOffset
                val heartY = rect.centerY() - heartCursor.texture.height / 2f
                batch.draw(heartCursor.texture, heartX, heartY)
            }
        }
    }

    open fun dispose() {
        textRenderer.dispose()
    }
}
