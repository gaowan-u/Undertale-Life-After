package com.undertale.afterlife.scene

import android.graphics.RectF
import com.undertale.afterlife.menu.GameColors
import com.undertale.afterlife.menu.HeartCursor
import com.undertale.afterlife.menu.TextRenderer
import com.undertale.afterlife.render.SpriteBatch
import com.undertale.afterlife.render.Texture

class SettingsMenu(
    textRenderer: TextRenderer,
    private var touchUiVisible: Boolean = true
) : MainMenu(
    textRenderer,
    menuItems = mutableListOf("音量", "画质", "触控UI: 开", "返回"),
    title = "设置"
) {

    private val TOUCH_UI_INDEX = 2
    private var lastTouchUiState: Boolean? = null

    private var showConfirm: Boolean = false
    private var confirmSelected: String? = null

    private val dialogWidth = 560f
    private val dialogHeight = 240f
    private val dialogX = (1920f - dialogWidth) / 2f
    private val dialogY = (1080f - dialogHeight) / 2f

    private val btnWidth = 140f
    private val btnHeight = 45f
    private val btnGap = 60f
    private val btnStartX = dialogX + (dialogWidth - btnWidth * 2f - btnGap) / 2f
    private val btnY = dialogY + dialogHeight - btnHeight - 30f

    private val yesRect = RectF(btnStartX, btnY, btnStartX + btnWidth, btnY + btnHeight)
    private val noRect = RectF(btnStartX + btnWidth + btnGap, btnY, btnStartX + btnWidth * 2f + btnGap, btnY + btnHeight)

    private val texOverlay: Texture by lazy {
        Texture.createSolidColorARGB(0xB4000000.toInt())
    }
    private val texDialogBg: Texture by lazy { createRectTexture(dialogWidth, dialogHeight) }

    private var mouseX: Float = 0f
    private var mouseY: Float = 0f

    fun setTouchUiVisible(visible: Boolean) {
        touchUiVisible = visible
        lastTouchUiState = null
    }

    fun handleInput(
        navUp: Boolean, navDown: Boolean, select: Boolean, back: Boolean,
        mx: Float, my: Float, mouseClicked: Boolean
    ): String? {
        mouseX = mx
        mouseY = my

        if (showConfirm) {
            return handleConfirmInput(navUp, navDown, select, back, mouseClicked)
        }

        if (back) return "back"

        return super.handleInput(0f, navUp, navDown, select, back, mx, my, mouseClicked)
    }

    private fun handleConfirmInput(
        navUp: Boolean, navDown: Boolean, select: Boolean, back: Boolean, mouseClicked: Boolean
    ): String? {
        if (back) {
            showConfirm = false; confirmSelected = null; return null
        }

        if (navUp || navDown) {
            confirmSelected = if (confirmSelected == "yes") "no" else "yes"
        }

        if (yesRect.contains(mouseX, mouseY)) confirmSelected = "yes"
        else if (noRect.contains(mouseX, mouseY)) confirmSelected = "no"

        if (select || mouseClicked) {
            when (confirmSelected) {
                "yes" -> { showConfirm = false; confirmSelected = null; return "toggle_touch_ui" }
                "no" -> { showConfirm = false; confirmSelected = null }
            }
        }
        return null
    }

    override fun handleSelection(): String? = when (selectedIndex) {
        0 -> "volume"
        1 -> "quality"
        2 -> {
            if (touchUiVisible) { showConfirm = true; confirmSelected = "no"; null }
            else "toggle_touch_ui"
        }
        3 -> "back"
        else -> null
    }

    override fun draw(batch: SpriteBatch) {
        updateTouchUiText()
        super.draw(batch)
        if (showConfirm) {
            drawConfirmDialog(batch)
        }
    }

    private fun updateTouchUiText() {
        if (touchUiVisible != lastTouchUiState) {
            lastTouchUiState = touchUiVisible
            val stateText = if (touchUiVisible) "开" else "关"
            val newText = "触控UI: $stateText"
            if (menuItems.size > TOUCH_UI_INDEX) {
                menuItems[TOUCH_UI_INDEX] = newText
            }
            lastTouchUiState = touchUiVisible
            invalidateItemSurfaces()
        }
    }

    private fun drawConfirmDialog(batch: SpriteBatch) {
        batch.draw(texOverlay, 0f, 0f, 1920f, 1080f)
        batch.draw(texDialogBg, dialogX, dialogY)

        drawText(batch, "提示", 24f, GameColors.YELLOW,
            dialogX + (dialogWidth - getTextW("提示", 24f)) / 2f, dialogY + 25f)

        drawText(batch, "关闭触控UI后，屏幕按钮将消失，", 24f, GameColors.WHITE,
            dialogX + (dialogWidth - getTextW("关闭触控UI后，屏幕按钮将消失，", 24f)) / 2f, dialogY + 75f)

        drawText(batch, "只能使用键盘操作。确定要继续吗？", 24f, GameColors.WHITE,
            dialogX + (dialogWidth - getTextW("只能使用键盘操作。确定要继续吗？", 24f)) / 2f, dialogY + 105f)

        val yesHover = yesRect.contains(mouseX, mouseY) || confirmSelected == "yes"
        val noHover = noRect.contains(mouseX, mouseY) || confirmSelected == "no"

        drawBtn(batch, yesRect.left, yesRect.top, "确定", yesHover)
        drawBtn(batch, noRect.left, noRect.top, "取消", noHover)
    }

    private fun drawText(batch: SpriteBatch, text: String, size: Float, color: Int, x: Float, y: Float) {
        val tex = textRenderer.getTextTexture(text, size, color)
        batch.draw(tex, x, y)
    }

    private fun getTextW(text: String, size: Float): Float = textRenderer.getTextDimensions(text, size).first

    private fun drawBtn(batch: SpriteBatch, x: Float, y: Float, text: String, hover: Boolean) {
        val bgColor = if (hover) 0xFF464646.toInt() else 0xFF323232.toInt()
        val borderColor = if (hover) GameColors.YELLOW else 0xFF646464.toInt()
        val btnTex = createBtnTexture(text, bgColor, borderColor)
        batch.draw(btnTex, x, y)
    }

    private val btnTextureCache: MutableMap<String, Texture> = mutableMapOf()

    private fun createBtnTexture(text: String, bgColor: Int, borderColor: Int): Texture {
        val key = "$text|$bgColor|$borderColor"
        btnTextureCache[key]?.let { return it }

        val bmp = android.graphics.Bitmap.createBitmap(
            btnWidth.toInt(), btnHeight.toInt(), android.graphics.Bitmap.Config.ARGB_8888)
        val canvas = android.graphics.Canvas(bmp)
        val paint = android.graphics.Paint().apply { isAntiAlias = true }

        paint.color = bgColor; paint.style = android.graphics.Paint.Style.FILL
        canvas.drawRoundRect(0f, 0f, btnWidth, btnHeight, 8f, 8f, paint)

        paint.color = borderColor; paint.style = android.graphics.Paint.Style.STROKE; paint.strokeWidth = 2f
        canvas.drawRoundRect(0f, 0f, btnWidth, btnHeight, 8f, 8f, paint)

        val tex = textRenderer.getTextTexture(text, 24f, GameColors.WHITE)
        val (tw, th) = textRenderer.getTextDimensions(text, 24f)
        val tx = (btnWidth - tw) / 2f
        val ty = (btnHeight - th) / 2f
        val bmpTex = android.graphics.Bitmap.createBitmap(tex.width, tex.height, android.graphics.Bitmap.Config.ARGB_8888)
        val copyCanvas = android.graphics.Canvas(bmpTex)
        // Can't easily copy GL texture to bitmap, so draw text directly with same paint
        paint.color = GameColors.WHITE; paint.style = android.graphics.Paint.Style.FILL; paint.textSize = 24f
        paint.typeface = android.graphics.Typeface.DEFAULT
        canvas.drawText(text, tx, ty + th, paint)

        val result = Texture()
        result.loadFromBitmap(bmp)
        bmp.recycle()
        btnTextureCache[key] = result
        return result
    }

    private fun createRectTexture(w: Float, h: Float): Texture {
        val bmp = android.graphics.Bitmap.createBitmap(w.toInt(), h.toInt(), android.graphics.Bitmap.Config.ARGB_8888)
        val canvas = android.graphics.Canvas(bmp)
        val paint = android.graphics.Paint().apply { isAntiAlias = true }

        paint.color = 0xFF1E1E1E.toInt(); paint.style = android.graphics.Paint.Style.FILL
        canvas.drawRoundRect(0f, 0f, w, h, 12f, 12f, paint)

        paint.color = GameColors.BORDER; paint.style = android.graphics.Paint.Style.STROKE; paint.strokeWidth = 2f
        canvas.drawRoundRect(0f, 0f, w, h, 12f, 12f, paint)

        val result = Texture()
        result.loadFromBitmap(bmp)
        bmp.recycle()
        return result
    }

    override fun dispose() {
        super.dispose()
        btnTextureCache.values.forEach { it.dispose() }
        btnTextureCache.clear()
    }
}
